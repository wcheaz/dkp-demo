## 1. State Foundation

- [ ] 1.1 Add `parameters` to `AgentState` and make `update_design_parameters` persist to state

  Add a `parameters?: DesignParameters` field to `AgentState` in `src/lib/types.ts`. Update the `update_design_parameters` handler in `src/app/page.tsx` to merge provided fields into `AgentState.parameters` via `setState`. Update the `useCopilotReadable` hook value from `{ designs }` to `{ designs, parameters }` so the agent can observe session-level parameters.

  Done when:
  - `AgentState` in `src/lib/types.ts` contains a `parameters` field
  - Calling `update_design_parameters` with any field merges it into `AgentState.parameters` (previous fields preserved, new fields added)
  - `useCopilotReadable` exposes `{ designs, parameters }`
  - Existing `update_design_parameters` return value format is unchanged (summary string)
  - `npm run build` passes with no type errors

  Stop and hand off if:
  - Adding `parameters` to `AgentState` causes type errors in `DesignComponent` or other consumers that reference `AgentState`

## 2. reset_design Frontend Tool

- [ ] 2.1 Implement `reset_design` frontend tool

  Add a new `useFrontendTool` registration for `reset_design` in `src/app/page.tsx` (after the existing `update_design_parameters` tool). The tool accepts three optional parameters: `design_ids` (number array — IDs to remove, omit = remove all), `clear_parameters` (string array — parameter keys to clear from `AgentState.parameters`), `clear_all_parameters` (boolean, default false — clear all params, takes precedence over `clear_parameters`).

  Valid `clear_parameters` values are: `buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`, `atticUsage`, `eavesShape`, `wallConstruction`, `location`, `overhang`.

  Error handling: if any ID in `design_ids` is not found, return an error string listing valid IDs with no state mutation. If any key in `clear_parameters` is invalid, return an error string listing valid keys with no state mutation.

  Return a summary string containing: designs removed count + IDs, parameters cleared, remaining designs count, remaining parameter key=value pairs.

  Done when:
  - Tool is registered via `useFrontendTool` with name `reset_design`
  - Full reset (no args or `clear_all_parameters: true`) removes all designs and clears all parameters
  - `design_ids: [1, 3]` removes only those entries, leaves parameters unchanged
  - `clear_parameters: ["floorPlanDimensions", "roofPitch"]` clears only those fields, leaves designs unchanged
  - Compound call (`design_ids` + `clear_parameters`) does both operations atomically
  - `clear_all_parameters: true` takes precedence over `clear_parameters`
  - Invalid design IDs return error with no state mutation
  - Invalid parameter keys return error with no state mutation
  - `npm run build` passes

  Stop and hand off if:
  - The `useFrontendTool` API does not support array-type parameters — document the limitation and propose an alternative shape

## 3. Agent System Prompt

- [ ] 3.1 Add `reset_design` documentation to agent system prompt

  Add a `- reset_design:` section to the system prompt string in `agent/src/agent.py`, after the existing `- update_design_parameters:` section and in the same tool documentation block as `modify_design_entry`. Include parameter descriptions, the valid `clear_parameters` field names, and usage rules distinguishing selective clearing from full reset.

  Done when:
  - System prompt contains the string `reset_design`
  - System prompt contains `clear_parameters`, `clear_all_parameters`, and `design_ids`
  - System prompt lists all 9 valid parameter field names
  - System prompt includes rules for selective vs. full reset usage
  - `reset_design` section appears in the same tool documentation block as `modify_design_entry`

  Stop and hand off if:
  - The system prompt string has grown too long and the agent's tool selection accuracy degrades (flag for prompt engineering review)

## 4. Verification

- [ ] 4.1 Write tests for `reset_design` tool behavior

  Create `test/test_reset_design.py` in the project `test/` directory. Test the core behavior scenarios: full reset, selective design removal, selective parameter clearing, compound operations, error cases for invalid IDs and invalid parameter keys, and `clear_all_parameters` precedence.

  Done when:
  - Test file exists at `test/test_reset_design.py`
  - Tests cover: full reset, selective design removal, selective parameter clearing, compound reset, invalid design ID error, invalid parameter key error, `clear_all_parameters` precedence over `clear_parameters`
  - All tests pass

  Stop and hand off if:
  - The frontend tool handlers cannot be tested in isolation from the React component lifecycle — document what can be unit-tested vs. what requires browser/E2E testing
