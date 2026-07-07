import math
import sys
import xml.etree.ElementTree as ET
from types import SimpleNamespace

import pytest

sys.path.insert(0, "agent/src")
from geometry_solver import parse_overhang  # type: ignore[import-not-found]  # noqa: E402
from mxf_builder import (  # type: ignore[import-not-found]  # noqa: E402
    WALL_HEIGHT,
    WALL_THICKNESS,
    build_mxf,
    wall_specs,
)


def _params(**kwargs):
    return SimpleNamespace(**kwargs)


def _parse(result: bytes):
    return ET.fromstring(result)


def _parse_point(text: str) -> tuple[float, float, float]:
    parts = [float(p) for p in text.split(",")]
    return (parts[0], parts[1], parts[2])


def _parse_polygon(text: str) -> list[tuple[float, float]]:
    return [
        (float(point.split(",")[0]), float(point.split(",")[1]))
        for point in text.split(" ")
    ]


class TestMxfGenerationSuccess:
    def test_mxf_generation_success(self):
        params = _params(floorPlanDimensions="10x6m", buildingType="Test")
        result = build_mxf(params)

        assert result.startswith(b"<?xml version=\"1.0\" encoding=\"utf-8\"?>")

        root = _parse(result)
        assert root.tag == "Mxf"
        assert root.attrib["version"] == "MXF Version 5.11"
        assert root.attrib["batchName"] == "Test"

        building_walls = root.findall(".//BuildingWall")
        walls = root.findall(".//Wall")
        assert len(building_walls) == 4
        assert len(walls) == 4
        assert [w.attrib["wall_ID"] for w in building_walls] == [
            "W0", "W1", "W2", "W3",
        ]
        assert [w.attrib["id"] for w in walls] == ["W0", "W1", "W2", "W3"]

        # Document must be re-parseable and contain the required top-level lists.
        for tag in ("BuildingList", "WallList", "JobList", "CustomerList"):
            assert root.find(tag) is not None


class TestCoordinateCalculation:
    def test_wall_origins_match_plan_corners(self):
        # 10x6m plan -> corners (0,0),(10,0),(10,6),(0,6)
        specs = wall_specs(10.0, 6.0)
        expected_origins = [
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (10.0, 6.0, 0.0),
            (0.0, 6.0, 0.0),
        ]
        assert [s["origin"] for s in specs] == expected_origins

    def test_walls_form_closed_rectangle(self):
        # origin + length * running_direction must equal the next wall's origin.
        specs = wall_specs(10.0, 6.0)
        for i in range(4):
            spec = specs[i]
            ox, oy, oz = spec["origin"]
            rx, ry, rz = spec["run"]
            length = spec["length"]
            end = (ox + rx * length, oy + ry * length, oz + rz * length)
            next_origin = specs[(i + 1) % 4]["origin"]
            assert end == next_origin, (
                f"W{i} run end {end} does not reach W{(i + 1) % 4} origin {next_origin}"
            )

    def test_xml_running_axis_is_unit_direction(self):
        # The xAxis point is origin + unit running direction (per Pamir spec).
        params = _params(floorPlanDimensions="10x6m")
        root = _parse(build_mxf(params))
        specs = wall_specs(10.0, 6.0)
        for i, position in enumerate(root.findall(".//BuildingWall/Position")):
            origin = _parse_point(position.attrib["origin"])
            x_axis = _parse_point(position.attrib["xAxis"])
            direction = (
                round(x_axis[0] - origin[0], 6),
                round(x_axis[1] - origin[1], 6),
                round(x_axis[2] - origin[2], 6),
            )
            assert direction == specs[i]["run"], (
                f"W{i} running direction {direction} != {specs[i]['run']}"
            )

    def test_thickness_axes_point_inward(self):
        params = _params(floorPlanDimensions="10x6m")
        root = _parse(build_mxf(params))
        positions = root.findall(".//BuildingWall/Position")

        expected_inward = [
            (0.0, 1.0, 0.0),   # W0 bottom -> north
            (-1.0, 0.0, 0.0),  # W1 right  -> west
            (0.0, -1.0, 0.0),  # W2 top    -> south
            (1.0, 0.0, 0.0),   # W3 left   -> east
        ]
        for i, position in enumerate(positions):
            origin = _parse_point(position.attrib["origin"])
            z_axis = _parse_point(position.attrib["zAxis"])
            inward = (
                round(z_axis[0] - origin[0], 6),
                round(z_axis[1] - origin[1], 6),
                round(z_axis[2] - origin[2], 6),
            )
            assert inward == expected_inward[i], (
                f"W{i} thickness axis points {inward}, expected {expected_inward[i]}"
            )

    def test_vertical_axis_points_up(self):
        params = _params(floorPlanDimensions="10x6m")
        root = _parse(build_mxf(params))
        for position in root.findall(".//BuildingWall/Position"):
            origin = _parse_point(position.attrib["origin"])
            y_axis = _parse_point(position.attrib["yAxis"])
            assert round(y_axis[2] - origin[2], 6) == 1.0

    def test_wall_lengths_match_plan(self):
        # W0/W2 span the width (10m); W1/W3 span the depth (6m).
        specs = wall_specs(10.0, 6.0)
        assert [s["length"] for s in specs] == [10.0, 6.0, 10.0, 6.0]

    def test_decimal_dimensions_coordinates(self):
        specs = wall_specs(8.5, 12.3)
        assert specs[1]["origin"] == (8.5, 0.0, 0.0)
        assert specs[2]["origin"] == (8.5, 12.3, 0.0)
        assert specs[3]["origin"] == (0.0, 12.3, 0.0)


