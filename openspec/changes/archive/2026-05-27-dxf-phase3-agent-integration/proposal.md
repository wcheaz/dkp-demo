## Why

The DXF geometry engine (`agent/src/dxf_builder.py`) produces complete CAD-ready drawings with floor plans, roof outlines, truss layouts, dimensions, and title blocks (Phases 1-2 complete). However, the agent cannot invoke DXF generation and the frontend has no way to receive or download DXF content. Phase 3 connects the existing geometry engine to the agent tool layer, the data model, and a backend serving endpoint so that users can generate and download CAD files during a design session.

## What Changes

- **New `generate_dxf` agent tool**: A `@agent.tool` in `agent/src/agent.py` that accepts design parameters, calls `dxf_builder.build_dxf()`, encodes the result as base64, and stores it in the matching `DesignEntry` via a new `dxfContent` field. Returns a confirmation string with file size and the design entry ID.
- **Extended `DesignEntry` model**: Add `dxfContent: Optional[str] = None` to the Python Pydantic model and the TypeScript `DesignEntry` interface. This field holds base64-encoded DXF content. The field is named `dxfContent` (not `dxfUrl`) because the chosen delivery approach is base64 inline in state, not file-based URL serving.
- **New Starlette endpoint `POST /api/dxf/generate`**: Accepts `DesignParameters` as JSON body, calls `build_dxf()`, and returns raw DXF bytes with `Content-Type: application/dxf` and `Content-Disposition: attachment`. This endpoint exists for direct frontend download and external tool integration independent of the agent tool path.
- **Updated system prompt**: Add `generate_dxf` to the tool catalog in `_BASE_PROMPT` so the agent knows to call it whenever a design completes with all required parameters.

## Capabilities

### New Capabilities

- `dxf-generation-tool`: Agent tool (`generate_dxf`) that generates DXF from `DesignParameters` via `dxf_builder.build_dxf()`, encodes as base64, stores in `DesignEntry.dxfContent`, and returns a confirmation. Uses the existing `_timed_tool` decorator pattern.
- `dxf-serve-endpoint`: Starlette POST route (`/api/dxf/generate`) that accepts `DesignParameters` JSON, calls `build_dxf()`, and returns raw DXF bytes as a downloadable response. Decoupled from the agent loop — callable directly from the frontend or external tools.

### Modified Capabilities

- `design-entry-model`: Adding `dxfContent: Optional[str] = None` field to both the Python Pydantic `DesignEntry` and the TypeScript `DesignEntry` interface. Default is `None` so existing entries are unaffected.
- `agent-system-prompt`: Adding `generate_dxf` to the tool catalog section of `_BASE_PROMPT` with a one-line description of when to call it.

## Non-goals

- No frontend CAD viewer or DXF rendering (Phase 4).
- No DXF download button or UI affordance in the design component (Phase 4).
- No file-system-based DXF storage or `generated/` directory. Delivery is base64 in state only.
- No changes to `dxf_builder.py` — the geometry engine is complete.
- No persistent DXF storage across sessions or page reloads.
- No DXF generation status indicator or async polling.
- No CORS configuration changes — the existing agent-to-frontend communication path (CopilotKit) is used for the agent tool path; the Starlette endpoint is same-origin or relies on existing proxy setup.

## Impact

- **Files modified**: `agent/src/agent.py` (new tool, model change, prompt update), `agent/src/main.py` (new route), `src/lib/types.ts` (TypeScript interface change).
- **API**: New `POST /api/dxf/generate` endpoint. New agent tool `generate_dxf`.
- **Dependencies**: No new Python or npm packages — uses existing `ezdxf`, `starlette`, and `base64` stdlib.
- **Backward compatibility**: `dxfContent` defaults to `None` — all existing `DesignEntry` instances and frontend code remain functional without migration.
