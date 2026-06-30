import sys
import xml.etree.ElementTree as ET
from types import SimpleNamespace

import pytest

sys.path.insert(0, "agent/src")
from mxf_builder import (  # noqa: E402
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
