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

# MXF truss frame geometry (metres). An MXF chord member is a
# ``(member_type, start, end)`` triple where ``member_type`` is the Pamir
# ``WoodMember`` type attribute (``"TopChord"`` / ``"BottomChord"``) and
# ``start`` / ``end`` are the ``(x, y)`` endpoints of the chord in the
# frame's LOCAL coordinate system: X runs along the truss span
# (0 = left wall, ``width_mm/1000`` = right wall) and Y is the height above
# the wall-plate / eaves baseline (0 = eaves, rising to the ridge).
MxfChordMember = tuple[str, tuple[float, float], tuple[float, float]]

# One MXF truss frame: the truss Y position along the building depth (m) and
# the ordered list of full-span chord members that compose that single frame.
MxfTrussFrame = tuple[float, list[MxfChordMember]]

# Transport-split thresholds for tall trusses (metres). A truss whose total
# height exceeds the road transport limit is split into a rectangular base
# (Part 1) and a triangular cap (Part 2) joined by horizontal splice chords at
# the split line. Matches the standard transport restriction and the Pamir
# reference multi-part truss pattern (see design.md §"Transport Limit
# Detection and Multi-Part Splicing"). These are fixed engineering constants,
# not configuration knobs.
TRANSPORT_MAX_HEIGHT_M = 3.3    # trigger threshold: split when truss is taller
TRANSPORT_SPLIT_HEIGHT_M = 2.8  # Part 1 (Base) vertical extent

# Gable-end panel stud spacing (metres). The first and last trusses in the
# layout sequence are emitted as ``GableEnd`` family ``roof``-type Frame
# definitions whose vertical studs run from the bottom chord up to the sloping
# top chord at standard 600 mm centres (see design.md §"Outer Gable-End
# Panels"). The ``type="roof"`` matches the Pamir reference export
# (``hidden/Sample_Project/7JULY_Z.mxf``). Fixed engineering constant, not a
# configuration knob.
GABLE_END_STUD_SPACING_M = 0.6

# Sloped bracing constant (metres). Purlins run perpendicular to the truss
# span along the roof slope at standard 1.0 m centres
# (see design.md §"Sloped Bracing System" / spec.md "Roof Slope Bracing").
# Fixed engineering constant, not a configuration knob.
PURLIN_SPACING_M = 1.0

# Functional brace type string written to the ``EngineeredBrace.braceType``
# attribute, matching the Pamir reference export
# (``hidden/Sample_Project/7JULY_Z.mxf``) so MiTek Pamir classifies each
# generated brace correctly on import. Only the ``purlin`` token is emitted:
# every other ``braceType`` value used by the reference
# (``bottomChordRunner``, ``lateralWebBrace``) is gable-plan specific and is
# not generated here.
BRACE_TYPE_PURLIN = "purlin"

# An MXF transport-split truss part: ``(name, z_base, z_top, members)`` where
# ``name`` is the Pamir Part label (``"Part 1"`` base / ``"Part 2"`` cap),
# ``z_base`` / ``z_top`` are the frame-local vertical extents of the part (m),
# and ``members`` is the ordered chord-member list for that part.
MxfTrussPart = tuple[str, float, float, list[MxfChordMember]]

# One transport-split MXF truss frame: the truss Y position along the depth
# axis (m) and the ordered list of parts composing the frame. Short trusses
# carry a single part; tall trusses carry two (base + cap).
MxfSplitTrussFrame = tuple[float, list[MxfTrussPart]]