class TestSkinPolygons:
    def test_front_face_spans_full_length(self):
        params = _params(floorPlanDimensions="10x6m")
        root = _parse(build_mxf(params))
        for wall in root.findall(".//Wall"):
            face = wall.find("./SkinList/Skin/FrontFace/Face")
            assert face.attrib["z"] == "0"
            polygon = _parse_polygon(face.attrib["polygon"])
            xs = [p[0] for p in polygon]
            assert min(xs) == 0.0
            assert max(xs) == pytest.approx(10.0) or max(xs) == pytest.approx(6.0)
            heights = [p[1] for p in polygon]
            assert min(heights) == 0.0
            assert max(heights) == pytest.approx(WALL_HEIGHT)

    def test_back_face_shortened_by_thickness(self):
        params = _params(floorPlanDimensions="10x6m")
        root = _parse(build_mxf(params))
        for wall in root.findall(".//Wall"):
            length = 10.0 if wall.attrib["id"] in ("W0", "W2") else 6.0
            face = wall.find("./SkinList/Skin/BackFace/Face")
            assert face.attrib["z"] == f"{WALL_THICKNESS:g}"
            polygon = _parse_polygon(face.attrib["polygon"])
            xs = [p[0] for p in polygon]
            assert min(xs) == pytest.approx(WALL_THICKNESS)
            assert max(xs) == pytest.approx(length - WALL_THICKNESS)

    def test_overall_thickness_attribute(self):
        params = _params(floorPlanDimensions="10x6m")
        root = _parse(build_mxf(params))
        for wall in root.findall(".//Wall"):
            assert wall.attrib["overallThickness"] == f"{WALL_THICKNESS:g}"
            skin = wall.find("./SkinList/Skin")
            assert skin.attrib["thickness"] == f"{WALL_THICKNESS:g}"
            assert skin.attrib["id"] == f"{wall.attrib['id']}_S0"


class TestWallPlateList:
    def test_wall_plate_list_under_every_wall(self):
        params = _params(floorPlanDimensions="10x6m", buildingType="Test")
        root = _parse(build_mxf(params))

        walls = root.findall(".//Wall")
        assert len(walls) == 4
        for wall in walls:
            plate_list = wall.find("./WallPlateList")
            assert plate_list is not None, (
                f"Wall {wall.attrib['id']} is missing a WallPlateList"
            )
            plate = plate_list.find("./WallPlate")
            assert plate is not None, (
                f"Wall {wall.attrib['id']} WallPlateList has no WallPlate"
            )
            assert plate.attrib["offset"] == "0.05"
            assert plate.attrib["height"] == "0.05"
            assert plate.attrib["width"] == "0.1"

    def test_wall_plate_list_is_sibling_of_skin_list(self):
        params = _params(floorPlanDimensions="10x6m")
        root = _parse(build_mxf(params))

        for wall in root.findall(".//Wall"):
            child_tags = [child.tag for child in wall]
            assert "SkinList" in child_tags
            assert "WallPlateList" in child_tags
            assert child_tags.index("SkinList") < child_tags.index("WallPlateList"), (
                f"Wall {wall.attrib['id']}: WallPlateList must follow SkinList"
            )


class TestInvalidDimensions:
    def test_mxf_generation_invalid_dimensions(self):
        params = _params(floorPlanDimensions=None)
        with pytest.raises(ValueError):
            build_mxf(params)

    def test_malformed_dimensions_raises(self):
        params = _params(floorPlanDimensions="about twenty meters")
        with pytest.raises(ValueError):
            build_mxf(params)

    def test_non_positive_dimensions_raises(self):
        params = _params(floorPlanDimensions="0x10m")
        with pytest.raises(ValueError):
            build_mxf(params)


class TestOverhangParsing:
    """parse_overhang exposes numeric millimetre values for the overhang param."""

    def test_overhang_parsing(self):
        # Raw number stays as-is (millimetres); "m" suffix converts to mm.
        assert parse_overhang(250) == 250.0
        assert parse_overhang("250mm") == 250.0
        assert parse_overhang("0.5m") == 500.0
        assert parse_overhang(None) is None

    def test_overhang_parsing_none_returns_none(self):
        assert parse_overhang(None) is None

    def test_overhang_parsing_plain_number(self):
        assert parse_overhang("250") == 250.0
        assert parse_overhang(300) == 300.0
        assert parse_overhang(0.0) == 0.0

    def test_overhang_parsing_mm_suffix(self):
        assert parse_overhang("250mm") == 250.0
        assert parse_overhang("250 mm") == 250.0
        assert parse_overhang("250MM") == 250.0
        assert parse_overhang("  450mm  ") == 450.0

    def test_overhang_parsing_metres_suffix(self):
        assert parse_overhang("0.5m") == 500.0
        assert parse_overhang("1m") == 1000.0
        assert parse_overhang("1.2 m") == 1200.0

    def test_overhang_parsing_invalid_returns_none(self):
        assert parse_overhang("abc") is None
        assert parse_overhang("") is None
        assert parse_overhang("twenty mm") is None


class TestFlatRoofSurfaces:
    """Flat roof and floor surface generation (roofType="Flat")."""

    def _build_root(self, **overrides):
        defaults = {
            "floorPlanDimensions": "10x15m",
            "roofType": "Flat",
            "roofPitch": 0,
            "overhang": "0.5m",
        }
        defaults.update(overrides)
        return _parse(build_mxf(_params(**defaults)))

    def test_flat_roof_generation(self):
        # Spec scenario: 10x15m, Flat, pitch 0, overhang 0.5m.
        root = self._build_root()

        roof_ids = [r.attrib["surfaceID"] for r in root.findall(".//RoofList/Roof")]
        floor_ids = [f.attrib["surfaceID"] for f in root.findall(".//FloorList/Floor")]
        assert roof_ids == ["SR0-0"]
        assert floor_ids == ["SF0-0"]

        # RoofList/FloorList live inside <Building>, SurfaceList at the root.
        assert root.find(".//Building/RoofList") is not None
        assert root.find(".//Building/FloorList") is not None
        assert root.find("SurfaceList") is not None

    def test_flat_roof_surface_polygon_matches_spec(self):
        root = self._build_root()
        sr0 = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        assert sr0 is not None
        assert sr0.attrib["covering"] == "undefined"
        expected = (
            "-0.5,-0.5,3.12 10.5,-0.5,3.12 10.5,15.5,3.12 "
            "-0.5,15.5,3.12 -0.5,-0.5,3.12"
        )
        assert sr0.attrib["polygon"] == expected

    def test_flat_floor_surface_polygon_matches_spec(self):
        # Floor maps the building footprint at Z=0 (no overhang).
        root = self._build_root()
        sf0 = root.find('.//SurfaceList/Surface[@id="SF0-0"]')
        assert sf0 is not None
        assert sf0.attrib["verticalOffset"] == "0"
        assert sf0.attrib["polygon"] == "0,0,0 10,0,0 10,15,0 0,15,0 0,0,0"

    def test_flat_roof_is_horizontal_at_eaves_baseline(self):
        # Zero pitch: every Z coordinate on the roof surface equals the anchored
        # eaves baseline of 3.12 m.
        root = self._build_root()
        sr0 = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        zs = [float(p.split(",")[2]) for p in sr0.attrib["polygon"].split(" ")]
        assert all(z == pytest.approx(3.12) for z in zs)

    def test_flat_roof_overhang_expands_footprint(self):
        # 10x15 plan + 0.5m overhang => roof spans 11 x 16.
        root = self._build_root()
        sr0 = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        pts = [
            (float(p.split(",")[0]), float(p.split(",")[1]))
            for p in sr0.attrib["polygon"].split(" ")
        ]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        assert min(xs) == pytest.approx(-0.5)
        assert max(xs) == pytest.approx(10.5)
        assert min(ys) == pytest.approx(-0.5)
        assert max(ys) == pytest.approx(15.5)

    def test_flat_roof_defaults_when_roof_type_missing(self):
        # Without roofType the generator falls back to a flat roof.
        root = self._build_root(roofType=None, overhang=None)
        sr0 = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        assert sr0 is not None
        # No overhang => roof exactly covers the 10x15 footprint at Z=3.12.
        assert sr0.attrib["polygon"] == "0,0,3.12 10,0,3.12 10,15,3.12 0,15,3.12 0,0,3.12"


