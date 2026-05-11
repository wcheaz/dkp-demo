## Why

The demo script (Steps 1–2) requires the AI assistant to iteratively collect construction parameters from the user — parsing partial input, detecting missing required fields, and prompting until all required data is gathered. Currently the agent accepts freeform input with no parameter validation, no structured state tracking, and no awareness of required vs. optional fields. Additionally, the design-components panel needs to display the collected structured data so the demo audience can see what parameters have been captured.

## What Changes

- Add a `DesignParameters` model to both backend (`YourState` in `agent/src/agent.py`) and frontend (`AgentState` in `src/lib/types.ts`) with typed fields for construction parameters: `buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch` (required), and `atticUsage`, `eavesShape`, `wallConstruction`, `location`, `overhang` (optional).
- Add a `parametersComplete` flag to state indicating all required fields are filled.
- Update the agent's system prompt to instruct it to check which required fields are missing after each user message and ask for them specifically before proceeding.
- Add a `parameters` field to `AgentState`/`YourState` so the frontend can reflect collected parameters.
- Add a utilitarian data display section to the design component area that lists the current structured parameter values. This is for demo/testing visibility — no polished styling required.

## Capabilities

### New Capabilities

- `structured-params-collection`: Agent-side parameter model, required/optional field definitions, iterative collection loop, missing-field detection, and confirmation-before-proceed behavior.
- `design-params-display`: Frontend rendering of collected structured parameters within the design component area. Utilitarian display — lists field names and values, shows which required fields are still missing.

### Modified Capabilities

- `design-display`: The design component area now also renders a structured-data panel alongside or above the design cards, showing the current parameter state.

## Non-goals

- Simulated design generation (generating mock design images from parameters) — separate future change.
- Pricing engine / cost estimation — separate future change.
- Design reset / do-over flow — separate future change.
- Polished or production-quality UI styling for the parameter display.
- Pamir API integration.
- Persisting parameters across page reloads.

## Scope

**First rollout**: Agent collects the 4 required fields (`buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`) iteratively. Optional fields are accepted if provided but not demanded. When all required fields are present, the agent confirms the parameters with the user before continuing. The frontend displays the current parameter state in the design component area with a simple key-value listing.

**Deferred**: Attic usage, eaves shape, wall construction, location, and overhang as required fields (remain optional). Design generation triggered by complete parameters. Parameter-driven image selection.

## Impact

- `agent/src/agent.py` — New `DesignParameters` model on `YourState`, updated system prompt for iterative collection.
- `src/lib/types.ts` — New `DesignParameters` interface and `parameters` field on `AgentState`.
- `src/components/design-component.tsx` — Add parameter display section.
- `src/app/page.tsx` — Pass parameters state to design component, update `useCopilotReadable` to include parameters.
