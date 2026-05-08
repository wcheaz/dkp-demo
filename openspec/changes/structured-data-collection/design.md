## Context

This is a demo application for an AI-enabled truss/roof engineering assistant. The agent currently accepts freeform chat input with no structured parameter awareness. The frontend renders design cards via `DesignComponent` but has no data display for construction parameters.

The state synchronization architecture uses CopilotKit's `useCoAgent` hook. A critical constraint: **backend tool state mutations do not propagate to the frontend**. This was discovered during the `add_design_entry` implementation — the backend agent tool approach was abandoned in favor of frontend tools registered via `useFrontendTool` that call `setState` directly (see commented-out code in `agent/src/agent.py:326-342` and active frontend tool in `src/app/page.tsx:328-343`).

The parameter model is derived from 33 real construction projects (see `hidden/DEMO-STRUCTURED-DATA.md`). Four fields are required for a valid design request: building type, floor plan dimensions, roof type, and roof pitch. Five additional fields are optional.

## Goals / Non-Goals

**Goals:**
- Define a typed `DesignParameters` model shared between backend and frontend
- Agent iteratively collects required parameters by detecting missing fields and prompting the user
- Frontend displays collected parameters in a utilitarian panel for demo visibility
- Parameters propagate correctly from agent tool calls to the frontend UI

**Non-Goals:**
- Simulated design generation from parameters (separate change)
- Pricing/cost estimation (separate change)
- Design reset flow (separate change)
- Polished UI styling
- Persistence across page reloads

## Decisions

### D1: Frontend tool for parameter updates (not backend tool)

Use `update_design_parameters` as a **frontend tool** registered via `useFrontendTool` in `src/app/page.tsx`, not a backend `@agent.tool`.

**Why**: Backend tool state mutations on `ctx.deps.state` do not propagate to the frontend via CopilotKit's `useCoAgent`. This is the same constraint that caused `add_design_entry` to be implemented as a frontend tool. Using a frontend tool ensures `setState` is called directly, triggering a React re-render.

**Alternative considered**: Backend tool that modifies `ctx.deps.state.parameters`. Rejected because state changes are invisible to the frontend.

**Tool contract**:
- Accepts partial parameter updates as individual arguments (one per field)
- Merges provided fields into current `state.parameters`
- Returns a summary string listing: (a) updated values, (b) remaining missing required fields, (c) whether all required fields are complete
- This return value guides the agent's next action — ask for missing fields or confirm with the user

### D2: Parameter model shape

Both backend and frontend use the same field names and structure:

```python
# Backend: agent/src/agent.py
class DesignParameters(BaseModel):
    buildingType: Optional[str] = None         # Required
    floorPlanDimensions: Optional[str] = None   # Required - e.g. "10x15m"
    roofType: Optional[str] = None              # Required - Gable|Hip|Mono-pitch|Flat
    roofPitch: Optional[int] = None             # Required - degrees (2-45)
    atticUsage: Optional[str] = None            # Optional - None|Storage|Living space
    eavesShape: Optional[str] = None            # Optional - Open|Boxed|Flush
    wallConstruction: Optional[str] = None      # Optional - Brick|SIP panels|Concrete block|Mixed
    location: Optional[str] = None              # Optional - e.g. "Bratislava"
    overhang: Optional[str] = None              # Optional - e.g. "450mm"
```

```typescript
// Frontend: src/lib/types.ts
export interface DesignParameters {
  buildingType?: string;
  floorPlanDimensions?: string;
  roofType?: string;
  roofPitch?: number;
  atticUsage?: string;
  eavesShape?: string;
  wallConstruction?: string;
  location?: string;
  overhang?: string;
}
```

**Required fields**: `buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`
**Optional fields**: `atticUsage`, `eavesShape`, `wallConstruction`, `location`, `overhang`

**Why all Optional with None/null defaults**: The model starts empty and is filled incrementally. Required vs. optional is enforced by validation logic, not by the type system, because partial state is the normal intermediate state.

### D3: parametersComplete is computed, not stored

`parametersComplete` is not a field on the model. It is computed by checking that all four required fields are non-null and non-empty.

The `update_design_parameters` frontend tool computes this and includes it in its return string. The frontend `DesignComponent` computes it for display purposes.

**Why not stored**: Avoids a stale-flag bug where the flag could get out of sync with actual field values.

### D4: Agent system prompt drives the collection loop

The system prompt instructs the agent to:

1. On each user message, extract any parameter values from the text
2. Call `update_design_parameters` with whatever fields were extracted
3. Read the tool's return value to see which required fields are still missing
4. If required fields are missing → ask the user for them specifically, listing the missing field names and valid options
5. If all required fields are present → summarize the collected parameters and ask the user to confirm before proceeding

The prompt includes the list of required fields, valid values for each, and explicit instructions to NOT proceed to design-related discussion until all required fields are confirmed.

**Why prompt-driven rather than code-enforced**: The LLM is the natural parser for freeform user input. A code-level validation gate would require a separate validation endpoint and would not improve reliability — the LLM must interpret the user's natural language regardless. The tool return value provides the feedback signal the LLM needs.

### D5: Parameter display as a section within DesignComponent

Add a parameter display section inside `DesignComponent` (not a separate component). It renders above the design cards when `state.parameters` exists.

Display format:
- Title: "Design Parameters"
- Each field on its own line: `Label: value` or `Label: —`
- Missing required fields shown as `Label: ⚠ Required` with distinct styling
- No collapsible sections, no modals — just a flat list
- For demo/testing purposes only — utilitarian, not polished

**Why inside DesignComponent vs separate**: Keeps the rendering logic co-located with the other state-driven display. The design component area is the natural place for all design-related state visibility. A separate component would add unnecessary indirection for a demo feature.

### D6: useCopilotReadable includes parameters

Update the existing `useCopilotReadable` call in `src/app/page.tsx` to include `state.parameters` in its serialized value. This ensures the agent can see the current parameter state when planning its next response.

## Risks / Trade-offs

**LLM may skip calling the update tool** → The system prompt uses strong mandatory language (matching the pattern from `design-auto-creation`). The tool return value provides a feedback signal. If the LLM still skips it, the parameter display panel will show stale data, making the failure visible to the demo presenter.

**LLM may misparse user input** → Acceptable for a demo. The parameter model uses string types for most fields (not enums), so the LLM has flexibility in interpretation. The confirmation step before proceeding gives the user a chance to correct errors.

**Frontend tool approach adds latency** → Each `update_design_parameters` call requires a round-trip through the CopilotKit framework. For a demo, this latency is negligible and acceptable.

**No input validation on field values** → Roof pitch accepts any integer, floor plan dimensions accept any string. For a demo, strict validation is not required. The agent's system prompt lists valid value ranges as guidance.