class TestMonopitchRoofSurfaces:
    """Mono-pitch (single-slope) roof surface generation (roofType="Mono-pitch")."""

    _WIDTH = 10.0
    _DEPTH = 15.0
    _PITCH = 18.0
    _OVERHANG_M = 0.5
    _Z_EAVES = 3.12

    def _build_root(self, **overrides):
        defaults = {
            "floorPlanDimensions": "10x15m",
            "roofType": "Mono-pitch",
            "roofPitch": 18,
            "overhang": "0.5m",
        }
        defaults.update(overrides)
        return _parse(build_mxf(_params(**defaults)))

    def _expected_z(self):
        rise = math.tan(math.radians(self._PITCH))
        z_eaves = self._Z_EAVES
        z_ridge = z_eaves + (self._WIDTH + self._OVERHANG_M) * rise
        return z_eaves, z_ridge

    def test_monopitch_roof_generation(self):
        # One roof surface (SR0-0) emitted under Building/RoofList + root SurfaceList.
        root = self._build_root()
        roof_ids = [r.attrib["surfaceID"] for r in root.findall(".//RoofList/Roof")]
        assert roof_ids == ["SR0-0"]
        floor_ids = [f.attrib["surfaceID"] for f in root.findall(".//FloorList/Floor")]
        assert floor_ids == ["SF0-0"]
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        assert surface is not None
        assert surface.attrib["covering"] == "undefined"

    def test_monopitch_surface_polygon_xy_matches_footprint(self):
        # Eaves side at X=-overhang, ridge side at X=W; Y overhangs both ends.
        root = self._build_root()
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        pts = [
            (float(p.split(",")[0]), float(p.split(",")[1]))
            for p in surface.attrib["polygon"].split(" ")
        ]
        assert pts[0] == pytest.approx((-0.5, -0.5))
        assert pts[1] == pytest.approx((10.0, -0.5))
        assert pts[2] == pytest.approx((10.0, 15.5))
        assert pts[3] == pytest.approx((-0.5, 15.5))
        assert pts[4] == pytest.approx((-0.5, -0.5))  # closing point

    def test_monopitch_eaves_and_ridge_heights_match_spec(self):
        # Z_eaves = 3.12 (anchored); Z_ridge = 3.12 + (W + O) * tan(theta).
        root = self._build_root()
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        zs = [float(p.split(",")[2]) for p in surface.attrib["polygon"].split(" ")]
        z_eaves, z_ridge = self._expected_z()
        # Low (eaves) corners share Z_eaves; high (ridge) corners share Z_ridge.
        assert zs[0] == pytest.approx(z_eaves)
        assert zs[3] == pytest.approx(z_eaves)
        assert zs[4] == pytest.approx(z_eaves)  # closing point
        assert zs[1] == pytest.approx(z_ridge)
        assert zs[2] == pytest.approx(z_ridge)
        # Eaves sits at the anchored eaves baseline; ridge rises above it.
        assert z_eaves == pytest.approx(self._Z_EAVES)
        assert z_ridge > self._Z_EAVES

    def test_monopitch_slope_matches_pitch(self):
        # rise/run between the eaves edge and ridge edge == tan(pitch).
        root = self._build_root()
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        pts = [p.split(",") for p in surface.attrib["polygon"].split(" ")]
        run = float(pts[1][0]) - float(pts[0][0])
        rise = float(pts[1][2]) - float(pts[0][2])
        assert rise / run == pytest.approx(math.tan(math.radians(self._PITCH)))

    def test_monopitch_zero_overhang(self):
        # No overhang: low edge sits on the low wall (X=0, Z=z_eaves).
        root = self._build_root(overhang=None)
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        pts = [p.split(",") for p in surface.attrib["polygon"].split(" ")]
        assert float(pts[0][0]) == pytest.approx(0.0)             # low edge at X=0
        assert float(pts[0][2]) == pytest.approx(self._Z_EAVES)   # eaves = 3.12
        assert float(pts[1][0]) == pytest.approx(self._WIDTH)     # ridge at X=W
        z_ridge = self._Z_EAVES + self._WIDTH * math.tan(math.radians(self._PITCH))
        assert float(pts[1][2]) == pytest.approx(z_ridge)


