import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / "agent" / ".env")

_agent_src = str(Path(__file__).resolve().parent.parent / "agent")
if _agent_src not in sys.path:
    sys.path.insert(0, _agent_src)

import xml.etree.ElementTree as ET  # noqa: E402

import httpx  # noqa: E402
import pytest  # noqa: E402

from src.main import app  # noqa: E402


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


def _valid_payload(**overrides):
    payload = {
        "floorPlanDimensions": "10x6m",
        "buildingType": "Test",
    }
    payload.update(overrides)
    return payload


class TestMxfEndpointValidRequest:
    @pytest.mark.anyio
    async def test_mxf_endpoint_returns_200_with_mxf_content(self, client):
        resp = await client.post("/api/mxf/generate", json=_valid_payload())
        assert resp.status_code == 200
        assert len(resp.content) > 0
        body = resp.content.decode("utf-8", errors="replace")
        assert body.startswith("<?xml")
        assert "<Mxf" in body
        assert 'version="MXF Version 5.11"' in body

    @pytest.mark.anyio
    async def test_mxf_endpoint_content_type_is_mxf(self, client):
        resp = await client.post("/api/mxf/generate", json=_valid_payload())
        assert resp.status_code == 200
        assert "application/mxf" in resp.headers.get("content-type", "")

    @pytest.mark.anyio
    async def test_mxf_endpoint_content_disposition_header(self, client):
        resp = await client.post("/api/mxf/generate", json=_valid_payload())
        assert resp.status_code == 200
        cd = resp.headers.get("content-disposition", "")
        assert 'attachment; filename="design.mxf"' in cd

    @pytest.mark.anyio
    async def test_mxf_endpoint_contains_four_walls(self, client):
        resp = await client.post("/api/mxf/generate", json=_valid_payload())
        assert resp.status_code == 200
        body = resp.content.decode("utf-8", errors="replace")
        # Four building walls (W0..W3) plus four wall definitions.
        for wall_id in ("W0", "W1", "W2", "W3"):
            assert wall_id in body


class TestMxfEndpointInvalidDimensions:
    @pytest.mark.anyio
    async def test_mxf_endpoint_missing_dimensions_returns_400(self, client):
        payload = _valid_payload()
        del payload["floorPlanDimensions"]
        resp = await client.post("/api/mxf/generate", json=payload)
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data

    @pytest.mark.anyio
    async def test_mxf_endpoint_non_positive_dimensions_returns_400(self, client):
        resp = await client.post(
            "/api/mxf/generate",
            json=_valid_payload(floorPlanDimensions="0x10m"),
        )
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data

    @pytest.mark.anyio
    async def test_mxf_endpoint_malformed_dimensions_returns_400(self, client):
        resp = await client.post(
            "/api/mxf/generate",
            json=_valid_payload(floorPlanDimensions="about twenty meters"),
        )
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data


