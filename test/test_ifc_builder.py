import math
import sys
from pathlib import Path
from types import SimpleNamespace

import ifcopenshell
import pytest

sys.path.insert(0, "agent/src")
from ifc_builder import build_ifc
from geometry_solver import (
    WALL_HEIGHT,
    compute_truss_count,
    resolve_pitch,
    truss_positions,
    truss_ridge_height,
)


def _params(**kwargs):
    return SimpleNamespace(**kwargs)


def _parse(raw: bytes):
    return ifcopenshell.file.from_string(raw.decode("utf-8"))


def _body_item(element):
    reps = element.Representation.Representations
    body = [r for r in reps if r.RepresentationIdentifier == "Body"][0]
    return body.Items[0]


class TestValidIfcOutput:
    def test_non_empty_bytes(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_ifc(params)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_schema_identifier(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_ifc(params)
        assert b"FILE_SCHEMA(('IFC2X3'));" in result

    def test_required_entities_present(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        model = _parse(build_ifc(params))
        assert len(model.by_type("IfcProject")) == 1
        assert len(model.by_type("IfcSite")) == 1
        assert len(model.by_type("IfcBuilding")) == 1
        assert len(model.by_type("IfcBuildingStorey")) == 1
        assert len(model.by_type("IfcWallStandardCase")) == 4
        assert len(model.by_type("IfcMember")) >= 1


class TestSpatialHierarchy:
    def _build(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        return _parse(build_ifc(params))

    def test_aggregation_chain(self):
        model = self._build()
        project = model.by_type("IfcProject")[0]
        site = model.by_type("IfcSite")[0]
        building = model.by_type("IfcBuilding")[0]
        storey = model.by_type("IfcBuildingStorey")[0]
        aggs = model.by_type("IfcRelAggregates")
        assert any(
            a.RelatingObject == project and site in a.RelatedObjects for a in aggs
        )
        assert any(
            a.RelatingObject == site and building in a.RelatedObjects for a in aggs
        )
        assert any(
            a.RelatingObject == building and storey in a.RelatedObjects for a in aggs
        )

    def test_containment_links_to_storey(self):
        model = self._build()
        storey = model.by_type("IfcBuildingStorey")[0]
        rels = model.by_type("IfcRelContainedInSpatialStructure")
        assert len(rels) >= 1
        contained: list = []
        for rel in rels:
            contained.extend(rel.RelatedElements)
        for wall in model.by_type("IfcWallStandardCase"):
            assert wall in contained
        for member in model.by_type("IfcMember"):
            assert member in contained
        assert any(rel.RelatingStructure == storey for rel in rels)


class TestUnits:
    def test_length_unit_milli_metre(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        model = _parse(build_ifc(params))
        units = model.by_type("IfcProject")[0].UnitsInContext.Units
        length = [u for u in units if getattr(u, "UnitType", None) == "LENGTHUNIT"][0]
        assert length.Name == "METRE"
        assert length.Prefix == "MILLI"


class TestMemberGeometry:
    def test_members_are_extruded_swept_solids(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        model = _parse(build_ifc(params))
        assert len(model.by_type("IfcMember")) > 0
        for member in model.by_type("IfcMember"):
            item = _body_item(member)
            assert item.is_a("IfcExtrudedAreaSolid")
            profile = item.SweptArea
            assert profile.is_a("IfcRectangleProfileDef")
            assert profile.ProfileName == "45x120"
            loc = profile.Position.Location.Coordinates
            assert abs(loc[0]) < 1e-6
            assert abs(loc[1]) < 1e-6

    def test_profile_dimensions(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        model = _parse(build_ifc(params))
        profile = _body_item(model.by_type("IfcMember")[0]).SweptArea
        assert profile.ProfileName == "45x120"
        assert profile.XDim == 45.0
        assert profile.YDim == 120.0

    def test_walls_use_extruded_solids(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        model = _parse(build_ifc(params))
        for wall in model.by_type("IfcWallStandardCase"):
            assert _body_item(wall).is_a("IfcExtrudedAreaSolid")


class TestMaterialAssociation:
    def test_timber_material_association(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        model = _parse(build_ifc(params))

        materials = model.by_type("IfcMaterial")
        assert len(materials) >= 1
        timber = [m for m in materials if m.Name == "Timber - C24"]
        assert len(timber) == 1

        rels = model.by_type("IfcRelAssociatesMaterial")
        assert len(rels) >= 1

        members = model.by_type("IfcMember")
        assert len(members) >= 1

        # Every IfcMember must be linked to the "Timber - C24" material via an
        # IfcRelAssociatesMaterial whose RelatingMaterial is that IfcMaterial.
        linked_members: list = []
        timber_relation_found = False
        for rel in rels:
            if rel.RelatingMaterial == timber[0]:
                timber_relation_found = True
                linked_members.extend(
                    obj for obj in rel.RelatedObjects if obj.is_a("IfcMember")
                )
        assert timber_relation_found
        for member in members:
            assert member in linked_members


class TestSharedGeometry:
    @pytest.mark.parametrize("roof_type", ["Gable", "Hip", "Mono-pitch", "Flat"])
    def test_member_count_matches_geometry_solver(self, roof_type):
        params = _params(
            floorPlanDimensions="10x15m", roofType=roof_type, roofPitch=30
        )
        model = _parse(build_ifc(params))
        count = compute_truss_count(10, 15)
        members = model.by_type("IfcMember")
        if roof_type.lower() == "flat":
            assert len(members) == count * 1
        else:
            assert len(members) == count * 3

    def test_gable_rafter_length_matches_shared_coordinates(self):
        w = 10000.0
        params = _params(floorPlanDimensions="10x10m", roofType="Gable", roofPitch=30)
        model = _parse(build_ifc(params))
        positions = truss_positions(w, w, compute_truss_count(10, 10))
        pitch_deg = resolve_pitch("gable", 30)
        ridge_h = truss_ridge_height(w, "gable", pitch_deg)
        z_rise = WALL_HEIGHT + ridge_h - WALL_HEIGHT
        expected = math.sqrt((w / 2) ** 2 + z_rise ** 2)
        depths = [_body_item(m).Depth for m in model.by_type("IfcMember")]
        assert any(abs(d - expected) < 1.0 for d in depths)


class TestRoundTripAllRoofTypes:
    @pytest.mark.parametrize("roof_type", ["Gable", "Hip", "Mono-pitch", "Flat"])
    def test_reparseable(self, roof_type):
        params = _params(
            floorPlanDimensions="10x15m", roofType=roof_type, roofPitch=30
        )
        model = _parse(build_ifc(params))
        assert len(model.by_type("IfcWallStandardCase")) == 4
        assert len(model.by_type("IfcMember")) >= 1


class TestInvalidInputs:
    def test_none_roof_type_raises(self):
        params = _params(floorPlanDimensions="10x15m", roofType=None)
        with pytest.raises(ValueError):
            build_ifc(params)

    def test_unsupported_roof_type_raises(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gambrel")
        with pytest.raises(ValueError):
            build_ifc(params)

    def test_malformed_dimensions_raises(self):
        params = _params(
            floorPlanDimensions="about twenty meters", roofType="Gable"
        )
        with pytest.raises(ValueError):
            build_ifc(params)


_GENERATED_DIR = Path(__file__).resolve().parent.parent / "generated"

_EXAMPLE_CONFIGS = [
    ("gable", "10x15m", "Gable", 30),
    ("hip", "10x15m", "Hip", 30),
    ("mono-pitch", "10x15m", "Mono-pitch", 15),
    ("flat", "10x15m", "Flat", 0),
    ("decimal", "8.5x12.3m", "Gable", 35),
]


class TestGenerateExampleFiles:
    @pytest.mark.parametrize(
        "name,dims,roof,pitch",
        _EXAMPLE_CONFIGS,
        ids=[c[0] for c in _EXAMPLE_CONFIGS],
    )
    def test_write_example_ifc(self, name, dims, roof, pitch):
        _GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        params = _params(floorPlanDimensions=dims, roofType=roof, roofPitch=pitch)
        result = build_ifc(params)
        model = _parse(result)
        assert len(model.by_type("IfcWallStandardCase")) == 4
        assert len(model.by_type("IfcMember")) >= 1
        out_path = _GENERATED_DIR / f"{name}.ifc"
        out_path.write_bytes(result)