class TestGableRoofSurfaces:
    """Gable (two-plane) roof surface generation (roofType="Gable")."""

    _WIDTH = 10.0
    _DEPTH = 15.0
    _PITCH = 30.0
    _OVERHANG_M = 0.5
    _Z_EAVES = 3.12

    def _build_root(self, **overrides):
        defaults = {
            "floorPlanDimensions": "10x15m",
            "roofType": "Gable",
            "roofPitch": 30,
            "overhang": "0.5m",
        }
        defaults.update(overrides)
        return _parse(build_mxf(_params(**defaults)))

    def _expected_z(self):
        rise = math.tan(math.radians(self._PITCH))
        run_ridge = min(self._WIDTH, self._DEPTH) / 2.0
        z_eaves = self._Z_EAVES
        z_ridge = z_eaves + (run_ridge + self._OVERHANG_M) * rise
        return z_eaves, z_ridge

    def test_gable_roof_generation(self):
        # Two roof surfaces (SR0-0, SR0-1) emitted under Building/RoofList
        # plus the root SurfaceList.
        root = self._build_root()
        roof_ids = [r.attrib["surfaceID"] for r in root.findall(".//RoofList/Roof")]
        floor_ids = [f.attrib["surfaceID"] for f in root.findall(".//FloorList/Floor")]
        assert roof_ids == ["SR0-0", "SR0-1"]
        assert floor_ids == ["SF0-0"]
        for sid in ("SR0-0", "SR0-1"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            assert surface is not None
            assert surface.attrib["covering"] == "undefined"

    def test_gable_floor_surface_polygon_matches_spec(self):
        root = self._build_root()
        sf0 = root.find('.//SurfaceList/Surface[@id="SF0-0"]')
        assert sf0 is not None
        assert sf0.attrib["polygon"] == "0,0,0 10,0,0 10,15,0 0,15,0 0,0,0"

    def test_gable_eaves_and_ridge_heights_match_spec(self):
        # Z_eaves = 3.12 (anchored); Z_ridge = 3.12 + (W/2 + O) * tan(theta).
        # Coordinates are serialized with ``:g`` (6 significant figures), so a
        # 1 mm tolerance accommodates the documented rounding (spec: = 3.12,
        # ≈ 6.295).
        root = self._build_root()
        z_eaves, z_ridge = self._expected_z()
        for sid in ("SR0-0", "SR0-1"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            zs = [float(p.split(",")[2]) for p in surface.attrib["polygon"].split(" ")]
            assert min(zs) == pytest.approx(z_eaves, abs=1e-3)
            assert max(zs) == pytest.approx(z_ridge, abs=1e-3)
        assert z_eaves == pytest.approx(self._Z_EAVES, abs=1e-3)
        assert z_ridge > self._Z_EAVES

    def test_gable_ridge_runs_along_depth_at_mid_width(self):
        # Ridge from (W/2, -overhang, Z_ridge) to (W/2, D+overhang, Z_ridge).
        root = self._build_root()
        _, z_ridge = self._expected_z()
        mid = self._WIDTH / 2.0
        ridge_xs = []
        ridge_ys = []
        for sid in ("SR0-0", "SR0-1"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            for p in surface.attrib["polygon"].split(" "):
                x, y, z = (float(v) for v in p.split(","))
                if z == pytest.approx(z_ridge):
                    ridge_xs.append(x)
                    ridge_ys.append(y)
        assert len(ridge_xs) >= 4  # two ridge endpoints per plane
        assert all(x == pytest.approx(mid) for x in ridge_xs)
        assert min(ridge_ys) == pytest.approx(-self._OVERHANG_M)
        assert max(ridge_ys) == pytest.approx(self._DEPTH + self._OVERHANG_M)

    def test_gable_surfaces_slope_matches_pitch(self):
        # rise/run between the eaves edge and ridge edge == tan(pitch).
        # Serialized coordinates use ``:g`` (6 sig figs), so allow 1e-3 slack.
        root = self._build_root()
        rise = math.tan(math.radians(self._PITCH))
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        pts = [p.split(",") for p in surface.attrib["polygon"].split(" ")]
        run = float(pts[1][0]) - float(pts[0][0])
        z_rise = float(pts[1][2]) - float(pts[0][2])
        assert z_rise / run == pytest.approx(rise, abs=1e-3)

    def test_gable_overhang_expands_footprint(self):
        # Combined roof spans X in [-0.5, 10.5], Y in [-0.5, 15.5].
        root = self._build_root()
        all_xs, all_ys = [], []
        for sid in ("SR0-0", "SR0-1"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            for p in surface.attrib["polygon"].split(" "):
                x, y, _ = (float(v) for v in p.split(","))
                all_xs.append(x)
                all_ys.append(y)
        assert min(all_xs) == pytest.approx(-self._OVERHANG_M)
        assert max(all_xs) == pytest.approx(self._WIDTH + self._OVERHANG_M)
        assert min(all_ys) == pytest.approx(-self._OVERHANG_M)
        assert max(all_ys) == pytest.approx(self._DEPTH + self._OVERHANG_M)

    def test_gable_zero_overhang(self):
        # No overhang: eaves sit on the outer walls (X=0 / X=W) at z_eaves.
        root = self._build_root(overhang=None)
        # Re-compute ridge without overhang: z_eaves + (run_ridge + 0) * rise.
        rise = math.tan(math.radians(self._PITCH))
        run_ridge = min(self._WIDTH, self._DEPTH) / 2.0
        z_ridge = self._Z_EAVES + run_ridge * rise
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        pts = [p.split(",") for p in surface.attrib["polygon"].split(" ")]
        assert float(pts[0][0]) == pytest.approx(0.0)        # low eaves at X=0
        assert float(pts[0][2]) == pytest.approx(self._Z_EAVES)
        surface_hi = root.find('.//SurfaceList/Surface[@id="SR0-1"]')
        pts_hi = [p.split(",") for p in surface_hi.attrib["polygon"].split(" ")]
        assert float(pts_hi[1][0]) == pytest.approx(self._WIDTH)  # high eaves at X=W
        assert float(pts_hi[1][2]) == pytest.approx(self._Z_EAVES)
        # Ridge points reach z_ridge.
        assert float(pts[1][2]) == pytest.approx(z_ridge)


class TestGableFullSpanTrusses:
    """Full-span gable truss frame generation (roofType="Gable").

    Verifies the MXF ``<FrameList>`` contains a full-span common truss: a
    single wall-to-wall ``BottomChord`` and two sloping ``TopChord`` members
    meeting at the central ridge at ``X = width/2``, instead of the split
    half-span trusses that MiTek Pamir auto-frames from layout-only roof
    surfaces (see proposal.md).
    """

    _WIDTH = 10.0
    _DEPTH = 15.0
    _PITCH = 30.0
    _OVERHANG_M = 0.5

    def _build_root(self, **overrides):
        defaults = {
            "floorPlanDimensions": "10x15m",
            "roofType": "Gable",
            "roofPitch": 30,
            "overhang": "0.5m",
        }
        defaults.update(overrides)
        return _parse(build_mxf(_params(**defaults)))

    @staticmethod
    def _chord_line(member) -> list[tuple[float, float]]:
        """Return the ``(start, end)`` chord endpoints from a WoodMember Face.

        The Face polygon's first two points encode the structural chord line;
        the remaining two points are the perpendicular timber-thickness offset.
        """
        face = member.find("./FrontFace/Face")
        polygon = face.attrib["polygon"]
        pts = [
            (float(p.split(",")[0]), float(p.split(",")[1]))
            for p in polygon.split(" ")
        ]
        return pts[:2]

    def test_gable_full_span(self):
        # The MXF must contain a <FrameList> with one full-span common truss
        # Frame: a single wall-to-wall BottomChord + two TopChords meeting at
        # the central ridge at X = width/2.
        root = self._build_root()
        frame_list = root.find("FrameList")
        assert frame_list is not None, "MXF must emit a <FrameList> for gable roofs"

        frame = frame_list.find("Frame")
        assert frame is not None
        assert frame.attrib["family"] == "Truss"
        # quantity reflects the number of common trusses placed along depth.
        assert int(frame.attrib["quantity"]) >= 2

        members = frame.findall("./PartList/Part/MemberList/WoodMember")
        bottoms = [m for m in members if m.attrib["type"] == "BottomChord"]
        tops = [m for m in members if m.attrib["type"] == "TopChord"]
        # Exactly one full-span BottomChord and exactly two TopChords.
        assert len(bottoms) == 1, "Gable truss must have a single full-span bottom chord"
        assert len(tops) == 2, "Gable truss must have two sloping top chords"

        # --- Bottom chord spans wall-to-wall (full span, single member) ---
        bpts = self._chord_line(bottoms[0])
        assert bpts[0][0] == pytest.approx(0.0)
        assert bpts[1][0] == pytest.approx(self._WIDTH)
        assert bpts[0][1] == pytest.approx(0.0)
        assert bpts[1][1] == pytest.approx(0.0)

        # --- Two top chords meet at the central ridge at X = width/2 ---
        ridge_x = self._WIDTH / 2.0
        ridge_y = ridge_x * math.tan(math.radians(self._PITCH))
        eave_xs: list[float] = []
        for top in tops:
            pts = self._chord_line(top)
            reaches_ridge = [
                (p[0] == pytest.approx(ridge_x) and p[1] == pytest.approx(ridge_y))
                for p in pts
            ]
            assert any(reaches_ridge), (
                f"Top chord does not reach the ridge at "
                f"({ridge_x}, {ridge_y}): {pts}"
            )
            # The other endpoint is the eave (sits on the outer wall + overhang).
            for p in pts:
                if not (
                    p[0] == pytest.approx(ridge_x)
                    and p[1] == pytest.approx(ridge_y)
                ):
                    eave_xs.append(p[0])
        # The two top chords come from opposite eaves (one left, one right).
        assert len(eave_xs) == 2
        assert min(eave_xs) < ridge_x
        assert max(eave_xs) > ridge_x

    def test_gable_full_span_ridge_height_matches_pitch(self):
        # The ridge Y coordinate of the top chords == (width/2) * tan(pitch).
        root = self._build_root()
        frame = root.find("FrameList/Frame")
        tops = frame.findall("./PartList/Part/MemberList/WoodMember[@type='TopChord']")
        expected_ridge_y = (self._WIDTH / 2.0) * math.tan(math.radians(self._PITCH))
        ridge_ys: list[float] = []
        for top in tops:
            for _x, y in self._chord_line(top):
                ridge_ys.append(y)
        assert max(ridge_ys) == pytest.approx(expected_ridge_y)

    def test_gable_frame_quantity_matches_truss_count(self):
        # The FrameList carries two Frame definitions: a common-truss Frame
        # whose quantity covers the interior positions (total - 2 gable ends)
        # and a GableEnd Frame whose quantity is 2 (first + last positions).
        # The sum of both quantities equals the total truss count.
        root = self._build_root()
        frames = root.findall("FrameList/Frame")
        from geometry_solver import GeometrySolver

        solver = GeometrySolver(
            self._WIDTH * 1000.0, self._DEPTH * 1000.0, "gable", self._PITCH
        )
        total = len(solver.mxf_truss_frames())
        gable_ends = len(solver.mxf_gable_end_frames())
        expected_common = max(0, total - gable_ends)
        quantities = {
            f.attrib["family"]: int(f.attrib["quantity"]) for f in frames
        }
        assert quantities.get("Truss", 0) == expected_common
        assert quantities.get("GableEnd", 0) == gable_ends
        assert quantities.get("Truss", 0) + quantities.get("GableEnd", 0) == total

    def test_gable_full_span_zero_overhang(self):
        # With no overhang the top-chord eave endpoints sit exactly on the
        # outer walls (X=0 and X=width) at the eaves baseline.
        root = self._build_root(overhang=None)
        frame = root.find("FrameList/Frame")
        tops = frame.findall("./PartList/Part/MemberList/WoodMember[@type='TopChord']")
        eave_xs: list[float] = []
        for top in tops:
            for x, y in self._chord_line(top):
                if y == pytest.approx(0.0):
                    eave_xs.append(x)
        assert min(eave_xs) == pytest.approx(0.0)
        assert max(eave_xs) == pytest.approx(self._WIDTH)

    def test_flat_roof_emits_no_frame_list(self):
        # Only gable roofs emit a full-span FrameList in this task; a flat roof
        # must not produce one.
        root = self._build_root(roofType="Flat", roofPitch=0)
        assert root.find("FrameList") is None


class TestTrussTransportHeightSplitting:
    """Transport-height splitting for tall gable trusses (ridge > 3.3 m).

    Verifies the unified geometry solver splits trusses exceeding the 3.3 m
    road transport limit into Part 1 (rectangular base, height <= 2.8 m) and
    Part 2 (triangular cap) joined by horizontal splice chords at the 2.8 m
    interface, per design.md §"Transport Limit Detection and Multi-Part
    Splicing". Tested at the solver level because the MXF builder integration
    is a later task; the solver is the single source of truth for the split
    geometry.
    """

    _TALL_WIDTH_M = 14.0
    _DEPTH_M = 15.0
    _PITCH = 30.0
    _SHORT_WIDTH_M = 10.0

    def test_truss_transport_height_splitting(self):
        from geometry_solver import (
            TRANSPORT_MAX_HEIGHT_M,
            TRANSPORT_SPLIT_HEIGHT_M,
            GeometrySolver,
        )

        # 14 m wide gable @ 30° -> ridge = 7.0 * tan(30°) ≈ 4.04 m (> 3.3 m).
        solver = GeometrySolver(
            self._TALL_WIDTH_M * 1000.0, self._DEPTH_M * 1000.0, "gable", self._PITCH
        )
        assert solver.truss_height_m > TRANSPORT_MAX_HEIGHT_M
        assert solver.needs_transport_split()

        frames = solver.mxf_truss_parts()
        assert len(frames) >= 2, "Solver must produce one split frame per truss position"

        expected_ridge_y = solver.truss_height_m
        expected_mid = self._TALL_WIDTH_M / 2.0
        tan_pitch = math.tan(math.radians(self._PITCH))
        expected_x_left = TRANSPORT_SPLIT_HEIGHT_M / tan_pitch

        for y_m, parts in frames:
            assert len(parts) == 2, (
                f"Tall truss frame at Y={y_m} must split into 2 parts, got {len(parts)}"
            )

            # --- Part 1 (Base): rectangular, height <= 2.8 m ---
            name1, z1_base, z1_top, members1 = parts[0]
            assert name1 == "Part 1"
            assert z1_base == pytest.approx(0.0)
            assert z1_top <= TRANSPORT_SPLIT_HEIGHT_M + 1e-9, (
                f"Part 1 (Base) height must be <= 2.8 m, got {z1_top}"
            )
            assert z1_top == pytest.approx(TRANSPORT_SPLIT_HEIGHT_M)
            # Part 1 carries a wall-to-wall BottomChord at Y=0.
            bottoms1 = [m for m in members1 if m[0] == "BottomChord"]
            assert len(bottoms1) == 1
            _, b1_start, b1_end = bottoms1[0]
            assert b1_start == pytest.approx((0.0, 0.0))
            assert b1_end == pytest.approx((self._TALL_WIDTH_M, 0.0))
            # Part 1 carries a flat HORIZONTAL TopChord at Y=2.8 (lower splice).
            tops1 = [m for m in members1 if m[0] == "TopChord"]
            assert len(tops1) == 1
            _, sp_lower_start, sp_lower_end = tops1[0]
            assert sp_lower_start[1] == pytest.approx(sp_lower_end[1]), (
                "Part 1 flat top chord (lower splice) must be horizontal"
            )
            assert sp_lower_start[1] == pytest.approx(TRANSPORT_SPLIT_HEIGHT_M)
            assert sp_lower_start[0] == pytest.approx(0.0)
            assert sp_lower_end[0] == pytest.approx(self._TALL_WIDTH_M)

            # --- Part 2 (Cap): triangular, sits on Part 1 ---
            name2, z2_base, z2_top, members2 = parts[1]
            assert name2 == "Part 2"
            assert z2_base == pytest.approx(TRANSPORT_SPLIT_HEIGHT_M)
            assert z2_top == pytest.approx(expected_ridge_y)
            # Part 2 carries a horizontal BottomChord at Y=2.8 (upper splice)
            # bounded by the top-chord crossings.
            bottoms2 = [m for m in members2 if m[0] == "BottomChord"]
            assert len(bottoms2) == 1
            _, sp_upper_start, sp_upper_end = bottoms2[0]
            assert sp_upper_start[1] == pytest.approx(sp_upper_end[1]), (
                "Part 2 bottom chord (upper splice) must be horizontal"
            )
            assert sp_upper_start[1] == pytest.approx(TRANSPORT_SPLIT_HEIGHT_M)
            assert sp_upper_start[0] == pytest.approx(expected_x_left)
            assert sp_upper_end[0] == pytest.approx(
                self._TALL_WIDTH_M - expected_x_left
            )
            # Part 2 carries two TopChords that rise to the central ridge,
            # preserving the original roof pitch.
            tops2 = [m for m in members2 if m[0] == "TopChord"]
            assert len(tops2) == 2
            ridge_xs: list[float] = []
            for _mtype, s, e in tops2:
                for px, py in (s, e):
                    if py == pytest.approx(expected_ridge_y):
                        ridge_xs.append(px)
                # Each cap top chord keeps the roof pitch (slope == tan(pitch)).
                (sx, sy), (ex, ey) = s, e
                run = ex - sx
                rise = ey - sy
                assert rise / run == pytest.approx(tan_pitch) or (
                    rise / run == pytest.approx(-tan_pitch)
                )
            assert len(ridge_xs) == 2
            assert all(x == pytest.approx(expected_mid) for x in ridge_xs), (
                f"Cap top chords must meet at the ridge X={expected_mid}, "
                f"got {ridge_xs}"
            )

    def test_truss_transport_short_truss_not_split(self):
        from geometry_solver import GeometrySolver

        # 10 m wide gable @ 30° -> ridge = 5.0 * tan(30°) ≈ 2.89 m (< 3.3 m).
        solver = GeometrySolver(
            self._SHORT_WIDTH_M * 1000.0, self._DEPTH_M * 1000.0, "gable", self._PITCH
        )
        assert not solver.needs_transport_split()

        frames = solver.mxf_truss_parts()
        assert len(frames) >= 2
        for _y_m, parts in frames:
            assert len(parts) == 1, "Short truss must NOT be transport-split"
            name, z_base, z_top, members = parts[0]
            assert name == "Part 1"
            assert z_base == pytest.approx(0.0)
            assert z_top == pytest.approx(solver.truss_height_m)
            # Single-part geometry matches the full-span frame: 2 TopChords + 1
            # BottomChord (mirrors TestGableFullSpanTrusses).
            assert len([m for m in members if m[0] == "TopChord"]) == 2
            assert len([m for m in members if m[0] == "BottomChord"]) == 1

    def test_truss_transport_non_gable_returns_empty(self):
        from geometry_solver import GeometrySolver

        # Transport splitting is gable-only in this change; hip/mono/flat
        # solvers must return an empty part list even when very tall.
        tall_mono = GeometrySolver(
            self._TALL_WIDTH_M * 1000.0, self._DEPTH_M * 1000.0, "mono-pitch", 25.0
        )
        assert tall_mono.truss_height_m > 3.3
        assert tall_mono.mxf_truss_parts() == []


class TestGableEndPanels:
    """Gable-end panel frame generation (roofType="Gable").

    Verifies the first and last trusses in the layout sequence are emitted as
    ``GableEnd`` family ``PanelFrame`` definitions with vertical studs spaced
    at the standard 600 mm pitch, per design.md §"Outer Gable-End Panels".
    """

    _WIDTH = 10.0
    _DEPTH = 15.0
    _PITCH = 30.0
    _OVERHANG_M = 0.5
    _STUD_SPACING_M = 0.6

    def _build_root(self, **overrides):
        defaults = {
            "floorPlanDimensions": "10x15m",
            "roofType": "Gable",
            "roofPitch": 30,
            "overhang": "0.5m",
        }
        defaults.update(overrides)
        return _parse(build_mxf(_params(**defaults)))

    def test_gable_end(self):
        # The MXF must carry a GableEnd PanelFrame Frame definition covering
        # the two outer (first + last) layout positions, plus vertical Stud
        # members spaced at 600 mm centres running from the bottom chord up to
        # the sloping top chord.
        root = self._build_root()
        frame_list = root.find("FrameList")
        assert frame_list is not None, "MXF must emit a <FrameList> for gable roofs"

        gable_frames = [
            f for f in frame_list.findall("Frame")
            if f.attrib["family"] == "GableEnd"
        ]
        assert len(gable_frames) == 1, (
            "Expected exactly one GableEnd Frame definition (shared by both "
            "outer positions via quantity=2)"
        )
        gable = gable_frames[0]
        assert gable.attrib["type"] == "PanelFrame"
        assert int(gable.attrib["quantity"]) == 2, (
            "GableEnd Frame must cover the two outer positions (first + last)"
        )

        # Outer profile preserved: 1 BottomChord + 2 TopChords (same as a
        # common truss) plus vertical Stud members.
        members = gable.findall("./PartList/Part/MemberList/WoodMember")
        bottoms = [m for m in members if m.attrib["type"] == "BottomChord"]
        tops = [m for m in members if m.attrib["type"] == "TopChord"]
        studs = [m for m in members if m.attrib["type"] == "Stud"]
        assert len(bottoms) == 1, "GableEnd panel must keep the wall-to-wall BottomChord"
        assert len(tops) == 2, "GableEnd panel must keep the two sloping TopChords"
        assert len(studs) >= 2, "GableEnd panel must add vertical Stud members"

        # Each stud is vertical (start.X == end.X), starts at the bottom chord
        # (Y=0), and rises above it. Collect X positions for spacing checks.
        stud_xs: list[float] = []
        for stud in studs:
            face = stud.find("./FrontFace/Face")
            assert face is not None
            pts = [
                (float(p.split(",")[0]), float(p.split(",")[1]))
                for p in face.attrib["polygon"].split(" ")
            ]
            start, end = pts[0], pts[1]
            assert start[0] == pytest.approx(end[0]), (
                f"Stud at X={start[0]} must be vertical (start.X == end.X)"
            )
            assert start[1] == pytest.approx(0.0), (
                f"Stud at X={start[0]} must start at the bottom chord (Y=0)"
            )
            assert end[1] > 0.0, (
                f"Stud at X={start[0]} must rise above the bottom chord"
            )
            stud_xs.append(start[0])

        # Studs are spaced at the standard 600 mm pitch.
        stud_xs.sort()
        spacings = [stud_xs[i + 1] - stud_xs[i] for i in range(len(stud_xs) - 1)]
        assert all(s == pytest.approx(self._STUD_SPACING_M) for s in spacings), (
            f"Stud spacing must be 600 mm, got {spacings}"
        )

    def test_gable_end_studs_reach_top_chord(self):
        # The stud top endpoint (Y) must match the top-chord height at that X.
        # tan(30°) ~ 0.577; for X <= width/2 the top-chord Y = X * tan(pitch),
        # and for X > width/2 it falls symmetrically.
        root = self._build_root()
        gable = next(
            f for f in root.findall("FrameList/Frame")
            if f.attrib["family"] == "GableEnd"
        )
        tan_pitch = math.tan(math.radians(self._PITCH))
        mid = self._WIDTH / 2.0
        for stud in gable.findall("./PartList/Part/MemberList/WoodMember[@type='Stud']"):
            face = stud.find("./FrontFace/Face")
            pts = [
                (float(p.split(",")[0]), float(p.split(",")[1]))
                for p in face.attrib["polygon"].split(" ")
            ]
            (_sx, _sy), (ex, ey) = pts[0], pts[1]
            expected_top = ex * tan_pitch if ex <= mid else (self._WIDTH - ex) * tan_pitch
            assert ey == pytest.approx(expected_top, abs=1e-3), (
                f"Stud at X={ex} top Y={ey} does not match top chord Y={expected_top}"
            )

    def test_gable_end_does_not_duplicate_common_truss_positions(self):
        # total positions == common-truss quantity + gable-end quantity (2).
        # The gable-end positions replace (not extend) the outer common-truss
        # positions, so the FrameList quantities must sum to the truss count.
        from geometry_solver import GeometrySolver

        root = self._build_root()
        frames = root.findall("FrameList/Frame")
        solver = GeometrySolver(
            self._WIDTH * 1000.0, self._DEPTH * 1000.0, "gable", self._PITCH
        )
        total = len(solver.mxf_truss_frames())
        emitted = sum(int(f.attrib["quantity"]) for f in frames)
        assert emitted == total, (
            f"FrameList quantities sum to {emitted} but the building has "
            f"{total} truss positions"
        )

    def test_flat_roof_emits_no_gable_end_frame(self):
        # GableEnd panels are gable-only; a flat roof must not emit one.
        root = self._build_root(roofType="Flat", roofPitch=0)
        assert root.find("FrameList") is None


class TestHipRoofSurfaces:
    """Hip (four-plane) roof surface generation (roofType="Hip").

    Spec scenario (spec.md): W=8.0m, D=9.6m, roofType="Hip", roofPitch=18,
    overhang=0.25m -> 4 surfaces (2 trapezoids + 2 hip-end triangles),
    Z_eaves = 3.12, Z_ridge ~ 4.501, ridge from (4.0, 4.0, 4.501) to
    (4.0, 5.6, 4.501).
    """

    _WIDTH = 8.0
    _DEPTH = 9.6
    _PITCH = 18.0
    _OVERHANG_M = 0.25
    _Z_EAVES = 3.12

    def _build_root(self, **overrides):
        defaults = {
            "floorPlanDimensions": "8x9.6m",
            "roofType": "Hip",
            "roofPitch": 18,
            "overhang": "0.25m",
        }
        defaults.update(overrides)
        return _parse(build_mxf(_params(**defaults)))

    def _expected_z(self):
        rise = math.tan(math.radians(self._PITCH))
        run_ridge = min(self._WIDTH, self._DEPTH) / 2.0
        z_eaves = self._Z_EAVES
        z_ridge = z_eaves + (run_ridge + self._OVERHANG_M) * rise
        return z_eaves, z_ridge

    def test_hip_roof_generation(self):
        # Four roof surfaces (SR0-0..SR0-3) emitted under Building/RoofList
        # plus the root SurfaceList.
        root = self._build_root()
        roof_ids = [r.attrib["surfaceID"] for r in root.findall(".//RoofList/Roof")]
        floor_ids = [f.attrib["surfaceID"] for f in root.findall(".//FloorList/Floor")]
        assert roof_ids == ["SR0-0", "SR0-1", "SR0-2", "SR0-3"]
        assert floor_ids == ["SF0-0"]
        for sid in ("SR0-0", "SR0-1", "SR0-2", "SR0-3"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            assert surface is not None
            assert surface.attrib["covering"] == "undefined"

    def test_hip_floor_surface_polygon_matches_spec(self):
        root = self._build_root()
        sf0 = root.find('.//SurfaceList/Surface[@id="SF0-0"]')
        assert sf0 is not None
        assert sf0.attrib["polygon"] == "0,0,0 8,0,0 8,9.6,0 0,9.6,0 0,0,0"

    def test_hip_eaves_and_ridge_heights_match_spec(self):
        # Z_eaves = 3.12 (anchored); Z_ridge = 3.12 + (W/2 + O) * tan(theta).
        # Coordinates are serialized with ``:g`` (6 significant figures), so a
        # 1 mm tolerance accommodates the documented rounding (spec: = 3.12,
        # ~4.501).
        root = self._build_root()
        z_eaves, z_ridge = self._expected_z()
        for sid in ("SR0-0", "SR0-1", "SR0-2", "SR0-3"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            zs = [float(p.split(",")[2]) for p in surface.attrib["polygon"].split(" ")]
            assert min(zs) == pytest.approx(z_eaves, abs=1e-3)
            assert max(zs) == pytest.approx(z_ridge, abs=1e-3)
        assert z_eaves == pytest.approx(self._Z_EAVES, abs=1e-3)
        assert z_ridge > self._Z_EAVES

    def test_hip_ridge_runs_shortened_along_depth(self):
        # Ridge from (W/2, W/2, Z_ridge) to (W/2, D-W/2, Z_ridge) -- shorter
        # than the full depth by W (inset W/2 from each short end).
        root = self._build_root()
        _, z_ridge = self._expected_z()
        mid = self._WIDTH / 2.0
        ridge_pts = []
        for sid in ("SR0-0", "SR0-1", "SR0-2", "SR0-3"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            for p in surface.attrib["polygon"].split(" "):
                x, y, z = (float(v) for v in p.split(","))
                if z == pytest.approx(z_ridge, abs=1e-3):
                    ridge_pts.append((x, y))
        # The ridge has exactly two distinct endpoints (no other Z_ridge pts).
        unique = {(round(x, 3), round(y, 3)) for x, y in ridge_pts}
        assert unique == {
            (mid, self._WIDTH / 2.0),
            (mid, self._DEPTH - self._WIDTH / 2.0),
        }

    def test_hip_surfaces_slope_matches_pitch(self):
        # rise/run between the eaves edge and ridge edge == tan(pitch).
        # SR0-0 (low-X trapezoid): pts[0]=SW eaves, pts[1]=front ridge.
        # Serialized coordinates use ``:g`` (6 sig figs), so allow 1e-3 slack.
        root = self._build_root()
        rise = math.tan(math.radians(self._PITCH))
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        pts = [p.split(",") for p in surface.attrib["polygon"].split(" ")]
        run = float(pts[1][0]) - float(pts[0][0])
        z_rise = float(pts[1][2]) - float(pts[0][2])
        assert z_rise / run == pytest.approx(rise, abs=1e-3)

    def test_hip_overhang_expands_footprint(self):
        # Combined roof spans X in [-0.25, 8.25], Y in [-0.25, 9.85].
        root = self._build_root()
        all_xs, all_ys = [], []
        for sid in ("SR0-0", "SR0-1", "SR0-2", "SR0-3"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            for p in surface.attrib["polygon"].split(" "):
                x, y, _ = (float(v) for v in p.split(","))
                all_xs.append(x)
                all_ys.append(y)
        assert min(all_xs) == pytest.approx(-self._OVERHANG_M)
        assert max(all_xs) == pytest.approx(self._WIDTH + self._OVERHANG_M)
        assert min(all_ys) == pytest.approx(-self._OVERHANG_M)
        assert max(all_ys) == pytest.approx(self._DEPTH + self._OVERHANG_M)

    def test_hip_zero_overhang(self):
        # No overhang: eaves sit on the outer walls at z_eaves (3.12).
        root = self._build_root(overhang=None)
        for sid in ("SR0-0", "SR0-1", "SR0-2", "SR0-3"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            zs = [float(p.split(",")[2]) for p in surface.attrib["polygon"].split(" ")]
            assert min(zs) == pytest.approx(self._Z_EAVES, abs=1e-3)


class TestDynamicEavesHeight:
    def test_dynamic_z_base_applied(self):
        from src.geometry_solver import (
            flat_roof_surface_polygon,
            monopitch_roof_surface_polygon,
            gable_roof_surface_polygons,
            hip_roof_surface_polygons,
        )
        custom_z_base = 2.50  # 2.5m wall top instead of 3.05m
        expected_z_eaves = 2.50 + 0.07  # 2.57m

        # 1. Flat roof
        flat_poly = flat_roof_surface_polygon(10.0, 15.0, 0.5, z_base=custom_z_base)
        for pt in flat_poly:
            assert pt[2] == pytest.approx(expected_z_eaves)

        # 2. Monopitch roof
        mono_poly = monopitch_roof_surface_polygon(10.0, 15.0, 30.0, 0.5, z_base=custom_z_base)
        assert mono_poly[0][2] == pytest.approx(expected_z_eaves)

        # 3. Gable roof
        gable_polys = gable_roof_surface_polygons(10.0, 15.0, 30.0, 0.5, z_base=custom_z_base)
        assert gable_polys[0][0][2] == pytest.approx(expected_z_eaves)

        # 4. Hip roof
        hip_polys = hip_roof_surface_polygons(8.0, 9.6, 18.0, 0.25, z_base=custom_z_base)
        assert hip_polys[0][0][2] == pytest.approx(expected_z_eaves)

