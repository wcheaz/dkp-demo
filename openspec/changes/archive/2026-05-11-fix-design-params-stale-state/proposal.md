## Why

When generating multiple designs in a single session, Design #2 always inherits the structured-field parameters from Design #1 instead of its own. The root cause is architectural: `generate_design` copies parameters from a single shared global `state.parameters` object, creating an unavoidable race condition with `useCoAgent`'s async state sync. Refs and backfill logic cannot reliably solve this because `useCoAgent` round-trips state through the agent backend, causing the `useEffect` that updates the ref to overwrite the manually-set value with stale data.

## What Changes

- **BREAKING**: `generate_design` frontend tool will accept all 9 parameter fields directly as arguments instead of reading from `state.parameters`. The agent must pass the specific parameters for each design at call time.
- **BREAKING**: The `update_design_parameters` handler will no longer backfill parameters onto existing design entries. Each design entry's parameters are set once at creation time by the agent's `generate_design` call and never overwritten by the global state.
- Remove `latestStateRef` and the associated `useEffect` workaround — these were band-aids for the stale-state problem that cannot fully solve it.
- Remove the global `state.parameters` field from `AgentState`. Parameter state lives exclusively on individual `DesignEntry.parameters`. The `update_design_parameters` tool still exists for the agent's collection-loop workflow (it reports missing required fields), but it no longer mutates any persistent state.
- Update the agent system prompt to instruct the agent to pass all collected parameters directly to `generate_design`.

## Non-goals

- Changing the UI rendering of parameters on design cards (already works correctly per-entry).
- Adding parameter editing after design creation (out of scope for this change).
- Modifying the agent's parameter collection loop flow (the agent still collects params iteratively via `update_design_parameters` — only the final handoff to `generate_design` changes).

## Capabilities

### New Capabilities

- `design-params-self-contained`: Each `generate_design` call receives its own parameter fields directly. No parameter data is read from or written to global shared state during design creation. Parameters are self-contained on each `DesignEntry`.

### Modified Capabilities

- `design-auto-creation`: The `generate_design` tool signature changes to accept parameter fields. The handler no longer reads `state.parameters` or uses ref-based state access.
- `structured-params-collection`: `update_design_parameters` becomes a read-only diagnostic tool that reports missing required fields to the agent. It no longer persists parameters to global state or backfills onto design entries.

## Impact

- **Frontend**: `src/app/page.tsx` — rewrite of `generate_design` handler (new parameter arguments, remove global-state reads), simplification of `update_design_parameters` handler (remove backfill, remove state persistence), removal of `latestStateRef` and associated `useEffect`.
- **Frontend types**: `src/lib/types.ts` — remove `parameters` from `AgentState` (or keep as empty placeholder for future use). `DesignEntry.parameters` remains unchanged.
- **Agent backend**: `agent/src/agent.py` — update system prompt to instruct the agent to pass parameters directly to `generate_design`. Update `YourState` to remove or deprecate the `parameters` field. `DesignEntry` model unchanged.
- **Existing specs**: `design-params-display` requires no changes (renders per-entry params, which are unchanged). `design-entry-model` requires no changes (`DesignEntry` shape unchanged).
