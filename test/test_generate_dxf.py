import asyncio
import base64
import sys
from pathlib import Path

_agent_src = str(Path(__file__).resolve().parent.parent / "agent")
if _agent_src not in sys.path:
    sys.path.insert(0, _agent_src)

from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage

from src.agent import (
    DesignEntry,
    DesignParameters,
    StateDeps,
    YourState,
    agent,
    generate_dxf,
)


def _make_ctx(entries):
    state = YourState(designs=list(entries))
    deps = StateDeps(state)
    return RunContext(deps=deps, model=None, usage=RunUsage(), agent=agent)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestSuccessfulGeneration:
    def test_sets_dxf_content_to_valid_base64(self):
        params = DesignParameters(
            floorPlanDimensions="10x15m", roofType="Gable", roofPitch=30
        )
        entry = DesignEntry(
            id=1, imageUrl="/x.svg", promptText="t", parameters=params
        )
        ctx = _make_ctx([entry])
        result = _run(generate_dxf(ctx, 1))
        assert "DXF generated" in result
        assert "design 1" in result
        stored = ctx.deps.state.designs[0].dxfContent
        assert stored is not None
        decoded = base64.b64decode(stored)
        assert len(decoded) > 0

    def test_dxf_content_is_real_dxf_bytes(self):
        params = DesignParameters(
            floorPlanDimensions="8x12m", roofType="Hip", roofPitch=25
        )
        entry = DesignEntry(
            id=2, imageUrl="/y.svg", promptText="hip", parameters=params
        )
        ctx = _make_ctx([entry])
        _run(generate_dxf(ctx, 2))
        decoded = base64.b64decode(ctx.deps.state.designs[0].dxfContent)
        decoded_str = decoded.decode("utf-8", errors="replace")
        assert "0\nSECTION" in decoded_str or "SECTION" in decoded_str


class TestDesignIdNotFound:
    def test_returns_error_for_missing_id(self):
        ctx = _make_ctx([])
        result = _run(generate_dxf(ctx, 999))
        assert result == "No design found with id 999."

    def test_no_state_mutation(self):
        params = DesignParameters(
            floorPlanDimensions="10x10m", roofType="Flat"
        )
        entry = DesignEntry(
            id=1, imageUrl="/a.svg", promptText="t", parameters=params
        )
        ctx = _make_ctx([entry])
        result = _run(generate_dxf(ctx, 42))
        assert "No design found" in result
        assert ctx.deps.state.designs[0].dxfContent is None


class TestNoParameters:
    def test_returns_error_when_parameters_none(self):
        entry = DesignEntry(id=1, imageUrl="/x.svg", promptText="t")
        ctx = _make_ctx([entry])
        result = _run(generate_dxf(ctx, 1))
        assert result == "Design 1 has no parameters. Collect parameters first."

    def test_no_dxf_content_set(self):
        entry = DesignEntry(id=3, imageUrl="/z.svg", promptText="empty")
        ctx = _make_ctx([entry])
        _run(generate_dxf(ctx, 3))
        assert ctx.deps.state.designs[0].dxfContent is None


class TestBuildDxfValueError:
    def test_invalid_roof_type_returns_error(self):
        params = DesignParameters(
            floorPlanDimensions="10x15m", roofType="Dome"
        )
        entry = DesignEntry(
            id=1, imageUrl="/x.svg", promptText="t", parameters=params
        )
        ctx = _make_ctx([entry])
        result = _run(generate_dxf(ctx, 1))
        assert result.startswith("Cannot generate DXF:")
        assert "Dome" in result

    def test_missing_floor_plan_dimensions_returns_error(self):
        params = DesignParameters(roofType="Gable")
        entry = DesignEntry(
            id=2, imageUrl="/x.svg", promptText="t", parameters=params
        )
        ctx = _make_ctx([entry])
        result = _run(generate_dxf(ctx, 2))
        assert result.startswith("Cannot generate DXF:")

    def test_no_dxf_content_stored_on_error(self):
        params = DesignParameters(
            floorPlanDimensions="10x15m", roofType="InvalidType"
        )
        entry = DesignEntry(
            id=5, imageUrl="/x.svg", promptText="t", parameters=params
        )
        ctx = _make_ctx([entry])
        _run(generate_dxf(ctx, 5))
        assert ctx.deps.state.designs[0].dxfContent is None
