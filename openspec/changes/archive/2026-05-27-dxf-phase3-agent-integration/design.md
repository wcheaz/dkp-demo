## Context

The DXF geometry engine (`agent/src/dxf_builder.py`) is complete (Phases 1-2). It exposes a single function `build_dxf(params: DesignParameters) -> bytes` that produces a valid DXF with five layers: `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, `Title_Block`. The agent (`agent/src/agent.py`) currently has no tool that calls this function, and the `DesignEntry` model has no field to carry DXF content. The Starlette app (`agent/src/main.py`) serves the agent via CopilotKit's `to_ag_ui()` and has one additional route (`/api/health`).

**Existing tool pattern**: All agent tools use `@agent.tool` + `@_timed_tool` decorators. They accept `ctx: RunContext[StateDeps]` as the first parameter and typed arguments for the rest. They return strings (agent-consumable results). Tools that modify state do so by mutating `ctx.deps.state` directly.

**Existing DesignEntry** (Python):
```python
class DesignEntry(BaseModel):
    id: int
    imageUrl: str
    promptText: str
    status: str = "complete"
    parameters: Optional[DesignParameters] = None
    price: Optional[int] = None
```

**Existing DesignEntry** (TypeScript):
```typescript
export interface DesignEntry {
  id: number;
  imageUrl: string;
  promptText: string;
  status?: "processing" | "complete";
  parameters?: DesignParameters;
  price?: number | "---";
  materialStats?: MaterialStats | null;
}
```

## Goals / Non-Goals

**Goals:**
- Expose DXF generation as an agent tool callable during a design session
- Carry DXF content in the shared state so the frontend can access it without a separate fetch
- Provide a standalone HTTP endpoint for direct DXF download (no agent loop required)
- Update the system prompt so the agent calls `generate_dxf` at the right time

**Non-Goals:**
- No frontend UI changes (Phase 4)
- No persistent file storage or `generated/` directory
- No async DXF generation or progress polling
- No changes to `dxf_builder.py`
- No CORS or proxy changes

## Decisions

### D1: DXF delivery via base64 in state (not file-based URL)

DXF content is base64-encoded and stored directly in `DesignEntry.dxfContent`. The frontend will decode and create Blob URLs for download.

- **Why**: Avoids file-system management, works through CopilotKit's state sync without additional HTTP endpoints, and keeps all design data self-contained in the state model. The agent and frontend share state through CopilotKit's existing infrastructure.
- **Alternative**: Write DXF to `agent/generated/` and serve via static route with a URL stored in `DesignEntry.dxfUrl`. Rejected because it requires file lifecycle management, CORS/proxy configuration between frontend and agent backend, and cleanup logic — all unnecessary for a demo.

### D2: `generate_dxf` tool matches DesignEntry by ID

The tool accepts `design_id: int` and looks up the matching entry in `ctx.deps.state.designs`. If found and the entry has complete parameters, it calls `build_dxf(entry.parameters)`, base64-encodes the result, stores it in `entry.dxfContent`, and returns a confirmation string.

- **Why**: The agent already tracks designs by ID. Matching by ID is unambiguous and matches the pattern used by `modify_design_entry` and `reset_design`.
- **Error cases**:
  - Design ID not found → return error string `"No design found with id {design_id}."`
  - Design has no parameters → return error string `"Design {design_id} has no parameters. Collect parameters first."`
  - `build_dxf()` raises `ValueError` (missing/invalid roofType or floorPlanDimensions) → catch and return error string `"Cannot generate DXF: {error_message}."`

### D3: Tool parameter shape — single `design_id` argument

The tool signature is `generate_dxf(ctx, design_id: int) -> str`. It reads parameters from the matched design entry rather than accepting separate parameter arguments.

- **Why**: Avoids duplicating the full `DesignParameters` argument list. The design entry already has the parameters collected by the parameter extraction loop. Passing only `design_id` keeps the tool call simple and reduces the chance of parameter mismatches between the state and the tool call.
- **Alternative**: Accept all `DesignParameters` fields as tool arguments. Rejected because the agent would need to re-pass every parameter it already stored, increasing token usage and error surface.

### D4: Starlette endpoint accepts DesignParameters JSON body

`POST /api/dxf/generate` accepts a JSON body matching the `DesignParameters` schema. It calls `build_dxf()` directly and returns raw DXF bytes with headers `Content-Type: application/dxf` and `Content-Disposition: attachment; filename="design.dxf"`.

- **Why**: Provides a clean HTTP API for direct DXF download without requiring the agent loop. Useful for: (a) frontend-initiated downloads, (b) external tool integration, (c) testing the DXF builder without running the agent.
- **Error handling**: If `build_dxf()` raises `ValueError`, return HTTP 400 with JSON `{"error": "<message>"}`. If the request body is malformed, return HTTP 422.
- **Alternative**: A GET endpoint with query parameters. Rejected because `DesignParameters` has 9 fields and GET query strings would be unwieldy and not RESTful for a generation action.

### D5: `dxfContent` field is Optional[str] with None default

Both the Python model and TypeScript interface add `dxfContent: Optional[str] = None` (`dxfContent?: string` in TypeScript). The field is excluded from the API response when `None`/`undefined`.

- **Why**: `None` default means no migration for existing entries. Frontend code that doesn't know about `dxfContent` continues to work unchanged.
- **Content**: A standard base64-encoded string (using Python's `base64.b64encode()`). No data URI prefix (`data:...`), no compression. The frontend wraps it as needed.

### D6: System prompt addition — one line in tool catalog

Add `- generate_dxf: Generate a downloadable DXF CAD file for a completed design.` to the tool catalog section of `_BASE_PROMPT`. Also add a trigger rule: `generate_dxf` should be called automatically after `generate_design` completes with all required parameters, or when the user explicitly requests a DXF/CAD file.

- **Why**: Minimal prompt change. The agent already knows the tool catalog pattern and the skill file (`run-generate-design`) can be updated separately to reference `generate_dxf` in the workflow.
- **Alternative**: Detailed multi-line instructions for DXF generation in the prompt. Rejected because the skill file already manages the design workflow and the tool docstring provides parameter guidance.

## Risks / Trade-offs

- **Risk**: Base64 encoding inflates DXF content by ~33%. A typical DXF for a 10x15m building is ~15-25 KB raw, ~20-34 KB base64. → Mitigation: Acceptable for a demo. State sync happens once per generation. No impact on real-time performance.
- **Risk**: `build_dxf()` raises `ValueError` if `roofType` or `floorPlanDimensions` is missing or invalid. → Mitigation: The tool catches `ValueError` and returns a human-readable error string. The agent can then ask the user for the missing parameter.
- **Risk**: Design parameters on the entry may be partially filled (some fields None). → Mitigation: `build_dxf()` already requires `roofType` and `floorPlanDimensions` and raises on missing values. The tool's error handling surfaces this to the agent.
- **Trade-off**: The Starlette endpoint bypasses the agent loop entirely and has no access to agent state. It generates DXF from the request body only. → Accepted; this is intentional. The endpoint is for direct API access, not for the agent-driven workflow.
- **Trade-off**: `dxfContent` in state means DXF data is lost on session reset or page reload. → Accepted; the TODO explicitly defers persistent storage and this matches the existing demo behavior for all other state.
