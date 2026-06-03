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
    _to_iso,
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
    def test_10x15m_floor_plan_line_count(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_FLOOR_PLAN, "LINE")
        assert len(lines) == 12

    def test_decimal_dimensions_line_count(self):
        params = _params(floorPlanDimensions="8.5x12.3m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_FLOOR_PLAN, "LINE")
        assert len(lines) == 12

    def test_isometric_projected_bottom_ring(self):
        w, d = 10000.0, 15000.0
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_FLOOR_PLAN, "LINE")
        from dxf_builder import WALL_HEIGHT
        bottom_corners_2d = [
            _to_iso(0, 0, 0),
            _to_iso(w, 0, 0),
            _to_iso(w, d, 0),
            _to_iso(0, d, 0),
        ]
        top_corners_2d = [
            _to_iso(0, 0, WALL_HEIGHT),
            _to_iso(w, 0, WALL_HEIGHT),
            _to_iso(w, d, WALL_HEIGHT),
            _to_iso(0, d, WALL_HEIGHT),
        ]
        bottom_set = {(round(x, 2), round(y, 2)) for x, y in bottom_corners_2d}
        top_set = {(round(x, 2), round(y, 2)) for x, y in top_corners_2d}
        bottom_ring = []
        top_ring = []
        vertical = []
        for l in lines:
            s = (round(l.dxf.start.x, 2), round(l.dxf.start.y, 2))
            e = (round(l.dxf.end.x, 2), round(l.dxf.end.y, 2))
            s_in_bot = s in bottom_set
            e_in_bot = e in bottom_set
            s_in_top = s in top_set
            e_in_top = e in top_set
            if s_in_bot and e_in_bot:
                bottom_ring.append(l)
            elif s_in_top and e_in_top:
                top_ring.append(l)
            else:
                vertical.append(l)
        assert len(bottom_ring) == 4, f"Expected 4 bottom ring lines, got {len(bottom_ring)}"
        assert len(top_ring) == 4, f"Expected 4 top ring lines, got {len(top_ring)}"
        assert len(vertical) == 4, f"Expected 4 vertical lines, got {len(vertical)}"
        drawn_bottom = set()
        for l in bottom_ring:
            drawn_bottom.add((round(l.dxf.start.x, 2), round(l.dxf.start.y, 2)))
            drawn_bottom.add((round(l.dxf.end.x, 2), round(l.dxf.end.y, 2)))
        assert drawn_bottom == bottom_set

    def test_isometric_projected_top_ring(self):
        w, d = 10000.0, 15000.0
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_FLOOR_PLAN, "LINE")
        from dxf_builder import WALL_HEIGHT
        top_corners_2d = [
            _to_iso(0, 0, WALL_HEIGHT),
            _to_iso(w, 0, WALL_HEIGHT),
            _to_iso(w, d, WALL_HEIGHT),
            _to_iso(0, d, WALL_HEIGHT),
        ]
        top_set = {(round(x, 2), round(y, 2)) for x, y in top_corners_2d}
        top_ring = [
            l for l in lines
            if (round(l.dxf.start.x, 2), round(l.dxf.start.y, 2)) in top_set
            and (round(l.dxf.end.x, 2), round(l.dxf.end.y, 2)) in top_set
        ]
        assert len(top_ring) == 4

    def test_isometric_vertical_lines_connect_rings(self):
        w, d = 10000.0, 15000.0
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_FLOOR_PLAN, "LINE")
        from dxf_builder import WALL_HEIGHT
        corners_3d = [(0, 0), (w, 0), (w, d), (0, d)]
        for cx, cy in corners_3d:
            bot = _to_iso(cx, cy, 0)
            top = _to_iso(cx, cy, WALL_HEIGHT)
            found = False
            for l in lines:
                sx, sy = l.dxf.start.x, l.dxf.start.y
                ex, ey = l.dxf.end.x, l.dxf.end.y
                if (abs(sx - bot[0]) < 0.1 and abs(sy - bot[1]) < 0.1
                        and abs(ex - top[0]) < 0.1 and abs(ey - top[1]) < 0.1):
                    found = True
                    break
                if (abs(sx - top[0]) < 0.1 and abs(sy - top[1]) < 0.1
                        and abs(ex - bot[0]) < 0.1 and abs(ey - bot[1]) < 0.1):
                    found = True
                    break
            assert found, f"Vertical line at corner ({cx},{cy}) not found"

    def test_isometric_centerlines_projected(self):
        w, d = 10000.0, 15000.0
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        polys = _entities_on_layer(msp, LAYER_WALL_CENTERLINES, "LWPOLYLINE")
        assert len(polys) == 1
        verts = _lwpolyline_vertices(polys[0])
        expected = [
            _to_iso(0, 0, 0),
            _to_iso(w, 0, 0),
            _to_iso(w, d, 0),
            _to_iso(0, d, 0),
        ]
        for v, e in zip(verts, expected):
            assert abs(v[0] - e[0]) < 0.1
            assert abs(v[1] - e[1]) < 0.1


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
        w, d = 10000.0, 15000.0
        pitch = 30.0
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=pitch)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) == 5
        ridge_h = (min(w, d) / 2) * math.tan(pitch * math.pi / 180)
        z_ridge = 2700 + ridge_h
        ridge_s = _to_iso(w / 2, 0, z_ridge)
        ridge_e = _to_iso(w / 2, d, z_ridge)
        peak = _to_iso(w / 2, d / 2, z_ridge)
        rs = (round(ridge_s[0], 2), round(ridge_s[1], 2))
        re_ = (round(ridge_e[0], 2), round(ridge_e[1], 2))
        ridge_found = False
        for line in lines:
            s = (round(line.dxf.start.x, 2), round(line.dxf.start.y, 2))
            e = (round(line.dxf.end.x, 2), round(line.dxf.end.y, 2))
            if (s == rs and e == re_) or (s == re_ and e == rs):
                ridge_found = True
        assert ridge_found, "Ridge line not found at projected coordinates"
        peak_pt = (round(peak[0], 2), round(peak[1], 2))
        rafter_count = sum(
            1 for l in lines
            if (round(l.dxf.start.x, 2), round(l.dxf.start.y, 2)) == peak_pt
            or (round(l.dxf.end.x, 2), round(l.dxf.end.y, 2)) == peak_pt
        )
        assert rafter_count == 4


