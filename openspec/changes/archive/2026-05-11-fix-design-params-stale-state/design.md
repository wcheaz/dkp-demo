## Context

The frontend uses CopilotKit's `useCoAgent` to share state between the React app and the Python agent. Currently, `AgentState` contains both a `designs` array and a global `parameters` object. When `generate_design` runs, it copies `state.parameters` onto the new `DesignEntry`. This creates a timing dependency: the agent must call `update_design_parameters` (to set global params) before `generate_design`, and both calls must fully propagate through `useCoAgent`'s async sync cycle before the next tool fires. In practice, tool calls arrive in rapid succession and the sync cycle cannot keep up, causing Design #2 to read stale Design #1 parameters from the ref or global state.

Previous attempts to fix this with `latestStateRef` + synchronous ref updates failed because `useCoAgent`'s `useEffect` overwrites the ref with the backend-synced `state`, which lags behind the frontend's local mutations.

## Goals / Non-Goals

**Goals:**
- Eliminate the race condition entirely by removing the dependency on global `state.parameters` during design creation.
- Each `DesignEntry` carries its own parameters, provided directly by the agent at `generate_design` call time.
- `update_design_parameters` remains useful to the agent's collection loop (reporting missing fields) but becomes stateless — it does not write to `AgentState`.

**Non-Goals:**
- Adding per-design parameter editing after creation.
- Changing how parameters render in the UI (`DesignComponent`).
- Modifying the agent's conversational flow for collecting parameters.

## Decisions

### Decision 1: `generate_design` accepts all 9 parameter fields as direct arguments

**Choice**: Add `building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`, `attic_usage`, `eaves_shape`, `wall_construction`, `location`, `overhang` as optional parameters to the `generate_design` tool, mirroring the signature of `update_design_parameters`.

**Rationale**: The agent already has the parameter values in its context when it decides to generate a design. Passing them directly eliminates the shared-state race condition entirely — no ref, no backfill, no global state dependency.

**Alternative considered**: Keep `generate_design` as-is and add a `design_id` parameter to `update_design_parameters` to support per-design writes. Rejected because it adds complexity (two calls to create one design) and still requires the agent to coordinate call ordering.

### Decision 2: `update_design_parameters` becomes a pure diagnostic tool

**Choice**: `update_design_parameters` no longer calls `setState`. It reads the current state solely to compute which required fields are missing, and returns that summary to the agent. It does not persist parameters anywhere.

**Rationale**: With parameters flowing directly through `generate_design`, there is no reason for `update_design_parameters` to write state. Keeping it as a read-only diagnostic preserves the agent's collection-loop workflow without introducing state mutations that could conflict.

**Alternative considered**: Remove `update_design_parameters` entirely. Rejected because the agent's system prompt and collection loop depend on its return value to know which required fields are still missing. Removing it would require a larger agent rewrite.

### Decision 3: Remove `parameters` from `AgentState`

**Choice**: Delete the `parameters: DesignParameters` field from `AgentState` (TypeScript) and `YourState` (Python). Remove `useCopilotReadable` serialization of parameters.

**Rationale**: With `update_design_parameters` no longer writing state and `generate_design` no longer reading it, the global `parameters` field has no consumers. Removing it eliminates dead state and prevents future accidental reliance on it.

**Alternative considered**: Keep `parameters` on `AgentState` but always leave it empty. Rejected because unused state fields invite bugs — a future change might read from it thinking it's populated.

### Decision 4: Remove `latestStateRef` and its `useEffect`

**Choice**: Delete `latestStateRef`, the `useEffect` that syncs it, and all `latestStateRef.current` reads from handler bodies.

**Rationale**: The ref was introduced solely to work around the stale-closure / stale-state problem for parameter reads. With parameters now coming from tool arguments, the only remaining state mutation is appending to `designs`. Since `generate_design` only needs the current designs list to compute the next ID, and tool handlers receive the latest `state` from `useCoAgent`'s closure on re-render, the ref is no longer necessary. If `useCoAgent` closures become stale for the designs array, that is a separate (and less critical) issue — the worst case is a duplicate ID, which the existing `useMemo` ID-backfill logic already corrects.

### Decision 5: Agent system prompt update

**Choice**: Update the agent's system prompt to instruct it to pass all collected parameters directly to `generate_design` when calling it, rather than relying on `update_design_parameters` to persist them first.

**Rationale**: The agent's current workflow is: collect params → call `update_design_parameters` (persists to state) → call `generate_design` (reads from state). The new workflow is: collect params → call `update_design_parameters` (diagnostic only, reports missing fields) → call `generate_design` (agent passes params directly). The agent still calls `update_design_parameters` to check completeness, but now also passes those same params to `generate_design`.

## Risks / Trade-offs

- **Risk**: Agent fails to pass params to `generate_design`, resulting in a design with no parameters displayed. → **Mitigation**: The system prompt explicitly instructs the agent to pass all collected params. The `generate_design` handler still accepts optional params — if none are provided, the entry simply has no params. This is a graceful degradation, not a crash.
- **Risk**: `useCoAgent` closures for the designs array could also go stale in rapid-fire scenarios, causing duplicate IDs. → **Mitigation**: The existing `useMemo` ID-backfill logic (lines 295-310 of `page.tsx`) already corrects null or duplicate IDs on re-render. This is sufficient because the visual impact of a duplicate ID is minor and self-correcting.
- **Trade-off**: The agent must now pass up to 9 extra arguments to `generate_design`, making the tool call larger. → **Acceptable**: LLM tool calls routinely handle this many parameters. The agent already constructs similarly-sized calls for `update_design_parameters`.
