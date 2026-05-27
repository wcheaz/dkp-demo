import sys
from io import BytesIO, StringIO
from types import SimpleNamespace

import ezdxf
import pytest

sys.path.insert(0, "agent/src")
from dxf_builder import build_dxf, LAYER_FLOOR_PLAN, LAYER_ROOF_OUTLINE


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
        assert doc.dxfversion == "AC1015"

    def test_layers_exist(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        layer_names = [l.dxf.name for l in doc.layers]
        assert LAYER_FLOOR_PLAN in layer_names
        assert LAYER_ROOF_OUTLINE in layer_names


class TestFloorPlanOutline:
    def test_10x15m_floor_plan(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        polys = _entities_on_layer(msp, LAYER_FLOOR_PLAN, "LWPOLYLINE")
        assert len(polys) == 1
        verts = _lwpolyline_vertices(polys[0])
        expected = [(0, 0), (10000, 0), (10000, 15000), (0, 15000)]
        for v, e in zip(verts, expected):
            assert abs(v[0] - e[0]) < 0.01
            assert abs(v[1] - e[1]) < 0.01

    def test_decimal_dimensions(self):
        params = _params(floorPlanDimensions="8.5x12.3m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        polys = _entities_on_layer(msp, LAYER_FLOOR_PLAN, "LWPOLYLINE")
        assert len(polys) == 1
        verts = _lwpolyline_vertices(polys[0])
        expected = [(0, 0), (8500, 0), (8500, 12300), (0, 12300)]
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
        params = _params(floorPlanDimensions="10x15m", roofType="Gable")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) >= 1
        ridge_found = False
        for line in lines:
            start = (line.dxf.start.x, line.dxf.start.y)
            end = (line.dxf.end.x, line.dxf.end.y)
            if abs(start[0] - 5000) < 0.01 and abs(end[0] - 5000) < 0.01:
                ridge_found = True
        assert ridge_found, "Ridge line at x=5000 not found"


class TestHipRoof:
    def test_hip_roof_outline(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Hip")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) == 5
        ridge_lines = []
        hip_lines = []
        for line in lines:
            s = (line.dxf.start.x, line.dxf.start.y)
            e = (line.dxf.end.x, line.dxf.end.y)
            if abs(s[0] - 5000) < 0.01 and abs(e[0] - 5000) < 0.01:
                ridge_len = abs(e[1] - s[1])
                ridge_lines.append(ridge_len)
            else:
                hip_lines.append((s, e))
        assert len(ridge_lines) == 1
        assert abs(ridge_lines[0] - 5000) < 0.01
        assert len(hip_lines) == 4


class TestMonoPitchRoof:
    def test_mono_pitch_roof_outline(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Mono-pitch")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        polys = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LWPOLYLINE")
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(polys) == 1
        assert len(lines) >= 1


class TestFlatRoof:
    def test_flat_roof_outline(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        polys = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LWPOLYLINE")
        assert len(polys) == 1
        verts = _lwpolyline_vertices(polys[0])
        expected = [(0, 0), (10000, 0), (10000, 15000), (0, 15000)]
        for v, e in zip(verts, expected):
            assert abs(v[0] - e[0]) < 0.01
            assert abs(v[1] - e[1]) < 0.01


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
        assert doc.dxfversion == "AC1015"

    def test_case_insensitive_flat(self):
        params = _params(floorPlanDimensions="10x15m", roofType="FLAT")
        result = build_dxf(params)
        doc = _read_dxf(result)
        assert doc.dxfversion == "AC1015"