class TestMxfEndpointMalformedJson:
    @pytest.mark.anyio
    async def test_mxf_endpoint_malformed_json_returns_422(self, client):
        resp = await client.post(
            "/api/mxf/generate",
            content=b"not json at all",
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_mxf_endpoint_invalid_param_types_returns_422(self, client):
        resp = await client.post(
            "/api/mxf/generate",
            json={"floorPlanDimensions": [1, 2], "buildingType": 123},
        )
        assert resp.status_code == 422


class TestMxfEndpointMinimalPayload:
    @pytest.mark.anyio
    async def test_mxf_endpoint_minimal_dimensions_returns_200(self, client):
        resp = await client.post(
            "/api/mxf/generate",
            json={"floorPlanDimensions": "8x12m"},
        )
        assert resp.status_code == 200
        body = resp.content.decode("utf-8", errors="replace")
        assert "<Mxf" in body
        assert "application/mxf" in resp.headers.get("content-type", "")


class TestMxfEndpointRoofSurfaces:
    """Verify roofType / roofPitch / overhang flow into surface XML nodes."""

    @pytest.mark.anyio
    async def test_mxf_endpoint_gable_roof_emits_surface_lists(self, client):
        resp = await client.post(
            "/api/mxf/generate",
            json=_valid_payload(
                floorPlanDimensions="10x15m",
                roofType="Gable",
                roofPitch=30,
                overhang="0.5m",
            ),
        )
        assert resp.status_code == 200
        root = ET.fromstring(resp.content)
        # <RoofList>/<FloorList> under <Building>, <SurfaceList> at the root.
        assert root.find(".//Building/RoofList") is not None
        assert root.find(".//Building/FloorList") is not None
        assert root.find("SurfaceList") is not None
        # Gable => two roof planes plus one floor surface.
        roof_ids = [r.attrib["surfaceID"] for r in root.findall(".//RoofList/Roof")]
        floor_ids = [f.attrib["surfaceID"] for f in root.findall(".//FloorList/Floor")]
        assert roof_ids == ["SR0-0", "SR0-1"]
        assert floor_ids == ["SF0-0"]
        for sid in ("SR0-0", "SR0-1"):
            surface = root.find(f'.//SurfaceList/Surface[@id="{sid}"]')
            assert surface is not None
            assert surface.attrib["covering"] == "undefined"
            # Each polygon point carries three coordinate components.
            first_point = surface.attrib["polygon"].split(" ")[0]
            assert len(first_point.split(",")) == 3
        floor_surface = root.find('.//SurfaceList/Surface[@id="SF0-0"]')
        assert floor_surface is not None
        assert floor_surface.attrib["verticalOffset"] == "0"

    @pytest.mark.anyio
    async def test_mxf_endpoint_flat_roof_returns_single_horizontal_surface(self, client):
        resp = await client.post(
            "/api/mxf/generate",
            json=_valid_payload(
                floorPlanDimensions="10x15m",
                roofType="Flat",
                roofPitch=0,
                overhang="0.5m",
            ),
        )
        assert resp.status_code == 200
        root = ET.fromstring(resp.content)
        roof_ids = [r.attrib["surfaceID"] for r in root.findall(".//RoofList/Roof")]
        assert roof_ids == ["SR0-0"]
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        assert surface is not None
        # Flat (zero pitch) => horizontal plane at the anchored eaves baseline Z=3.12.
        zs = [float(p.split(",")[2]) for p in surface.attrib["polygon"].split(" ")]
        assert all(z == pytest.approx(3.12) for z in zs)

    @pytest.mark.anyio
    async def test_mxf_endpoint_overhang_unit_string_expands_footprint(self, client):
        # overhang="0.5m" must be parsed and expand the roof footprint by 0.5m on
        # every side (10x15 plan -> spans X[-0.5, 10.5], Y[-0.5, 15.5]).
        resp = await client.post(
            "/api/mxf/generate",
            json=_valid_payload(
                floorPlanDimensions="10x15m",
                roofType="Flat",
                overhang="0.5m",
            ),
        )
        assert resp.status_code == 200
        root = ET.fromstring(resp.content)
        surface = root.find('.//SurfaceList/Surface[@id="SR0-0"]')
        pts = [
            (float(p.split(",")[0]), float(p.split(",")[1]))
            for p in surface.attrib["polygon"].split(" ")
        ]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        assert min(xs) == pytest.approx(-0.5)
        assert max(xs) == pytest.approx(10.5)
        assert min(ys) == pytest.approx(-0.5)
        assert max(ys) == pytest.approx(15.5)

    @pytest.mark.anyio
    async def test_mxf_endpoint_hip_roof_emits_four_surfaces(self, client):
        resp = await client.post(
            "/api/mxf/generate",
            json=_valid_payload(
                floorPlanDimensions="10x15m",
                roofType="Hip",
                roofPitch=18,
                overhang="250mm",
            ),
        )
        assert resp.status_code == 200
        root = ET.fromstring(resp.content)
        roof_ids = [r.attrib["surfaceID"] for r in root.findall(".//RoofList/Roof")]
        # Hip => four hip planes plus one floor surface.
        assert roof_ids == ["SR0-0", "SR0-1", "SR0-2", "SR0-3"]
        assert root.find(".//FloorList/Floor") is not None


class TestMxfEndpointStructuralFraming:
    """Verify the REST payload carries the full structural framing XML.

    Per ``openspec/changes/gable-roof-generation-fixes/specs/mxf-generation``
    the gable MXF response SHALL include a ``<FrameList>`` (root-level Frame
    definitions carrying member/plate/brace geometry) and a
    ``<BuildingFrameList>`` under ``<Building>`` positioning each generated
    frame instance.
    """

    @pytest.mark.anyio
    async def test_mxf_endpoint_gable_emits_frame_list_and_building_frame_list(
        self, client
    ):
        resp = await client.post(
            "/api/mxf/generate",
            json=_valid_payload(
                floorPlanDimensions="10x15m",
                roofType="Gable",
                roofPitch=30,
                overhang="0.5m",
            ),
        )
        assert resp.status_code == 200
        root = ET.fromstring(resp.content)

        # Root-level <FrameList> carrying the Frame definitions.
        frame_list = root.find("FrameList")
        assert frame_list is not None, (
            "/api/mxf/generate must emit a <FrameList> for gable roofs"
        )
        frames = frame_list.findall("Frame")
        assert len(frames) >= 1, (
            "<FrameList> must carry at least one Frame definition"
        )

        # <BuildingFrameList> under <Building> positioning each frame instance.
        building_frame_list = root.find(".//Building/BuildingFrameList")
        assert building_frame_list is not None, (
            "/api/mxf/generate must emit a <BuildingFrameList> under <Building> "
            "for gable roofs"
        )
        building_frames = building_frame_list.findall("BuildingFrame")
        assert len(building_frames) >= 1, (
            "<BuildingFrameList> must position at least one frame instance"
        )
        # Each BuildingFrame references a frameID defined in <FrameList>.
        defined_ids = {f.attrib["id"] for f in frames}
        for bf in building_frames:
            assert bf.attrib["frameID"] in defined_ids, (
                f"<BuildingFrame frameID={bf.attrib['frameID']!r}> must "
                f"reference a Frame defined in <FrameList> ({sorted(defined_ids)})"
            )