class TestHipRoof:
    def test_hip_roof_outline(self):
        w, d = 10000.0, 15000.0
        pitch = 30.0
        params = _params(floorPlanDimensions="10x15m", roofType="Hip", roofPitch=pitch)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) == 5
        ridge_h = (min(w, d) / 2) * math.tan(pitch * math.pi / 180)
        z_ridge = 2700 + ridge_h
        ridge_len = d - w
        ry_start_2d = _to_iso(w / 2, (d - ridge_len) / 2, z_ridge)
        ry_end_2d = _to_iso(w / 2, (d + ridge_len) / 2, z_ridge)
        rs = (round(ry_start_2d[0], 2), round(ry_start_2d[1], 2))
        re_ = (round(ry_end_2d[0], 2), round(ry_end_2d[1], 2))
        ridge_lines = []
        hip_lines = []
        for line in lines:
            s = (round(line.dxf.start.x, 2), round(line.dxf.start.y, 2))
            e = (round(line.dxf.end.x, 2), round(line.dxf.end.y, 2))
            if (s == rs and e == re_) or (s == re_ and e == rs):
                ridge_lines.append(line)
            else:
                hip_lines.append(line)
        assert len(ridge_lines) == 1
        assert len(hip_lines) == 4
        eave_corners_2d = [
            (round(p[0], 2), round(p[1], 2))
            for p in [_to_iso(0, 0, 2700), _to_iso(w, 0, 2700), _to_iso(0, d, 2700), _to_iso(w, d, 2700)]
        ]
        for hl in hip_lines:
            s = (round(hl.dxf.start.x, 2), round(hl.dxf.start.y, 2))
            e = (round(hl.dxf.end.x, 2), round(hl.dxf.end.y, 2))
            connects_ridge = s == rs or s == re_ or e == rs or e == re_
            connects_eave = s in eave_corners_2d or e in eave_corners_2d
            assert connects_ridge and connects_eave


class TestMonoPitchRoof:
    def test_mono_pitch_roof_outline(self):
        params = _params(floorPlanDimensions="10x15m", roofType="Mono-pitch")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) >= 4
        w, d = 10000.0, 15000.0
        ridge_h = w * math.tan(10 * math.pi / 180)
        z_low = 2700
        z_high = 2700 + ridge_h
        expected_pts = {
            (round(p[0], 2), round(p[1], 2))
            for p in [
                _to_iso(0, 0, z_low), _to_iso(w, 0, z_high),
                _to_iso(w, d, z_high), _to_iso(0, d, z_low),
            ]
        }
        drawn_pts = set()
        for l in lines:
            drawn_pts.add((round(l.dxf.start.x, 2), round(l.dxf.start.y, 2)))
            drawn_pts.add((round(l.dxf.end.x, 2), round(l.dxf.end.y, 2)))
        assert expected_pts <= drawn_pts

    def test_mono_pitch_2d_projected_slope(self):
        w, d = 10000.0, 15000.0
        pitch = 10.0
        params = _params(floorPlanDimensions="10x15m", roofType="Mono-pitch", roofPitch=pitch)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        low_pt = _to_iso(0, 0, 2700)
        high_pt = _to_iso(w, 0, 2700 + w * math.tan(pitch * math.pi / 180))
        low_2d = (round(low_pt[0], 2), round(low_pt[1], 2))
        high_2d = (round(high_pt[0], 2), round(high_pt[1], 2))
        slope_found = False
        for l in lines:
            s = (round(l.dxf.start.x, 2), round(l.dxf.start.y, 2))
            e = (round(l.dxf.end.x, 2), round(l.dxf.end.y, 2))
            if (s == low_2d and e == high_2d) or (s == high_2d and e == low_2d):
                slope_found = True
        assert slope_found


