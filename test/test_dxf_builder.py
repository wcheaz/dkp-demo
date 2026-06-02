import math
import sys
from io import BytesIO, StringIO
from pathlib import Path
from types import SimpleNamespace

import ezdxf
import pytest

sys.path.insert(0, "agent/src")
from dxf_builder import (
    build_dxf,
    _compute_truss_count,
    LAYER_FLOOR_PLAN,
    LAYER_WALL_CENTERLINES,
    LAYER_ROOF_OUTLINE,
    LAYER_TRUSSES,
    LAYER_DIMENSIONS,
    LAYER_LABELS,
    LAYER_LUMBER_SPECS,
    LAYER_TITLE_BLOCK,
)


def _params(**kwargs):
    return SimpleNamespace(**kwargs)


def _read_dxf(raw: bytes):
    return ezdxf.read(StringIO(raw.decode("utf-8")))


def _entities_on_layer(msp, layer: str, etype=None):
    ents = [e for e in msp if e.dxf.layer == layer]
    if etype:
        ents = [e for e in ents if e.dxftype() == etype]
    return ents


def _lwpolyline_vertices(pl):
    return [(v[0], v[1]) for v in pl.get_points(format="xy")]


class TestValidDxfOutput:
    def test_re_readable(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        assert doc.dxfversion == "AC1018"

    def test_layers_exist(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer_names = [l.dxf.name for l in doc.layers]
        assert LAYER_FLOOR_PLAN in layer_names
        assert LAYER_ROOF_OUTLINE in layer_names


class TestFloorPlanOutline:
    def test_10x15m_floor_plan_3d(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_FLOOR_PLAN, "LINE")
        assert len(lines) == 12
        bottom = [l for l in lines if abs(l.dxf.start.z) < 0.01 and abs(l.dxf.end.z) < 0.01]
        top = [l for l in lines if abs(l.dxf.start.z - 2700) < 0.01 and abs(l.dxf.end.z - 2700) < 0.01]
        vertical = [l for l in lines if abs(l.dxf.start.z - l.dxf.end.z) > 0.01]
        assert len(bottom) == 4
        assert len(top) == 4
        assert len(vertical) == 4

    def test_decimal_dimensions_3d(self):
        params = _params(floorPlanDimensions="8.5x12.3m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_FLOOR_PLAN, "LINE")
        assert len(lines) == 12

    def test_wall_centerlines_layer(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        polys = _entities_on_layer(msp, LAYER_WALL_CENTERLINES, "LWPOLYLINE")
        assert len(polys) == 1
        verts = _lwpolyline_vertices(polys[0])
        expected = [(0, 0), (10000, 0), (10000, 15000), (0, 15000)]
        for v, e in zip(verts, expected):
            assert abs(v[0] - e[0]) < 0.01
            assert abs(v[1] - e[1]) < 0.01


class TestInvalidDimensions:
    def test_none_dimensions_raises(self):
        params = _params(floorPlanDimensions=None, roofType="Flat")
        with pytest.raises(ValueError):
            build_dxf(params)

    def test_malformed_dimensions_raises(self):
        params = _params(floorPlanDimensions="about twenty meters", roofType="Flat")
        with pytest.raises(ValueError):
            build_dxf(params)


class TestGableRoof:
    def test_gable_roof_outline(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) == 5
        ridge_found = False
        for line in lines:
            start = (line.dxf.start.x, line.dxf.start.y, line.dxf.start.z)
            end = (line.dxf.end.x, line.dxf.end.y, line.dxf.end.z)
            if abs(start[0] - 5000) < 0.01 and abs(end[0] - 5000) < 0.01:
                ridge_found = True
                assert abs(start[2] - end[2]) < 0.01
                assert start[2] > 2700
        assert ridge_found, "Ridge line at x=5000 not found"
        rafter_lines = [l for l in lines if abs(l.dxf.start.z - 2700) < 0.01 and l.dxf.end.z > 2700]
        assert len(rafter_lines) == 4


class TestHipRoof:
    def test_hip_roof_outline(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Hip", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) == 5
        ridge_lines = []
        hip_lines = []
        for line in lines:
            s = (line.dxf.start.x, line.dxf.start.y, line.dxf.start.z)
            e = (line.dxf.end.x, line.dxf.end.y, line.dxf.end.z)
            if abs(s[0] - 5000) < 0.01 and abs(e[0] - 5000) < 0.01:
                ridge_len = abs(e[1] - s[1])
                ridge_lines.append(ridge_len)
                assert abs(s[2] - e[2]) < 0.01
                assert s[2] > 2700
            else:
                hip_lines.append((s, e))
        assert len(ridge_lines) == 1
        assert abs(ridge_lines[0] - 5000) < 0.01
        assert len(hip_lines) == 4
        for s, e in hip_lines:
            assert (abs(s[2] - 2700) < 0.01 and e[2] > 2700) or (abs(e[2] - 2700) < 0.01 and s[2] > 2700)


class TestMonoPitchRoof:
    def test_mono_pitch_roof_outline(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Mono-pitch")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) >= 4
        z_values = set()
        for line in lines:
            z_values.add(round(line.dxf.start.z, 1))
            z_values.add(round(line.dxf.end.z, 1))
        assert any(abs(z - 2700) < 0.01 for z in z_values)

    def test_mono_pitch_3d_slope(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Mono-pitch", roofPitch=10)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        slope_lines = [l for l in lines if abs(l.dxf.start.z - l.dxf.end.z) > 0.01]
        assert len(slope_lines) >= 1


class TestFlatRoof:
    def test_flat_roof_outline(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) == 4
        for line in lines:
            assert abs(line.dxf.start.z - 2700) < 0.01
            assert abs(line.dxf.end.z - 2700) < 0.01
        corners = set()
        for line in lines:
            corners.add((round(line.dxf.start.x, 1), round(line.dxf.start.y, 1)))
            corners.add((round(line.dxf.end.x, 1), round(line.dxf.end.y, 1)))
        expected = {(0, 0), (10000, 0), (10000, 15000), (0, 15000)}
        assert corners == expected


class TestInvalidRoofType:
    def test_none_roof_type_raises(self):
        params = _params(floorPlanDimensions="10x15m", roofType=None)
        with pytest.raises(ValueError):
            build_dxf(params)

    def test_unsupported_roof_type_raises(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gambrel")
        with pytest.raises(ValueError):
            build_dxf(params)


class TestCaseInsensitiveRoofType:
    def test_case_insensitive_gable(self):
        params = _params(floorPlanDimensions="10x15m", roofType="gable")
        result = build_dxf(params)
        doc = _read_dxf(result)
        assert doc.dxfversion == "AC1018"

    def test_case_insensitive_flat(self):
        params = _params(floorPlanDimensions="10x15m", roofType="FLAT")
        result = build_dxf(params)
        doc = _read_dxf(result)
        assert doc.dxfversion == "AC1018"


_ALL_FIVE_LAYERS = {LAYER_FLOOR_PLAN, LAYER_ROOF_OUTLINE, LAYER_TRUSSES, LAYER_DIMENSIONS, LAYER_LABELS, LAYER_LUMBER_SPECS}


class TestTrussCount:
    def test_10x15m(self):
        assert _compute_truss_count(10, 15) == 22

    def test_small_building(self):
        assert _compute_truss_count(3, 4) == 2

    def test_tiny_building_minimum(self):
        assert _compute_truss_count(0.5, 0.5) == 2

    def test_large_building(self):
        result = _compute_truss_count(20, 30)
        assert result == max(2, round(20 * 30 * 0.147))

    def test_square_building(self):
        result = _compute_truss_count(10, 10)
        assert result == max(2, round(10 * 10 * 0.147))


class TestTrussCrossSectionGable:
    def test_truss_layer_has_lines(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        count = _compute_truss_count(10, 15)
        assert len(lines) == count * 3

    def test_first_truss_inset(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        y_coords = sorted(set(round(l.dxf.start.y, 1) for l in lines))
        first_y = y_coords[0]
        expected_inset = 10000 * 0.05
        assert abs(first_y - expected_inset) < 1.0

    def test_triangle_shape(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        first_y = 10000 * 0.05
        ridge_h = (10000 / 2) * math.tan(30 * math.pi / 180)
        truss_at_first = [l for l in lines if abs(l.dxf.start.y - first_y) < 1.0 or abs(l.dxf.end.y - first_y) < 1.0]
        assert len(truss_at_first) == 3
        z_values = []
        for l in truss_at_first:
            z_values.extend([l.dxf.start.z, l.dxf.end.z])
        has_ridge = any(abs(zv - (2700 + ridge_h)) < 1.0 for zv in z_values)
        assert has_ridge


class TestTrussCrossSectionHip:
    def test_truss_layer_has_lines(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Hip", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        count = _compute_truss_count(10, 15)
        assert len(lines) == count * 3


class TestTrussCrossSectionMonoPitch:
    def test_truss_layer_has_lines(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Mono-pitch", roofPitch=10)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        count = _compute_truss_count(10, 15)
        assert len(lines) == count * 3

    def test_right_triangle_shape(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Mono-pitch", roofPitch=10)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        first_y = 10000 * 0.05
        ridge_h = 10000 * math.tan(10 * math.pi / 180)
        truss_lines = [l for l in lines if abs(l.dxf.start.y - first_y) < 1.0]
        assert len(truss_lines) >= 1
        slope_line = [l for l in truss_lines if abs(l.dxf.end.z - (2700 + ridge_h)) < 1.0]
        assert len(slope_line) >= 1


class TestTrussCrossSectionFlat:
    def test_truss_layer_has_horizontal_lines(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        count = _compute_truss_count(10, 15)
        assert len(lines) == count
        for line in lines:
            assert abs(line.dxf.start.y - line.dxf.end.y) < 0.01


class TestDimensionEntities:
    def test_width_and_depth_dimensions_present(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        dims = _entities_on_layer(msp, LAYER_DIMENSIONS, "DIMENSION")
        assert len(dims) >= 2

    def test_ridge_height_dimension_for_gable(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        dims = _entities_on_layer(msp, LAYER_DIMENSIONS, "DIMENSION")
        assert len(dims) >= 3

    def test_no_ridge_height_dimension_for_flat(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        dims = _entities_on_layer(msp, LAYER_DIMENSIONS, "DIMENSION")
        assert len(dims) == 2

    def test_overhang_dimension_present(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30, overhang="0.5m")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        dims = _entities_on_layer(msp, LAYER_DIMENSIONS, "DIMENSION")
        assert len(dims) >= 4

    def test_text_labels_present(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        texts = _entities_on_layer(msp, LAYER_LABELS, "TEXT")
        text_contents = [t.dxf.text for t in texts]
        assert any("Width: 10m" in t for t in text_contents)
        assert any("Depth: 15m" in t for t in text_contents)
        assert any("Ridge Height:" in t for t in text_contents)

    def test_flat_no_ridge_height_text(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        texts = _entities_on_layer(msp, LAYER_LABELS, "TEXT")
        text_contents = [t.dxf.text for t in texts]
        assert not any("Ridge Height:" in t for t in text_contents)


class TestLabelsLayer:
    def test_labels_layer_exists(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer_names = [l.dxf.name for l in doc.layers]
        assert LAYER_LABELS in layer_names

    def test_labels_layer_rgb(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer = doc.layers.get(LAYER_LABELS)
        assert layer.rgb == (218, 165, 32)

    def test_labels_text_on_labels_layer(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        texts = _entities_on_layer(msp, LAYER_LABELS, "TEXT")
        assert len(texts) >= 2


class TestLumberSpecsLayer:
    def test_lumber_specs_layer_exists(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer_names = [l.dxf.name for l in doc.layers]
        assert LAYER_LUMBER_SPECS in layer_names

    def test_lumber_specs_layer_rgb(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer = doc.layers.get(LAYER_LUMBER_SPECS)
        assert layer.rgb == (128, 0, 128)

    def test_lumber_specs_mtext_content(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        mtexts = _entities_on_layer(msp, LAYER_LUMBER_SPECS, "MTEXT")
        assert len(mtexts) >= 3
        contents = [m.text for m in mtexts]
        assert any("C24" in c for c in contents)
        assert any("45 mm" in c for c in contents)
        assert any("120 mm" in c for c in contents)


@pytest.mark.skip(reason="Title_Block layer is disabled in dxf_builder.py")
class TestTitleBlock:
    def test_rectangle_lines(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", buildingType="House", location="Bratislava")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TITLE_BLOCK, "LINE")
        assert len(lines) == 4

    def test_mtext_content_populated(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", buildingType="House", location="Bratislava")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        mtexts = _entities_on_layer(msp, LAYER_TITLE_BLOCK, "MTEXT")
        assert len(mtexts) == 5
        contents = [mtext.text for mtext in mtexts]
        assert any("House" in c for c in contents)
        assert any("Bratislava" in c for c in contents)
        assert any("10x15m" in c for c in contents)
        assert any("Gable" in c for c in contents)
        assert any("Date:" in c for c in contents)

    def test_none_fields_use_defaults(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        mtexts = _entities_on_layer(msp, LAYER_TITLE_BLOCK, "MTEXT")
        contents = [mtext.text for mtext in mtexts]
        assert any("Building" in c for c in contents)
        assert any("Location not specified" in c for c in contents)


class TestLayerRgbColors:
    def test_floor_plan_rgb(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer = doc.layers.get(LAYER_FLOOR_PLAN)
        assert layer.rgb == (128, 128, 128)

    def test_roof_outline_rgb(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer = doc.layers.get(LAYER_ROOF_OUTLINE)
        assert layer.rgb == (70, 130, 180)

    def test_trusses_rgb(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer = doc.layers.get(LAYER_TRUSSES)
        assert layer.rgb == (139, 90, 43)

    def test_dimensions_rgb(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer = doc.layers.get(LAYER_DIMENSIONS)
        assert layer.rgb == (0, 0, 255)


class TestRoundTripAllRoofTypes:
    @pytest.mark.parametrize("roof_type", ["Gable", "Hip", "Mono-pitch", "Flat"])
    def test_all_five_layers_present(self, roof_type):
        params = _params(floorPlanDimensions="10x15m", roofType=roof_type, roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer_names = {l.dxf.name for l in doc.layers}
        assert _ALL_FIVE_LAYERS <= layer_names

    @pytest.mark.parametrize("roof_type", ["Gable", "Hip", "Mono-pitch", "Flat"])
    def test_valid_dxf_round_trip(self, roof_type):
        params = _params(floorPlanDimensions="10x15m", roofType=roof_type, roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        assert doc.dxfversion == "AC1018"
        msp = doc.modelspace()
        all_entities = list(msp)
        assert len(all_entities) > 0


_GENERATED_DIR = Path(__file__).resolve().parent.parent / "generated"

_EXAMPLE_CONFIGS = [
    ("gable", "10x15m", "Gable", 30),
    ("hip", "10x15m", "Hip", 30),
    ("mono-pitch", "10x15m", "Mono-pitch", 15),
    ("flat", "10x15m", "Flat", 0),
    ("decimal", "8.5x12.3m", "Gable", 35),
]


class TestGenerateExampleFiles:
    @pytest.mark.parametrize("name,dims,roof,pitch", _EXAMPLE_CONFIGS, ids=[c[0] for c in _EXAMPLE_CONFIGS])
    def test_write_example_dxf(self, name, dims, roof, pitch):
        _GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        params = _params(floorPlanDimensions=dims, roofType=roof, roofPitch=pitch)
        result = build_dxf(params)
        doc = _read_dxf(result)
        assert doc.dxfversion == "AC1018"
        layer_names = {l.dxf.name for l in doc.layers}
        assert _ALL_FIVE_LAYERS <= layer_names
        out_path = _GENERATED_DIR / f"{name}.dxf"
        out_path.write_bytes(result)
