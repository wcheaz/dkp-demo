"""IFC2x3 model builder for truss and wall designs.

The builder consumes the shared :mod:`geometry_solver` module so that the
generated IFC is geometrically congruent with the DXF output produced by
:mod:`dxf_builder`. Both builders call the exact same coordinate helpers
(``wall_corners``, ``truss_positions``, ``truss_ridge_height`` ...), which
guarantees the chord joints and member lengths match across formats.

All coordinates and dimensions are expressed in millimetres. The output is a
valid ISO-10303-21 (STEP) text document using the ``IFC2x3`` schema, targeting
compatibility with MiTek Pamir.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

import ifcopenshell  # type: ignore[import-not-found]
import ifcopenshell.guid  # type: ignore[import-not-found]

try:
    from src.geometry_solver import (
        WALL_HEIGHT,
        compute_truss_count,
        parse_dimensions,
        resolve_pitch,
        truss_positions,
        truss_ridge_height,
        wall_corners,
    )
except ImportError:  # pragma: no cover - direct module import in unit tests
    from geometry_solver import (  # type: ignore[no-redef,import-not-found]
        WALL_HEIGHT,
        compute_truss_count,
        parse_dimensions,
        resolve_pitch,
        truss_positions,
        truss_ridge_height,
        wall_corners,
    )

if TYPE_CHECKING:
    from src.agent import DesignParameters

# Nominal timber sizing (mm): thickness x width, matching the lumber specs drawn
# by ``dxf_builder`` and the ``"ThicknessxWidth"`` profile name required by the
# IFC generation spec.
MEMBER_THICKNESS = 45.0
MEMBER_WIDTH = 120.0
MEMBER_PROFILE_NAME = "45x120"

# Lumber material assigned to every generated IfcMember. Hardcoded for now;
# see ``build_ifc`` for notes on making it dynamic via ``DesignParameters``.
TIMBER_MATERIAL_NAME = "Timber - C24"

WALL_THICKNESS = 200.0

_VALID_ROOF_TYPES = {"gable", "hip", "mono-pitch", "flat"}


def _axis3d(
    f: Any,
    location: tuple[float, float, float],
    axis: tuple[float, float, float],
    refdir: tuple[float, float, float],
) -> Any:
    return f.createIfcAxis2Placement3D(
        f.createIfcCartesianPoint(location),
        f.createIfcDirection(axis),
        f.createIfcDirection(refdir),
    )


def _rectangle_profile(f: Any, name: str, xdim: float, ydim: float) -> Any:
    position = f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0)), None)
    return f.createIfcRectangleProfileDef("AREA", name, position, xdim, ydim)


def _extruded_solid(f: Any, profile: Any, depth: float) -> Any:
    """Centered profile swept along the local +Z axis by ``depth`` millimetres."""
    position = _axis3d(f, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
    direction = f.createIfcDirection((0.0, 0.0, 1.0))
    return f.createIfcExtrudedAreaSolid(profile, position, direction, depth)


def _body_shape(f: Any, context: Any, extruded: Any) -> Any:
    body = f.createIfcShapeRepresentation(context, "Body", "SweptSolid", [extruded])
    return f.createIfcProductDefinitionShape(None, None, [body])


def _perpendicular(direction: tuple[float, float, float]) -> tuple[float, float, float]:
    """Return a unit vector perpendicular to ``direction`` (the member local X)."""
    dx, dy, _dz = direction
    rx, ry, rz = -dy, dx, 0.0
    norm = math.sqrt(rx * rx + ry * ry + rz * rz)
    if norm == 0:
        return (1.0, 0.0, 0.0)
    return (rx / norm, ry / norm, rz / norm)


def _create_owner_history(f: Any) -> Any:
    person = f.createIfcPerson("DKP", "DKP", "Demo", None, None, None, None, None)
    org = f.createIfcOrganization("DKP", "DKP Demo", None, None, None)
    person_org = f.createIfcPersonAndOrganization(person, org, None)
    app_org = f.createIfcOrganization("IfcOpenShell", "IfcOpenShell", None, None, None)
    application = f.createIfcApplication(
        app_org, ifcopenshell.__version__, "IfcOpenShell", "IfcOpenShell"
    )
    return f.createIfcOwnerHistory(
        person_org, application, None, "ADDED", None, None, None, 0
    )


def _add_wall(
    f: Any,
    context: Any,
    owner_history: Any,
    storey_placement: Any,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    thickness: float,
    height: float,
) -> Any:
    """Add an ``IfcWallStandardCase`` swept along one wall edge."""
    sx, sy, _sz = start
    ex, ey, _ez = end
    seg_dx, seg_dy = ex - sx, ey - sy
    length = math.sqrt(seg_dx * seg_dx + seg_dy * seg_dy)
    if length == 0:
        length = 1e-9
    seg_dir = (seg_dx / length, seg_dy / length, 0.0)
    mid = ((sx + ex) / 2, (sy + ey) / 2, 0.0)
    placement3d = _axis3d(f, mid, (0.0, 0.0, 1.0), seg_dir)
    local_placement = f.createIfcLocalPlacement(storey_placement, placement3d)
    profile = _rectangle_profile(f, "WallProfile", length, thickness)
    extruded = _extruded_solid(f, profile, height)
    shape = _body_shape(f, context, extruded)
    return f.createIfcWallStandardCase(
        ifcopenshell.guid.new(),
        owner_history,
        "Wall",
        None,
        None,
        local_placement,
        shape,
        None,
    )


def _add_member(
    f: Any,
    context: Any,
    owner_history: Any,
    storey_placement: Any,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    profile_name: str,
    thickness: float,
    width: float,
) -> Any:
    """Add an ``IfcMember`` swept along the segment centreline."""
    ax, ay, az = start
    bx, by, bz = end
    dx, dy, dz = bx - ax, by - ay, bz - az
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length == 0:
        length = 1e-9
    direction = (dx / length, dy / length, dz / length)
    refdir = _perpendicular(direction)
    placement3d = _axis3d(f, (ax, ay, az), direction, refdir)
    local_placement = f.createIfcLocalPlacement(storey_placement, placement3d)
    profile = _rectangle_profile(f, profile_name, thickness, width)
    extruded = _extruded_solid(f, profile, length)
    shape = _body_shape(f, context, extruded)
    return f.createIfcMember(
        ifcopenshell.guid.new(),
        owner_history,
        profile_name,
        None,
        None,
        local_placement,
        shape,
        None,
    )


def _member_segments(
    width_mm: float,
    depth_mm: float,
    roof_key: str,
    roof_pitch: float | None,
) -> list[tuple[tuple[float, float, float], tuple[float, float, float]]]:
    """Return the start/end coordinates of every timber member.

    Mirrors ``dxf_builder._draw_trusses`` exactly, sourcing the truss count,
    spacing and ridge height from the shared :mod:`geometry_solver` so DXF and
    IFC outputs stay geometrically congruent.
    """
    count = compute_truss_count(width_mm / 1000, depth_mm / 1000)
    pitch_deg = resolve_pitch(roof_key, roof_pitch)
    positions = truss_positions(width_mm, depth_mm, count)
    ridge_h = truss_ridge_height(width_mm, roof_key, pitch_deg)

    z_eave = WALL_HEIGHT
    z_ridge = WALL_HEIGHT + ridge_h
    w = width_mm

    segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
    for y in positions:
        if roof_key in ("gable", "hip"):
            segments.append(((0.0, y, z_eave), (w / 2, y, z_ridge)))
            segments.append(((w, y, z_eave), (w / 2, y, z_ridge)))
            segments.append(((0.0, y, z_eave), (w, y, z_eave)))
        elif roof_key == "mono-pitch":
            segments.append(((0.0, y, z_eave), (w, y, z_ridge)))
            segments.append(((0.0, y, z_eave), (w, y, z_eave)))
            segments.append(((w, y, z_eave), (w, y, z_ridge)))
        else:  # flat roof: single ceiling joist
            segments.append(((0.0, y, z_eave), (w, y, z_eave)))
    return segments


def build_ifc(params: DesignParameters) -> bytes:
    """Build a valid IFC2x3 model (as ``bytes``) from design parameters."""
    if params.roofType is None:
        raise ValueError("roofType is required")
    roof_key = params.roofType.strip().lower()
    if roof_key not in _VALID_ROOF_TYPES:
        raise ValueError(f"Unsupported roofType: {params.roofType!r}")

    width_mm, depth_mm = parse_dimensions(params.floorPlanDimensions)

    roof_pitch = getattr(params, "roofPitch", None)
    pitch_raw: float | None = float(roof_pitch) if roof_pitch is not None else None

    f = ifcopenshell.file(schema="IFC2X3")

    length_unit = f.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")
    area_unit = f.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE")
    volume_unit = f.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE")
    angle_unit = f.createIfcSIUnit(None, "PLANEANGLEUNIT", None, "RADIAN")
    unit_assignment = f.createIfcUnitAssignment(
        [length_unit, area_unit, volume_unit, angle_unit]
    )

    world = _axis3d(f, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
    context = f.createIfcGeometricRepresentationContext(
        None, "Model", 3, 1.0e-5, world, None
    )

    owner_history = _create_owner_history(f)

    project = f.createIfcProject(
        ifcopenshell.guid.new(),
        owner_history,
        "DKP Project",
        None,
        None,
        None,
        None,
        [context],
        unit_assignment,
    )

    site_placement = f.createIfcLocalPlacement(None, world)
    site = f.createIfcSite(
        ifcopenshell.guid.new(),
        owner_history,
        "DKP Site",
        None,
        None,
        site_placement,
        None,
        None,
        "ELEMENT",
        None,
        None,
        None,
        None,
        None,
    )
    building_placement = f.createIfcLocalPlacement(site_placement, world)
    building = f.createIfcBuilding(
        ifcopenshell.guid.new(),
        owner_history,
        "DKP Building",
        None,
        None,
        building_placement,
        None,
        None,
        "ELEMENT",
        0.0,
        0.0,
        None,
    )
    storey_placement = f.createIfcLocalPlacement(building_placement, world)
    storey = f.createIfcBuildingStorey(
        ifcopenshell.guid.new(),
        owner_history,
        "Ground Storey",
        None,
        None,
        storey_placement,
        None,
        None,
        "ELEMENT",
        0.0,
    )

    f.createIfcRelAggregates(
        ifcopenshell.guid.new(), owner_history, "ProjectContainer", None, project, [site]
    )
    f.createIfcRelAggregates(
        ifcopenshell.guid.new(), owner_history, "SiteContainer", None, site, [building]
    )
    f.createIfcRelAggregates(
        ifcopenshell.guid.new(),
        owner_history,
        "BuildingContainer",
        None,
        building,
        [storey],
    )

    elements: list[Any] = []
    members: list[Any] = []

    corners = wall_corners(width_mm, depth_mm)
    for i in range(4):
        sx, sy = corners[i]
        ex, ey = corners[(i + 1) % 4]
        elements.append(
            _add_wall(
                f,
                context,
                owner_history,
                storey_placement,
                (sx, sy, 0.0),
                (ex, ey, 0.0),
                WALL_THICKNESS,
                WALL_HEIGHT,
            )
        )

    for start, end in _member_segments(width_mm, depth_mm, roof_key, pitch_raw):
        member = _add_member(
            f,
            context,
            owner_history,
            storey_placement,
            start,
            end,
            MEMBER_PROFILE_NAME,
            MEMBER_THICKNESS,
            MEMBER_WIDTH,
        )
        elements.append(member)
        members.append(member)

    f.createIfcRelContainedInSpatialStructure(
        ifcopenshell.guid.new(),
        owner_history,
        "StoreyContents",
        None,
        elements,
        storey,
    )

    # Associate every generated timber IfcMember with a lumber material. A
    # single project-level IfcMaterial is mapped to all members via one
    # IfcRelAssociatesMaterial, keeping the STEP output compact while still
    # surfacing material data to downstream tools such as MiTek Pamir.
    #
    # The material name is currently hardcoded as "Timber - C24". To make it
    # dynamic, ``DesignParameters`` could expose a field such as
    # ``lumberMaterial: str`` and this value would be read from ``params``
    # instead of the module-level constant above.
    if members:
        timber_material = f.createIfcMaterial(TIMBER_MATERIAL_NAME)
        f.createIfcRelAssociatesMaterial(
            ifcopenshell.guid.new(),
            owner_history,
            "MemberMaterial",
            None,
            members,
            timber_material,
        )

    text = str(f.wrapped_data.to_string())
    return text.encode("utf-8")
