import sys
from pathlib import Path

_agent_src = str(Path(__file__).resolve().parent.parent / "agent")
if _agent_src not in sys.path:
    sys.path.insert(0, _agent_src)

import httpx
import pytest

from src.main import app


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


def _valid_payload(**overrides):
    payload = {
        "floorPlanDimensions": "10x15m",
        "roofType": "Gable",
        "roofPitch": 30,
    }
    payload.update(overrides)
    return payload


class TestValidRequest:
    @pytest.mark.anyio
    async def test_returns_200_with_dxf_content(self, client):
        resp = await client.post("/api/dxf/generate", json=_valid_payload())
        assert resp.status_code == 200
        assert len(resp.content) > 0
        body = resp.content.decode("utf-8", errors="replace")
        assert "SECTION" in body

    @pytest.mark.anyio
    async def test_content_type_is_dxf(self, client):
        resp = await client.post("/api/dxf/generate", json=_valid_payload())
        assert resp.status_code == 200
        assert "application/dxf" in resp.headers.get("content-type", "")

    @pytest.mark.anyio
    async def test_content_disposition_header(self, client):
        resp = await client.post("/api/dxf/generate", json=_valid_payload())
        assert resp.status_code == 200
        cd = resp.headers.get("content-disposition", "")
        assert 'attachment; filename="design.dxf"' in cd


class TestMissingRoofType:
    @pytest.mark.anyio
    async def test_missing_roof_type_returns_400(self, client):
        payload = _valid_payload()
        del payload["roofType"]
        resp = await client.post("/api/dxf/generate", json=payload)
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data


class TestInvalidRoofType:
    @pytest.mark.anyio
    async def test_invalid_roof_type_returns_400(self, client):
        resp = await client.post(
            "/api/dxf/generate", json=_valid_payload(roofType="Dome")
        )
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data
        assert "Dome" in data["error"]


class TestMalformedJson:
    @pytest.mark.anyio
    async def test_malformed_json_returns_422(self, client):
        resp = await client.post(
            "/api/dxf/generate",
            content=b"not json at all",
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_invalid_param_types_returns_422(self, client):
        resp = await client.post(
            "/api/dxf/generate",
            json={"floorPlanDimensions": [1, 2], "roofType": 123},
        )
        assert resp.status_code == 422


class TestFlatRoofMinimal:
    @pytest.mark.anyio
    async def test_minimal_flat_roof_returns_200(self, client):
        resp = await client.post(
            "/api/dxf/generate",
            json={"floorPlanDimensions": "8x12m", "roofType": "Flat"},
        )
        assert resp.status_code == 200
        body = resp.content.decode("utf-8", errors="replace")
        assert "SECTION" in body
        assert "application/dxf" in resp.headers.get("content-type", "")
