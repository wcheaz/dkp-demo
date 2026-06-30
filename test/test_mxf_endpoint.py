import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / "agent" / ".env")

_agent_src = str(Path(__file__).resolve().parent.parent / "agent")
if _agent_src not in sys.path:
    sys.path.insert(0, _agent_src)

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
