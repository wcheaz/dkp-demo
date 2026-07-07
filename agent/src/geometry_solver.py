"""Shared geometry calculations for DXF and IFC builders.

All coordinates and dimensions are expressed in millimetres unless a function
documents otherwise. This module intentionally has no CAD-library dependency so
that both :mod:`dxf_builder` and :mod:`ifc_builder` can reuse the same layout
math without pulling in ``ezdxf`` or ``ifcopenshell``.
"""

import math
import re

WALL_HEIGHT = 2700.0

VALID_ROOF_TYPES = {"gable", "hip", "mono-pitch", "flat"}

_DIMENSION_RE = re.compile(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?")

# Matches a numeric overhang with an optional ``mm`` or ``m`` unit suffix.
_OVERHANG_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(mm|m)?\s*$", re.IGNORECASE)


def parse_dimensions(raw: str | None) -> tuple[float, float]:
    """Parse a ``WxDm`` floor-plan string into ``(width_mm, depth_mm)``."""
    if raw is None:
        raise ValueError("floorPlanDimensions is required")
    match = _DIMENSION_RE.match(raw.strip())
    if not match:
        raise ValueError(f"Cannot parse floorPlanDimensions: {raw!r}")
    width_mm = float(match.group(1)) * 1000
    depth_mm = float(match.group(2)) * 1000
    return width_mm, depth_mm


def parse_overhang(raw: str | int | float | None) -> float | None:
    """Parse an overhang value into millimetres.

    Accepts raw numbers (``int``/``float``) and strings carrying an optional
    ``mm`` or ``m`` unit suffix, e.g. ``250``, ``"250mm"``, ``"0.5m"``. Plain
    numbers and ``mm`` suffixes are returned verbatim; ``m`` values are
    converted to millimetres. Returns ``None`` when ``raw`` is ``None`` or the
    string cannot be parsed, so callers can fall back to a default overhang.
    """
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    match = _OVERHANG_RE.match(str(raw).strip())
    if not match:
        return None
    value = float(match.group(1))
    unit = (match.group(2) or "").lower()
    if unit == "m":
        return value * 1000.0
    return value


def wall_corners(width_mm: float, depth_mm: float) -> list[tuple[float, float]]:
    """Return the four wall-centreline corners in XY, clockwise from origin."""
    return [
        (0.0, 0.0),
        (width_mm, 0.0),
        (width_mm, depth_mm),
        (0.0, depth_mm),
    ]


def resolve_pitch(roof_key: str, roof_pitch: float | None) -> float:
    """Resolve the effective roof pitch in degrees for a roof type.

    When no explicit pitch is supplied (or it is zero) a sensible default is
    chosen per roof type so DXF and IFC outputs always agree.
    """
    if roof_pitch is None or roof_pitch == 0:
        if roof_key in ("gable", "hip"):
            return 30.0
        if roof_key == "mono-pitch":
            return 10.0
        return 0.0
    return float(roof_pitch)


def truss_ridge_height(width_mm: float, roof_key: str, pitch_deg: float) -> float:
    """Rise of the truss ridge above the wall top plate (mm)."""
    if roof_key in ("gable", "hip"):
        return (width_mm / 2) * math.tan(pitch_deg * math.pi / 180)
    if roof_key == "mono-pitch":
        return width_mm * math.tan(pitch_deg * math.pi / 180)
    return 0.0


def compute_truss_count(width_m: float, depth_m: float) -> int:
    """Heuristic truss count scaled by the plan area, never fewer than two."""
    return max(2, round(width_m * depth_m * 0.147))


def truss_positions(width_mm: float, depth_mm: float, count: int) -> list[float]:
    """Y coordinates (mm) of each truss spaced along the depth axis."""
    shorter = min(width_mm, depth_mm)
    inset = shorter * 0.05
    if count == 1:
        return [depth_mm / 2]
    span = depth_mm - 2 * inset
    step = span / (count - 1)
    return [inset + i * step for i in range(count)]


# ---------------------------------------------------------------------------
# Unified structural truss solver
# ---------------------------------------------------------------------------
# The :class:`GeometrySolver` class consolidates all chord, web, joint, and
# support-node coordinate calculations shared by :mod:`ifc_builder`,
# :mod:`mxf_builder`, and :mod:`dxf_builder`. Each builder delegates to a
# single instance so the 3D IFC, MXF, and 2D CAD outputs stay geometrically
# congruent without duplicating the per-roof-type segment logic.
#
# All inputs and outputs are expressed in **millimetres** to match the
# existing DXF/IFC helpers above. The MXF-only metre helpers that follow this
# section are intentionally left as standalone functions because the MXF
# layout uses a different unit convention.

# Functional roles written to ``IfcMember.ObjectType`` (and mirrored on the
# structural segment metadata) so BIM viewers and estimating tools such as
# MiTek Pamir can classify timber members.
ROLE_TOP_CHORD = "TOP_CHORD"
ROLE_BOTTOM_CHORD = "BOTTOM_CHORD"
ROLE_WEB = "WEB"
ROLE_PLATE = "PLATE"

# A segment is a ``(start, end, role)`` triple of millimetre coordinates
# describing a single structural member. A bearing is a ``(location, index)``
# pair marking a wall-plate support point on a truss.
Segment = tuple[
    tuple[float, float, float], tuple[float, float, float], str
]
Bearing = tuple[tuple[float, float, float], int]


class GeometrySolver:
    """Unified structural truss geometry solver (millimetres).

    Consolidates the chord, web, joint, and support-node coordinate
    calculations shared by :mod:`ifc_builder` and :mod:`mxf_builder` so both
    builders emit geometrically congruent structural layouts.

    The solver derives the truss count, ridge height, and per-truss segments
    from the shared module-level helpers (``compute_truss_count``,
    ``truss_positions``, ``truss_ridge_height`` ...) so callers do not need to
    invoke them directly. Each :meth:`member_segments` entry corresponds to
    one truss position (one ``IfcElementAssembly`` / MXF ``Frame``); each
    inner segment is paired with a functional role string so the builder can
    stamp the role on the emitted element without re-deriving the geometry.

    Args:
        width_mm: Building width in millimetres (the truss span axis).
        depth_mm: Building depth in millimetres (the truss layout axis).
        roof_key: Roof-type key (``"gable"``, ``"hip"``, ``"mono-pitch"``,
            or ``"flat"``).
        roof_pitch: Optional explicit roof pitch in degrees. When ``None``
            (or zero) the per-type default from :func:`resolve_pitch` is used.

    Attributes:
        width_mm, depth_mm, roof_key, roof_pitch: Echo the constructor args.
        pitch_deg: Resolved effective pitch in degrees.
        count: Number of trusses along the depth axis.
        positions: Y coordinates (mm) of each truss position.
        ridge_height: Rise of the truss ridge above the wall top plate (mm).
    """

    def __init__(
        self,
        width_mm: float,
        depth_mm: float,
        roof_key: str,
        roof_pitch: float | None = None,
    ) -> None:
        self.width_mm = width_mm
        self.depth_mm = depth_mm
        self.roof_key = roof_key
        self.roof_pitch = roof_pitch
        self.pitch_deg = resolve_pitch(roof_key, roof_pitch)
        self.count = compute_truss_count(width_mm / 1000.0, depth_mm / 1000.0)
        self.positions = truss_positions(width_mm, depth_mm, self.count)
        self.ridge_height = truss_ridge_height(width_mm, roof_key, self.pitch_deg)

    @property
    def z_eave(self) -> float:
        """Z coordinate (mm) of the wall top plate / eaves baseline."""
        return WALL_HEIGHT

    @property
    def z_ridge(self) -> float:
        """Z coordinate (mm) of the truss ridge."""
        return WALL_HEIGHT + self.ridge_height

    def member_segments(self) -> list[list[Segment]]:
        """Return the per-truss chord / web / plate segments (millimetres).

        The outer list contains one entry per truss position (i.e. one
        ``IfcElementAssembly`` / MXF ``Frame``); each inner list holds the
        ``(start, end, role)`` segments that make up that single truss frame.

        Segment roles follow the canonical strings exposed at module scope:

        - :data:`ROLE_TOP_CHORD` — sloping rafter running from eave up to the
          ridge (gable / hip have two, mono-pitch has one).
        - :data:`ROLE_BOTTOM_CHORD` — horizontal ceiling joist tying the
          eaves together (gable / hip / mono-pitch).
        - :data:`ROLE_WEB` — vertical/inclined strut (e.g. the high-side
          post of a mono-pitch truss) that transfers load between chords.
        - :data:`ROLE_PLATE` — the single horizontal member of a flat-roof
          assembly.
        """
        z_eave = self.z_eave
        z_ridge = self.z_ridge
        w = self.width_mm

        trusses: list[list[Segment]] = []
        for y in self.positions:
            segments: list[Segment] = []
            if self.roof_key in ("gable", "hip"):
                segments.append(
                    ((0.0, y, z_eave), (w / 2.0, y, z_ridge), ROLE_TOP_CHORD)
                )
                segments.append(
                    ((w, y, z_eave), (w / 2.0, y, z_ridge), ROLE_TOP_CHORD)
                )
                segments.append(
                    ((0.0, y, z_eave), (w, y, z_eave), ROLE_BOTTOM_CHORD)
                )
            elif self.roof_key == "mono-pitch":
                segments.append(
                    ((0.0, y, z_eave), (w, y, z_ridge), ROLE_TOP_CHORD)
                )
                segments.append(
                    ((0.0, y, z_eave), (w, y, z_eave), ROLE_BOTTOM_CHORD)
                )
                segments.append(((w, y, z_eave), (w, y, z_ridge), ROLE_WEB))
            else:  # flat roof: single ceiling joist
                segments.append(
                    ((0.0, y, z_eave), (w, y, z_eave), ROLE_PLATE)
                )
            trusses.append(segments)
        return trusses

    def support_bearings(self) -> list[list[Bearing]]:
        """Return per-truss wall-plate support nodes (millimetres).

        Each truss contributes one ``(location, bearing_index)`` pair per wall
        bearing — i.e. the two endpoints of the bottom chord (gable / hip /
        mono-pitch) or the single plate (flat). ``bearing_index`` is 1-based
        so callers can label the support points ``S1`` / ``S2`` to match the
        Pamir reference naming.
        """
        per_truss: list[list[Bearing]] = []
        for truss in self.member_segments():
            bearings: list[Bearing] = []
            for start, end, role in truss:
                if role in (ROLE_BOTTOM_CHORD, ROLE_PLATE):
                    for bearing_index, bearing in enumerate(
                        (start, end), start=1
                    ):
                        bearings.append((bearing, bearing_index))
            per_truss.append(bearings)
        return per_truss


# ---------------------------------------------------------------------------
# MXF roof/floor surface geometry
# ---------------------------------------------------------------------------
# The helpers below compute 3D surface polygons for the Layout MXF (Pamir)
# export. Unlike the millimetre-based DXF/IFC helpers above, these coordinates
# are expressed in **metres** to match the MXF convention. The vertical
# reference is the MXF wall height (3.0 m) plus the wall plate (0.05 m).

# MXF wall geometry in metres (matches the Pamir reference export).
MXF_WALL_HEIGHT = 3.0
MXF_WALL_PLATE_HEIGHT = 0.05
# Vertical position of the eaves / wall top plate baseline in metres.
MXF_ROOF_Z_BASE = MXF_WALL_HEIGHT + MXF_WALL_PLATE_HEIGHT
# Standard vertical eaves offset (rafter end thickness) in metres.
MXF_EAVES_OFFSET = 0.07


Point3 = tuple[float, float, float]


def floor_surface_polygon(width_m: float, depth_m: float) -> list[Point3]:
    """Closed building-footprint polygon at ``Z = 0`` (metres).

    Returns five points (the first repeated to close the loop) tracing the
    rectangle clockwise from the local origin: ``(0,0) -> (W,0) -> (W,D) ->
    (0,D) -> (0,0)``.
    """
    return [
        (0.0, 0.0, 0.0),
        (width_m, 0.0, 0.0),
        (width_m, depth_m, 0.0),
        (0.0, depth_m, 0.0),
        (0.0, 0.0, 0.0),
    ]


def flat_roof_surface_polygon(
    width_m: float, depth_m: float, overhang_m: float, z_base: float = MXF_ROOF_Z_BASE
) -> list[Point3]:
    """Closed horizontal roof polygon at ``z_base + MXF_EAVES_OFFSET`` (metres).

    The building footprint is expanded by ``overhang_m`` on every side so the
    roof edge (eaves) sits beyond the outer walls. A flat roof has zero pitch,
    so every point shares the same Z (``z_base + MXF_EAVES_OFFSET``).
    """
    o = overhang_m
    z_val = z_base + MXF_EAVES_OFFSET
    return [
        (-o, -o, z_val),
        (width_m + o, -o, z_val),
        (width_m + o, depth_m + o, z_val),
        (-o, depth_m + o, z_val),
        (-o, -o, z_val),
    ]


def monopitch_roof_surface_polygon(
    width_m: float,
    depth_m: float,
    pitch_deg: float,
    overhang_m: float,
    z_base: float = MXF_ROOF_Z_BASE,
) -> list[Point3]:
    """Closed single-slope (mono-pitch) roof polygon (metres).

    The roof plane slopes up along the width (X) axis: it rests on the low
    wall plate at ``X = 0`` (``Z = z_base``) and rises to the ridge at
    ``X = width_m``. Following the design formulas:

      * ``Z_eaves = z_base + MXF_EAVES_OFFSET``  (low overhang edge)
      * ``Z_ridge = Z_eaves + (width_m + overhang_m) * tan(theta)``   (high ridge edge, run = W + O)

    The footprint overhangs by ``overhang_m`` on the low (eaves) side and on
    both depth (Y) ends; the high ridge edge sits at the high wall (``X =
    width_m``) so the ridge height matches ``run_ridge = W`` and the plane
    keeps a constant ``tan(theta)`` slope. Points trace the rectangle clockwise
    from the low-front corner.
    """
    rise = math.tan(math.radians(pitch_deg))
    z_eaves = z_base + MXF_EAVES_OFFSET
    z_ridge = z_eaves + (width_m + overhang_m) * rise
    o = overhang_m
    return [
        (-o, -o, z_eaves),
        (width_m, -o, z_ridge),
        (width_m, depth_m + o, z_ridge),
        (-o, depth_m + o, z_eaves),
        (-o, -o, z_eaves),
    ]


def gable_roof_surface_polygons(
    width_m: float,
    depth_m: float,
    pitch_deg: float,
    overhang_m: float,
    z_base: float = MXF_ROOF_Z_BASE,
) -> list[list[Point3]]:
    """Closed two-plane (gable) roof polygons (metres).

    The roof slopes along the shorter plan axis: the ridge sits at the midpoint
    of ``min(W, D)`` and runs along the longer axis. Following the design
    formulas:

      * ``Z_eaves = z_base + MXF_EAVES_OFFSET``
      * ``Z_ridge = Z_eaves + (run_ridge + overhang_m) * tan(theta)``  with ``run_ridge = min(W, D)/2``

    The footprint overhangs by ``overhang_m`` on all sides. Two rectangular
    surfaces are returned (``SR0-0`` on the low-X/Y side, ``SR0-1`` on the high
    side), each closing back to its first point. Points trace the rectangle
    clockwise.
    """
    rise = math.tan(math.radians(pitch_deg))
    run_ridge = min(width_m, depth_m) / 2.0
    z_eaves = z_base + MXF_EAVES_OFFSET
    z_ridge = z_eaves + (run_ridge + overhang_m) * rise
    o = overhang_m

    if width_m <= depth_m:
        # Ridge runs along Y at X = width_m/2; roof slopes along X.
        mid = width_m / 2.0
        plane_low = [
            (-o, -o, z_eaves),
            (mid, -o, z_ridge),
            (mid, depth_m + o, z_ridge),
            (-o, depth_m + o, z_eaves),
            (-o, -o, z_eaves),
        ]
        plane_high = [
            (mid, -o, z_ridge),
            (width_m + o, -o, z_eaves),
            (width_m + o, depth_m + o, z_eaves),
            (mid, depth_m + o, z_ridge),
            (mid, -o, z_ridge),
        ]
        return [plane_low, plane_high]

    # Ridge runs along X at Y = depth_m/2; roof slopes along Y.
    mid = depth_m / 2.0
    plane_low = [
        (-o, -o, z_eaves),
        (width_m + o, -o, z_eaves),
        (width_m + o, mid, z_ridge),
        (-o, mid, z_ridge),
        (-o, -o, z_eaves),
    ]
    plane_high = [
        (-o, mid, z_ridge),
        (width_m + o, mid, z_ridge),
        (width_m + o, depth_m + o, z_eaves),
        (-o, depth_m + o, z_eaves),
        (-o, mid, z_ridge),
    ]
    return [plane_low, plane_high]


def hip_roof_surface_polygons(
    width_m: float,
    depth_m: float,
    pitch_deg: float,
    overhang_m: float,
    z_base: float = MXF_ROOF_Z_BASE,
) -> list[list[Point3]]:
    """Closed four-plane (hip) roof polygons (metres).

    The roof slopes along the shorter plan axis: the ridge sits at the midpoint
    of ``min(W, D)`` (run_ridge = ``min(W, D)/2``) and runs along the longer
    axis, shortened by the shorter side on each end so the four hip planes
    converge at the ridge endpoints. Following the design formulas:

      * ``Z_eaves = z_base + MXF_EAVES_OFFSET``
      * ``Z_ridge = Z_eaves + (run_ridge + overhang_m) * tan(theta)``  with ``run_ridge = min(W, D)/2``

    The footprint overhangs by ``overhang_m`` on all sides. Four surfaces are
    returned in surface-ID order (``SR0-0``..``SR0-3``): two trapezoidal planes
    along the longer axis (low-then-high side of the ridge) and two triangular
    hip-end planes capping the shorter axis (low-then-high side). Each polygon
    closes back to its first point and the points trace clockwise.

    For ``width_m <= depth_m`` the ridge runs along Y at ``X = W/2`` between
    ``Y = W/2`` and ``Y = D - W/2``; for ``depth_m < width_m`` the axes swap.
    """
    rise = math.tan(math.radians(pitch_deg))
    run_ridge = min(width_m, depth_m) / 2.0
    z_eaves = z_base + MXF_EAVES_OFFSET
    z_ridge = z_eaves + (run_ridge + overhang_m) * rise
    o = overhang_m

    if width_m <= depth_m:
        # Ridge runs along Y at X = width_m/2; roof slopes along X.
        mid_x = width_m / 2.0
        # Ridge Y endpoints are inset by W/2 from each depth end (with overhang).
        ridge_front = (mid_x, mid_x, z_ridge)
        ridge_back = (mid_x, depth_m - mid_x, z_ridge)
        sw = (-o, -o, z_eaves)
        se = (width_m + o, -o, z_eaves)
        ne = (width_m + o, depth_m + o, z_eaves)
        nw = (-o, depth_m + o, z_eaves)

        # SR0-0: low-X trapezoid (SW -> front ridge -> back ridge -> NW -> close).
        plane_low = [sw, ridge_front, ridge_back, nw, sw]
        # SR0-1: high-X trapezoid (front ridge -> SE -> NE -> back ridge -> close).
        plane_high = [ridge_front, se, ne, ridge_back, ridge_front]
        # SR0-2: low-Y hip triangle (SW -> SE -> front ridge -> close).
        hip_front = [sw, se, ridge_front, sw]
        # SR0-3: high-Y hip triangle (NE -> NW -> back ridge -> close).
        hip_back = [ne, nw, ridge_back, ne]
        return [plane_low, plane_high, hip_front, hip_back]

    # Ridge runs along X at Y = depth_m/2; roof slopes along Y.
    mid_y = depth_m / 2.0
    # Ridge X endpoints are inset by D/2 from each width end (with overhang).
    ridge_left = (mid_y, mid_y, z_ridge)
    ridge_right = (width_m - mid_y, mid_y, z_ridge)
    sw = (-o, -o, z_eaves)
    se = (width_m + o, -o, z_eaves)
    ne = (width_m + o, depth_m + o, z_eaves)
    nw = (-o, depth_m + o, z_eaves)

    # SR0-0: low-Y trapezoid (SW -> SE -> right ridge -> left ridge -> close).
    plane_low = [sw, se, ridge_right, ridge_left, sw]
    # SR0-1: high-Y trapezoid (left ridge -> right ridge -> NE -> NW -> close).
    plane_high = [ridge_left, ridge_right, ne, nw, ridge_left]
    # SR0-2: low-X hip triangle (SW -> left ridge -> NW -> close).
    hip_left = [sw, ridge_left, nw, sw]
    # SR0-3: high-X hip triangle (SE -> NE -> right ridge -> close).
    hip_right = [se, ne, ridge_right, se]
    return [plane_low, plane_high, hip_left, hip_right]


def roof_surface_polygons(
    roof_key: str,
    width_m: float,
    depth_m: float,
    pitch_deg: float,
    overhang_m: float,
) -> list[list[Point3]]:
    """Return the closed roof surface polygons (metres) for a roof type.

    Dispatches to the per-type geometry routine. ``flat``, ``mono-pitch``,
    ``gable``, and ``hip`` are supported. ``pitch_deg`` is unused for a flat
    roof but kept in the signature so every roof type shares one entry point.
    """
    key = (roof_key or "flat").strip().lower()
    if key == "flat":
        return [flat_roof_surface_polygon(width_m, depth_m, overhang_m)]
    if key == "mono-pitch":
        return [monopitch_roof_surface_polygon(width_m, depth_m, pitch_deg, overhang_m)]
    if key == "gable":
        return gable_roof_surface_polygons(width_m, depth_m, pitch_deg, overhang_m)
    if key == "hip":
        return hip_roof_surface_polygons(width_m, depth_m, pitch_deg, overhang_m)
    raise ValueError(
        f"MXF roof surface generation not implemented for roofType: {roof_key!r}"
    )