class TestFlatRoof:
    def test_flat_roof_outline(self):
        w, d = 10000.0, 15000.0
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_ROOF_OUTLINE, "LINE")
        assert len(lines) == 4
        expected_pts = {
            (round(p[0], 2), round(p[1], 2))
            for p in [
                _to_iso(0, 0, 2700), _to_iso(w, 0, 2700),
                _to_iso(w, d, 2700), _to_iso(0, d, 2700),
            ]
        }
        drawn_pts = set()
        for line in lines:
            drawn_pts.add((round(line.dxf.start.x, 2), round(line.dxf.start.y, 2)))
            drawn_pts.add((round(line.dxf.end.x, 2), round(line.dxf.end.y, 2)))
        assert drawn_pts == expected_pts


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

    def test_first_truss_projected_coordinates(self):
        w, d = 10000.0, 15000.0
        params = _params(floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        first_y = w * 0.05
        ridge_h = (w / 2) * math.tan(30 * math.pi / 180)
        z_eave = 2700
        z_ridge = z_eave + ridge_h
        expected_starts = {
            (round(p[0], 2), round(p[1], 2))
            for p in [
                _to_iso(0, first_y, z_eave),
                _to_iso(w, first_y, z_eave),
            ]
        }
        drawn_starts = set()
        for l in lines:
            drawn_starts.add((round(l.dxf.start.x, 2), round(l.dxf.start.y, 2)))
        assert expected_starts <= drawn_starts

    def test_triangle_shape_projected(self):
        w = 10000.0
        params = _params(floorPlanDimensions="10x10m", roofType="Gable", roofPitch=30)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        first_y = min(w, w) * 0.05
        ridge_h = (w / 2) * math.tan(30 * math.pi / 180)
        z_eave = 2700
        z_ridge = z_eave + ridge_h
        left_eave = (round(_to_iso(0, first_y, z_eave)[0], 2), round(_to_iso(0, first_y, z_eave)[1], 2))
        right_eave = (round(_to_iso(w, first_y, z_eave)[0], 2), round(_to_iso(w, first_y, z_eave)[1], 2))
        ridge = (round(_to_iso(w / 2, first_y, z_ridge)[0], 2), round(_to_iso(w / 2, first_y, z_ridge)[1], 2))
        truss_segs = [
            l for l in lines
            if (round(l.dxf.start.x, 2), round(l.dxf.start.y, 2)) in (left_eave, right_eave, ridge)
            or (round(l.dxf.end.x, 2), round(l.dxf.end.y, 2)) in (left_eave, right_eave, ridge)
        ]
        assert len(truss_segs) >= 3


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

    def test_right_triangle_shape_projected(self):
        w, d = 10000.0, 15000.0
        params = _params(floorPlanDimensions="10x15m", roofType="Mono-pitch", roofPitch=10)
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        shorter = min(w, d)
        first_y = shorter * 0.05
        ridge_h = w * math.tan(10 * math.pi / 180)
        z_eave = 2700
        z_ridge = z_eave + ridge_h
        left_eave = _to_iso(0, first_y, z_eave)
        right_eave = _to_iso(w, first_y, z_eave)
        right_ridge = _to_iso(w, first_y, z_ridge)
        left_2d = (round(left_eave[0], 2), round(left_eave[1], 2))
        right_eave_2d = (round(right_eave[0], 2), round(right_eave[1], 2))
        right_ridge_2d = (round(right_ridge[0], 2), round(right_ridge[1], 2))
        slope_found = False
        for l in lines:
            s = (round(l.dxf.start.x, 2), round(l.dxf.start.y, 2))
            e = (round(l.dxf.end.x, 2), round(l.dxf.end.y, 2))
            if (s == left_2d and e == right_ridge_2d) or (s == right_ridge_2d and e == left_2d):
                slope_found = True
        assert slope_found


class TestTrussCrossSectionFlat:
    def test_truss_layer_has_projected_lines(self):
        w, d = 10000.0, 15000.0
        params = _params(floorPlanDimensions="10x15m", roofType="Flat")
        result = build_dxf(params)
        doc = _read_dxf(result)
        msp = doc.modelspace()
        lines = _entities_on_layer(msp, LAYER_TRUSSES, "LINE")
        count = _compute_truss_count(10, 15)
        assert len(lines) == count
        z_eave = 2700
        first_y = min(w, d) * 0.05
        expected_start = (round(_to_iso(0, first_y, z_eave)[0], 2), round(_to_iso(0, first_y, z_eave)[1], 2))
        expected_end = (round(_to_iso(w, first_y, z_eave)[0], 2), round(_to_iso(w, first_y, z_eave)[1], 2))
        first_line_found = False
        for line in lines:
            s = (round(line.dxf.start.x, 2), round(line.dxf.start.y, 2))
            e = (round(line.dxf.end.x, 2), round(line.dxf.end.y, 2))
            if (s == expected_start and e == expected_end) or (s == expected_end and e == expected_start):
                first_line_found = True
        assert first_line_found


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