# An MXF engineered brace: ``(brace_type, angle_deg, x, y, member_index)``.
# ``brace_type`` is the Pamir ``EngineeredBrace.braceType`` attribute
# (:data:`BRACE_TYPE_PURLIN`); ``angle_deg`` is the brace rotation in degrees
# (matches the roof pitch so each purlin is rendered square to its slope);
# ``(x, y)`` is the brace anchor in the frame LOCAL coordinate system (metres);
# and ``member_index`` is the 0-based index of the referenced chord member within its Frame's MemberList (left top chord = 0, right top
# chord = 1 — matching the order emitted by
# :meth:`GeometrySolver._gable_full_span_members`).
MxfBrace = tuple[str, float, float, float, int]


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
        overhang_mm: float = 0.0,
    ) -> None:
        self.width_mm = width_mm
        self.depth_mm = depth_mm
        self.roof_key = roof_key
        self.roof_pitch = roof_pitch
        self.pitch_deg = resolve_pitch(roof_key, roof_pitch)
        self.overhang_m = overhang_mm / 1000.0
        self.count = compute_truss_count(width_mm / 1000.0, depth_mm / 1000.0)
        self.positions = truss_positions(width_mm, depth_mm, self.count)
        if roof_key in ("gable", "hip"):
            self.ridge_height = (width_mm / 2.0 + overhang_mm) * math.tan(self.pitch_deg * math.pi / 180.0)
        else:
            self.ridge_height = truss_ridge_height(width_mm, roof_key, self.pitch_deg)

    @property
    def z_eave(self) -> float:
        """Z coordinate (mm) of the wall top plate / eaves baseline."""
        return WALL_HEIGHT

    @property
    def z_ridge(self) -> float:
        """Z coordinate (mm) of the truss ridge."""
        return WALL_HEIGHT + self.ridge_height

    @property
    def truss_height_m(self) -> float:
        """Total truss height in metres (ridge rise above the eaves baseline).

        This is the vertical dimension that must satisfy the road transport
        limit. It equals the frame-local ridge Y (the eaves baseline sits at
        ``Y = 0`` in the MXF frame convention), so the existing heel-less
        gable geometry maps directly to the design's ``H_truss`` transport
        height.
        """
        return self.ridge_height / 1000.0

    def needs_transport_split(self, overhang_m: float = 0.0) -> bool:
        """True when the truss exceeds the 3.3 m road transport height limit."""
        return self.truss_height_m > TRANSPORT_MAX_HEIGHT_M

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

    def mxf_truss_frames(self, overhang_m: float = 0.0) -> list[MxfTrussFrame]:
        """Return per-truss full-span gable chord geometry in metres (MXF convention).

        Each returned frame holds the LOCAL chord coordinates for one truss
        position, ready for direct emission into the Layout MXF
        ``<FrameList>``. Coordinates use the MXF frame convention: X runs
        along the span (0 = left wall, ``width_mm/1000`` = right wall) and Y
        is the height above the wall-plate / eaves baseline (rising to the
        ridge).

        For gable roofs every frame carries a single full-span ``BottomChord``
        (wall-to-wall) plus two sloping ``TopChord`` members that meet at the
        central ridge at ``X = width/2``. This is the structurally valid
        full-span layout that prevents MiTek Pamir from auto-framing each roof
        half into split half-span trusses (see proposal.md). Non-gable roof
        types return an empty list because full-span truss framing is only
        implemented for gable roofs in this change.

        Args:
            overhang_m: Optional top-chord overhang extension past the outer
                walls in metres. The bottom chord always spans exactly
                wall-to-wall; the overhang only lengthens the top chords
                (rafter tails) past the eaves.

        Returns:
            One :class:`MxfTrussFrame` per truss position along the depth
            axis. Each frame shares the same LOCAL chord layout; only the Y
            position (first tuple element) differs.
        """
        if self.roof_key != "gable":
            return []

        frames: list[MxfTrussFrame] = []
        for y_mm in self.positions:
            y_m = y_mm / 1000.0
            frames.append((y_m, self._gable_full_span_members(overhang_m)))
        return frames

    def mxf_truss_parts(self, overhang_m: float = 0.0) -> list[MxfSplitTrussFrame]:
        """Return per-truss chord geometry, split for transport when tall (m).

        Each returned frame holds the LOCAL chord coordinates for one truss
        position. When :meth:`needs_transport_split` is true the frame carries
        two parts following design.md §"Transport Limit Detection":

        * **Part 1 (Base)** — a rectangular base from ``Y = 0`` to
          ``Y = TRANSPORT_SPLIT_HEIGHT_M`` (2.8 m) with a wall-to-wall
          ``BottomChord`` at ``Y = 0`` and a flat horizontal ``TopChord`` at
          ``Y = 2.8 m`` (the lower splice chord).
        * **Part 2 (Cap)** — a triangular cap resting on Part 1, from
          ``Y = 2.8 m`` up to the ridge. Its ``BottomChord`` is the horizontal
          upper splice chord at the split line; its two ``TopChord`` members
          are the collinear segments of the original sloping top chords above
          the split line, so the roof pitch is preserved across the splice.

        When the truss fits within the transport limit the frame carries a
        single part (``"Part 1"``) spanning the full height, geometrically
        equivalent to :meth:`mxf_truss_frames`. Non-gable roof types return an
        empty list because transport splitting is only implemented for gable
        roofs in this change.

        Args:
            overhang_m: Optional top-chord overhang extension past the outer
                walls in metres. Applied to the full-span (non-split) top
                chords only; transport-split base/cap chords are emitted
                wall-to-wall so the horizontal splice interface stays clean.

        Returns:
            One :class:`MxfSplitTrussFrame` per truss position along the depth
            axis.
        """
        if self.roof_key != "gable":
            return []

        h = self.truss_height_m
        split_z = TRANSPORT_SPLIT_HEIGHT_M

        frames: list[MxfSplitTrussFrame] = []
        for y_mm in self.positions:
            y_m = y_mm / 1000.0
            if self.needs_transport_split(overhang_m):
                parts = self._gable_split_parts(h, split_z, overhang_m)
            else:
                parts = [("Part 1", 0.0, h, self._gable_full_span_members(overhang_m))]
            frames.append((y_m, parts))
        return frames

    def _gable_full_span_members(self, overhang_m: float) -> list[MxfChordMember]:
        """Return the full-span chord members for one gable truss (metres).

        Two sloping ``TopChord`` members meet at the central ridge at
        ``X = width/2``; a single wall-to-wall ``BottomChord`` ties the eaves.
        ``overhang_m`` only lengthens the top chords (rafter tails) past the
        eaves. Shared by :meth:`mxf_truss_frames`, the non-split path of
        :meth:`mxf_truss_parts`, and :meth:`_gable_end_members` so every code
        path emits identical full-span chord geometry.
        """
        w_m = self.width_mm / 1000.0
        ridge_m = self.truss_height_m
        mid = w_m / 2.0
        o = overhang_m
        return [
            ("TopChord", (-o, 0.0), (mid, ridge_m)),
            ("TopChord", (mid, ridge_m), (w_m + o, 0.0)),
            ("BottomChord", (0.0, 0.0), (w_m, 0.0)),
        ]

    def mxf_gable_end_frames(
        self, overhang_m: float = 0.0
    ) -> list[MxfTrussFrame]:
        """Return the gable-end panel frames at the outer layout positions (m).

        The first and last truss positions in the layout sequence are emitted
        as ``GableEnd`` family ``roof``-type Frame definitions: they share the
        full-span gable chord profile (one wall-to-wall ``BottomChord`` plus
        two sloping ``TopChord`` members meeting at the ridge) and add vertical
        ``Stud`` members spaced at the standard 600 mm pitch (see design.md
        §"Outer Gable-End Panels"). Each stud runs from the bottom chord
        (``Y = 0``) up to the top-chord height at the stud's ``X`` coordinate;
        degenerate zero-height studs at the eaves corners (where the top chord
        meets the bottom chord) are omitted so every emitted stud is a real
        vertical member.

        Non-gable roof types return an empty list because gable-end panels are
        only meaningful for gable roofs in this change. A layout with fewer
        than two truss positions also returns an empty list because gable-end
        designation requires distinct first/last positions.

        Args:
            overhang_m: Optional top-chord overhang extension past the outer
                walls in metres. Applied to the gable-end panel's top chords
                (rafter tails) so its outer profile matches the neighbouring
                common trusses; the studs are placed within the building width
                (``X`` in ``[0, width]``) and are unaffected by the overhang.

        Returns:
            Two :class:`MxfTrussFrame` entries: the first and last truss
            positions along the depth axis, each carrying the same gable-end
            panel member list (chords + studs).
        """
        if self.roof_key != "gable" or len(self.positions) < 2:
            return []

        members = self._gable_end_members(overhang_m)
        first_y_m = self.positions[0] / 1000.0
        last_y_m = self.positions[-1] / 1000.0
        return [(first_y_m, members), (last_y_m, members)]

    def _gable_end_members(self, overhang_m: float) -> list[MxfChordMember]:
        """Return the chord + stud members for one gable-end panel (metres).

        Combines the standard full-span gable chord profile from
        :meth:`_gable_full_span_members` (two sloping ``TopChord`` members
        meeting at the ridge plus one wall-to-wall ``BottomChord``, with the
        top chords extended by ``overhang_m`` past the outer walls) with the
        vertical ``Stud`` members from :meth:`_gable_end_studs`. Used by
        :meth:`mxf_gable_end_frames` so both outer layout positions emit
        identical gable-end panel geometry.
        """
        members = self._gable_full_span_members(overhang_m)
        members.extend(self._gable_end_studs(overhang_m))
        return members

    def mxf_gable_end_parts(self, overhang_m: float = 0.0) -> list[MxfSplitTrussFrame]:
        """Return the gable-end panel parts at the outer layout positions (m).

        Coordinates use the MXF frame convention. When needs_transport_split()
        is true, each panel is split into Part 1 (base) and Part 2 (cap)
        joined by horizontal splice chords, and vertical Stud members are
        split at the 2.8m limit.
        """
        if self.roof_key != "gable" or len(self.positions) < 2:
            return []

        h = self.truss_height_m
        split_z = TRANSPORT_SPLIT_HEIGHT_M

        frames: list[MxfSplitTrussFrame] = []
        for y_mm in (self.positions[0], self.positions[-1]):
            y_m = y_mm / 1000.0
            if self.needs_transport_split(overhang_m):
                parts = self._gable_end_split_parts(h, split_z, overhang_m)
            else:
                parts = [("Part 1", 0.0, h, self._gable_end_members(overhang_m))]
            frames.append((y_m, parts))
        return frames

    def _gable_end_split_parts(
        self, h: float, split_z: float, overhang_m: float
    ) -> list[MxfTrussPart]:
        w_m = self.width_mm / 1000.0
        mid = w_m / 2.0
        tan_pitch = math.tan(math.radians(self.pitch_deg))
        x_left = split_z / tan_pitch - overhang_m
        x_right = w_m + overhang_m - split_z / tan_pitch

        chords_part1 = [
            ("BottomChord", (0.0, 0.0), (w_m, 0.0)),
            ("TopChord", (-overhang_m, 0.0), (x_left, split_z)),
            ("TopChord", (x_right, split_z), (w_m + overhang_m, 0.0)),
            ("TopChord", (x_left, split_z), (x_right, split_z)),
        ]
        chords_part2 = [
            ("BottomChord", (x_left, split_z), (x_right, split_z)),
            ("TopChord", (x_left, split_z), (mid, h)),
            ("TopChord", (mid, h), (x_right, split_z)),
        ]

        all_studs = self._gable_end_studs(overhang_m)
        studs_part1: list[MxfChordMember] = []
        studs_part2: list[MxfChordMember] = []

        for _mtype, (x, y_start), (_, top_y) in all_studs:
            if top_y <= split_z:
                studs_part1.append(("Stud", (x, 0.0), (x, top_y)))
            else:
                studs_part1.append(("Stud", (x, 0.0), (x, split_z)))
                studs_part2.append(("Stud", (x, split_z), (x, top_y)))

        return [
            ("Part 1", 0.0, split_z, chords_part1 + studs_part1),
            ("Part 2", split_z, h, chords_part2 + studs_part2),
        ]

    def _gable_end_studs(self, overhang_m: float) -> list[MxfChordMember]:
        """Return the vertical Stud members for one gable-end panel (metres).

        Studs are placed at standard 600 mm centres (see
        :data:`GABLE_END_STUD_SPACING_M`) starting from ``X = 0`` and stepping
        across the full building width. Each stud runs vertically from the
        bottom chord (``Y = 0``) up to the sloping top chord at its ``X``
        coordinate. The top chord is a straight line of slope ``tan(pitch)``
        passing through the eave edge ``X = -overhang`` (and ``X = width +
        overhang`` on the far side), so its height at the stud's ``X`` is:

          * ``Y = (X + overhang) * tan(pitch)`` for ``X <= width/2``
          * ``Y = (width + overhang - X) * tan(pitch)`` for ``X > width/2``

        Degenerate zero-height studs (only possible when ``overhang == 0``, at
        ``X = 0`` and ``X = width`` where the top chord meets the bottom chord)
        are skipped so every emitted stud is a real vertical member with
        positive length.
        """
        w_m = self.width_mm / 1000.0
        tan_pitch = math.tan(math.radians(self.pitch_deg))
        mid = w_m / 2.0
        studs: list[MxfChordMember] = []
        # Step across the width at GABLE_END_STUD_SPACING_M centres. The loop
        # bound is inclusive of the far wall (X = width) so a width that is an
        # exact multiple of the spacing still considers that final position.
        step_count = int(w_m / GABLE_END_STUD_SPACING_M) + 1
        for i in range(step_count + 1):
            x = i * GABLE_END_STUD_SPACING_M
            if x > w_m + 1e-9:
                break
            if x <= mid:
                top_y = (x + overhang_m) * tan_pitch
            else:
                top_y = (w_m + overhang_m - x) * tan_pitch
            if top_y <= 1e-6:
                # Degenerate (zero-height) stud; skip.
                continue
            studs.append(("Stud", (x, 0.0), (x, top_y)))
        return studs

    def _gable_split_parts(
        self, h: float, split_z: float, overhang_m: float
    ) -> list[MxfTrussPart]:
        """Return Part 1 (base) and Part 2 (cap) for a transport-split gable truss.

        The original full-span top chords cross ``Y = split_z`` at
        ``x = split_z / tan(pitch)`` (left) and ``width - split_z / tan(pitch)``
        (right); those crossings bound the triangular cap's base. The cap's top
        chords stay collinear with the full-span top chords (same pitch) because
        they are the upper segments of the same lines. Both parts carry a
        horizontal chord at ``Y = split_z`` — Part 1's flat ``TopChord`` (lower
        splice) and Part 2's ``BottomChord`` (upper splice) — which is the
        structural plate-joint interface called out in design.md.

        Args:
            h: Total truss height in metres (ridge Y); must exceed ``split_z``.
            split_z: Base height / splice-line Y in metres (2.8 m).
        """
        w_m = self.width_mm / 1000.0
        mid = w_m / 2.0
        tan_pitch = math.tan(math.radians(self.pitch_deg))
        x_left = split_z / tan_pitch - overhang_m
        x_right = w_m + overhang_m - split_z / tan_pitch

        part1_members: list[MxfChordMember] = [
            ("BottomChord", (0.0, 0.0), (w_m, 0.0)),
            ("TopChord", (-overhang_m, 0.0), (x_left, split_z)),
            ("TopChord", (x_right, split_z), (w_m + overhang_m, 0.0)),
            ("TopChord", (x_left, split_z), (x_right, split_z)),
        ]
        part2_members: list[MxfChordMember] = [
            ("BottomChord", (x_left, split_z), (x_right, split_z)),
            ("TopChord", (x_left, split_z), (mid, h)),
            ("TopChord", (mid, h), (x_right, split_z)),
        ]
        return [
            ("Part 1", 0.0, split_z, part1_members),
            ("Part 2", split_z, h, part2_members),
        ]

    def mxf_slope_braces(self, overhang_m: float = 0.0) -> list[MxfBrace]:
        """Return the slope bracing definitions for one gable truss (metres).

        Braces run along the roof slope rather than at ceiling level so MiTek
        Pamir renders them square to the top chords and the ceiling-level
        collision warnings documented in proposal.md are avoided. Two brace
        families are emitted (see design.md §"Sloped Bracing System" / spec.md
        "Roof Slope Bracing"):

        * **Purlins** (:data:`BRACE_TYPE_PURLIN`) — placed at standard
          :data:`PURLIN_SPACING_M` (1.0 m) centres along each top chord,
          stepping up from the eave toward the ridge. The Pamir ``angle``
          attribute mirrors the roof pitch (``180 - pitch`` on the right
          chord) so each purlin is rendered square to its slope.

        Only ``purlin`` braces are emitted: the reference Pamir export
        (``hidden/Sample_Project/7JULY_Z.mxf``) uses no other ``braceType`` on
        gable common trusses beyond purlins, and emitting an unrecognised
        token (e.g. a wind-brace type) causes MiTek Pamir to reject the file
        on import.

        The ``member_index`` field of each brace references the chord member
        it braces: ``0`` for the left top chord and ``1`` for the right top
        chord, matching the order emitted by :meth:`_gable_full_span_members`
        (``[TopChord-left, TopChord-right, BottomChord]``) so the
        ``<MemberLink>`` resolves to the correct chord.

        Non-gable roof types return an empty list because sloped bracing is
        only implemented for gable roofs in this change.

        Returns:
            One :class:`MxfBrace` per brace anchor. The list is shared
            verbatim by every common-truss and gable-end Frame definition
            because both share the same full-span chord profile (only the
            stud members differ), so the brace anchors and chord indices are
            identical.
        """
        if self.roof_key != "gable":
            return []

        w_m = self.width_mm / 1000.0
        mid = w_m / 2.0
        pitch_rad = math.radians(self.pitch_deg)
        cos_p = math.cos(pitch_rad)
        sin_p = math.sin(pitch_rad)

        # Top-chord length from eaves edge to ridge (metres). Both chords share
        # this length by gable symmetry, so the same step count drives both.
        chord_len = (mid + overhang_m) / cos_p

        braces: list[MxfBrace] = []

        # Purlins along the LEFT top chord at PURLIN_SPACING_M centres. The
        # loop steps up from the eave (d = spacing) and skips the ridge
        # endpoint itself when the chord length is an exact multiple of the
        # spacing (the ridge is the convergence point of the two top chords,
        # not a free purlin anchor).
        step_count = int(chord_len / PURLIN_SPACING_M)
        for i in range(1, step_count + 1):
            d = i * PURLIN_SPACING_M
            if d > chord_len - 1e-9:
                break
            x = -overhang_m + d * cos_p
            y = d * sin_p
            braces.append((BRACE_TYPE_PURLIN, self.pitch_deg, x, y, 0))

        # Purlins along the RIGHT top chord. The chord runs from (mid, ridge)
        # to (width, 0); step from the right eave toward the ridge so the
        # anchors are symmetric with the left chord. The Pamir ``angle`` is
        # ``180 - pitch`` so the brace renders square to the right-side
        # slope.
        for i in range(1, step_count + 1):
            d = i * PURLIN_SPACING_M
            if d > chord_len - 1e-9:
                break
            x = w_m + overhang_m - d * cos_p
            y = d * sin_p
            braces.append((BRACE_TYPE_PURLIN, 180.0 - self.pitch_deg, x, y, 1))

        return braces


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
