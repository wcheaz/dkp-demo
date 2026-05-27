## 1. Freeze shared contract — dxfContent field on DesignEntry

- [x] 1.1 Add `dxfContent: Optional[str] = None` to the Python `DesignEntry` Pydantic model and the TypeScript `DesignEntry` interface
  - Scope: `agent/src/agent.py` (Python model), `src/lib/types.ts` (TypeScript interface)
  - Change: Both models gain a `dxfContent` field with `None`/`undefined` default so existing entries and constructors are unaffected.
  - Done when:
    - `agent/src/agent.py` `DesignEntry` class has `dxfContent: Optional[str] = None`
    - `src/lib/types.ts` `DesignEntry` interface has `dxfContent?: string`
    - `cd agent && python -c "from src.agent import DesignEntry; e = DesignEntry(id=1, imageUrl='/x.svg', promptText='t'); assert e.dxfContent is None"` exits 0
    - `npx tsc --noEmit` exits 0
  - Stop and hand off if: `npx tsc --noEmit` shows type errors in unrelated files that block compilation.

## 2. Agent tool — generate_dxf

- [x] 2.1 Implement the `generate_dxf` agent tool in `agent/src/agent.py`
  - Scope: `agent/src/agent.py`, `test/test_generate_dxf.py`
  - Change: New `@agent.tool` + `@_timed_tool` function `generate_dxf(ctx, design_id: int) -> str` that looks up the design entry by ID, calls `dxf_builder.build_dxf(entry.parameters)`, base64-encodes the result, stores it in `entry.dxfContent`, and returns a confirmation string. Handles three error cases: ID not found, no parameters, and `ValueError` from `build_dxf`.
  - Done when:
    - `agent/src/agent.py` contains `async def generate_dxf(ctx: RunContext[StateDeps], design_id: int) -> str` decorated with both `@agent.tool` and `@_timed_tool`
    - The tool's docstring documents the `design_id` parameter
    - `from src.agent import agent; tool_names = [t.name for t in agent.tool_defs]; assert "generate_dxf" in tool_names` succeeds
    - `cd agent && python -c "import base64; from src.agent import DesignEntry, DesignParameters; from src.dxf_builder import build_dxf; params = DesignParameters(floorPlanDimensions='10x15m', roofType='Gable', roofPitch=30); entry = DesignEntry(id=1, imageUrl='/x.svg', promptText='t', parameters=params); dxf_bytes = build_dxf(params); b64 = base64.b64encode(dxf_bytes).decode('ascii'); assert b64 == base64.b64encode(dxf_bytes).decode('ascii')"` exits 0
  - Stop and hand off if: `dxf_builder.build_dxf` signature has changed since Phase 2 and the call does not match.

- [x] 2.2 Write tests for `generate_dxf` tool logic in `test/test_generate_dxf.py`
  - Scope: `test/test_generate_dxf.py`
  - Change: Unit tests covering: (a) successful DXF generation for a design with complete parameters, verifying `dxfContent` is set to valid base64, (b) error return when design ID not found, (c) error return when design has no parameters, (d) error return when `build_dxf` raises `ValueError` for invalid roofType. Tests instantiate `YourState` with mock `DesignEntry` objects, construct `StateDeps`, and call the tool function directly.
  - Done when:
    - `pytest test/test_generate_dxf.py` exits 0 with all tests passing
    - Tests cover all 4 scenarios listed above
  - Stop and hand off if: The tool function cannot be called outside the agent context without a `RunContext` mock and no test pattern exists in `test/test_reset_design.py` to follow.

## 3. Starlette endpoint — POST /api/dxf/generate

- [x] 3.1 Add `POST /api/dxf/generate` route to `agent/src/main.py`
  - Scope: `agent/src/main.py`
  - Change: New async route handler that accepts JSON body, constructs a `DesignParameters` model, calls `build_dxf(params)`, and returns `Response` with `content=dxf_bytes`, `media_type="application/dxf"`, and `Content-Disposition: attachment; filename="design.dxf"` header. Catches `ValueError` from `build_dxf` → HTTP 400 JSON `{"error": message}`. Malformed JSON → HTTP 422. Route registered via `app.router.add_route("/api/dxf/generate", handler, methods=["POST"])`.
  - Done when:
    - `agent/src/main.py` contains the route handler and registration
    - `cd agent && python -c "from src.main import app; routes = [r.path for r in app.router.routes if hasattr(r, 'path')]; assert '/api/dxf/generate' in routes"` exits 0
  - Stop and hand off if: The Starlette app setup in `main.py` uses a pattern that prevents adding routes after `to_ag_ui()`.

- [x] 3.2 Write endpoint tests in `test/test_dxf_endpoint.py`
  - Scope: `test/test_dxf_endpoint.py`
  - Change: Tests using Starlette's test client (`httpx` or `requests` via `ASGITransport`) covering: (a) valid request returns 200 with DXF content and correct headers, (b) missing roofType returns 400 with error JSON, (c) invalid roofType returns 400, (d) malformed JSON returns 422, (e) minimal flat-roof request returns 200 with valid DXF.
  - Done when:
    - `pytest test/test_dxf_endpoint.py` exits 0 with all tests passing
    - Tests verify `Content-Type` and `Content-Disposition` headers on success responses
  - Stop and hand off if: The `to_ag_ui()` app cannot be tested with standard ASGI test clients without a full CopilotKit protocol handshake.

## 4. System prompt update

- [ ] 4.1 Add `generate_dxf` to the tool catalog in `_BASE_PROMPT`
  - Scope: `agent/src/agent.py` (the `_BASE_PROMPT` string)
  - Change: Add `- generate_dxf: Generate a downloadable DXF CAD file for a completed design.` to the tool catalog section. Add a trigger instruction: call `generate_dxf` after `generate_design` completes with all required parameters, or when the user explicitly requests a DXF/CAD file. Preserve all 7 existing tool catalog entries unchanged.
  - Done when:
    - `_BASE_PROMPT` contains the string `generate_dxf` in the tool catalog section
    - `_BASE_PROMPT` still contains all 7 original tool names: `get_knowledge_summary`, `query_knowledge_base`, `generate_design`, `modify_design_entry`, `update_design_parameters`, `generate_quote`, `reset_design`
    - `cd agent && python -c "from src.agent import _BASE_PROMPT; assert 'generate_dxf' in _BASE_PROMPT"` exits 0
  - Stop and hand off if: The skill file (`run-generate-design`) already adds `generate_dxf` to the prompt dynamically, making the base prompt addition redundant or conflicting.

## 5. Integrated quality gate

- [ ] 5.1 Run full Python test suite and TypeScript typecheck
  - Scope: no code edits; verification only
  - Change: Confirm all new and existing tests pass and the TypeScript build succeeds with the new `dxfContent` field.
  - Done when:
    - `pytest test/` exits 0
    - `npx tsc --noEmit` exits 0
  - Stop and hand off if: Pre-existing test failures are found that are unrelated to this change. Record the failure names and hand off for triage.
