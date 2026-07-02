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
    """Closed horizontal roof polygon at ``z_base`` (metres).

    The building footprint is expanded by ``overhang_m`` on every side so the
    roof edge (eaves) sits beyond the outer walls. A flat roof has zero pitch,
    so every point shares the same Z (``z_base``).
    """
    o = overhang_m
    return [
        (-o, -o, z_base),
        (width_m + o, -o, z_base),
        (width_m + o, depth_m + o, z_base),
        (-o, depth_m + o, z_base),
        (-o, -o, z_base),
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

      * ``Z_eaves = z_base - overhang * tan(theta)``  (low overhang edge)
      * ``Z_ridge = z_base + width_m * tan(theta)``   (high ridge edge, run = W)

    The footprint overhangs by ``overhang_m`` on the low (eaves) side and on
    both depth (Y) ends; the high ridge edge sits at the high wall (``X =
    width_m``) so the ridge height matches ``run_ridge = W`` and the plane
    keeps a constant ``tan(theta)`` slope. Points trace the rectangle clockwise
    from the low-front corner.
    """
    rise = math.tan(math.radians(pitch_deg))
    z_eaves = z_base - overhang_m * rise
    z_ridge = z_base + width_m * rise
    o = overhang_m
    return [
        (-o, -o, z_eaves),
        (width_m, -o, z_ridge),
        (width_m, depth_m + o, z_ridge),
        (-o, depth_m + o, z_eaves),
        (-o, -o, z_eaves),
    ]


def roof_surface_polygons(
    roof_key: str,
    width_m: float,
    depth_m: float,
    pitch_deg: float,
    overhang_m: float,
) -> list[list[Point3]]:
    """Return the closed roof surface polygons (metres) for a roof type.

    Dispatches to the per-type geometry routine. ``flat`` and ``mono-pitch``
    are supported; ``gable`` and ``hip`` are added by later tasks. ``pitch_deg``
    is unused for a flat roof but kept in the signature so every roof type
    shares one entry point.
    """
    key = (roof_key or "flat").strip().lower()
    if key == "flat":
        return [flat_roof_surface_polygon(width_m, depth_m, overhang_m)]
    if key == "mono-pitch":
        return [monopitch_roof_surface_polygon(width_m, depth_m, pitch_deg, overhang_m)]
    raise ValueError(
        f"MXF roof surface generation not implemented for roofType: {roof_key!r}"
    )
