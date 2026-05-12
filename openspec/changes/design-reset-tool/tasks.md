## 1. State Foundation

- [x] 1.1 Add `parameters` to `AgentState` and make `update_design_parameters` persist to state

  Add a `parameters?: DesignParameters` field to `AgentState` in `src/lib/types.ts`. Update the `update_design_parameters` handler in `src/app/page.tsx` to merge provided fields into `AgentState.parameters` via `setState`. Update the `useCopilotReadable` hook value from `{ designs }` to `{ designs, parameters }` so the agent can observe session-level parameters.

  Done when:
  - `AgentState` in `src/lib/types.ts` contains a `parameters` field
  - Calling `update_design_parameters` with any field merges it into `AgentState.parameters` (previous fields preserved, new fields added)
  - `useCopilotReadable` exposes `{ designs, parameters }`
  - Existing `update_design_parameters` return value format is unchanged (summary string)
  - `npm run build` passes with no type errors

  Stop and hand off if:
  - Adding `parameters` to `AgentState` causes type errors in `DesignComponent` or other consumers that reference `AgentState`

## 2. Design In Progress Placeholder

- [ ] 2.1 Create placeholder SVG and update DesignComponent to gate image on parameter completeness

  Create `public/design-in-progress.svg` — a placeholder image displaying "Design In Progress" with muted styling consistent with the design card aesthetic.

  Update the image rendering logic in `src/components/design-component.tsx` (currently at lines 76-89). After the `status === "processing"` spinner check, add a parameter completeness check: if ANY parameter field on the entry is undefined, null, empty string, or `"---"`, render the placeholder image (`/design-in-progress.svg`) instead of `entry.imageUrl`. Only render `entry.imageUrl` when ALL parameters are filled with real values. The placeholder image SHALL NOT open the modal on click.

  Done when:
  - `public/design-in-progress.svg` exists and renders "Design In Progress" text
  - Entry with incomplete parameters (any field missing or `"---"`) shows `/design-in-progress.svg` instead of `entry.imageUrl`
  - Entry with all parameters filled shows `entry.imageUrl` as before
  - Entry with `status: "processing"` still shows spinner (unchanged)
  - Entry with no parameters (`undefined` or `{}`) shows placeholder
  - Placeholder image click does not open the modal
  - `npm run build` passes

  Stop and hand off if:
  - The parameter completeness check causes performance issues with many entries (flag for memoization)

## 3. reset_design Frontend Tool

- [ ] 3.1 Implement `reset_design` frontend tool — partial reset and full scrap

  Add a new `useFrontendTool` registration for `reset_design` in `src/app/page.tsx` (after the existing `update_design_parameters` tool). The tool accepts five optional parameters:
  - `design_ids` (number array) — IDs to reset; omit = all designs
  - `remove_designs` (boolean, default false) — true = remove entries entirely (full scrap)
  - `clear_parameters` (string array) — param keys to set to `"---"` on targeted entries
  - `clear_all_parameters` (boolean, default false) — set ALL entry params to `"---"`
  - `clear_session_parameters` (string array) — param keys to clear from `AgentState.parameters`

  Valid parameter keys: `buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`, `atticUsage`, `eavesShape`, `wallConstruction`, `location`, `overhang`.

  **When `remove_designs` is false (partial reset — default)**:
  - Keep targeted entries in the list
  - Set specified parameter fields to `"---"` (via `clear_parameters` or `clear_all_parameters`)
  - Preserve all other parameters and `promptText`
  - Do NOT modify `entry.imageUrl` — the UI will automatically show the "Design In Progress" placeholder for entries with `"---"` fields (handled by task 2.1)

  **When `remove_designs` is true (full scrap)**:
  - Remove targeted entries from the list entirely
  - Ignore `clear_parameters` and `clear_all_parameters`

  **Session-level clearing** (`clear_session_parameters`) operates independently — it clears specified keys from `AgentState.parameters` regardless of `remove_designs`.

  Error handling: if any ID in `design_ids` is not found, return error with valid IDs, no state mutation. If any key in `clear_parameters` or `clear_session_parameters` is invalid, return error with valid keys, no state mutation.

  Done when:
  - Tool registered via `useFrontendTool` with name `reset_design`
  - Partial reset: entry stays, specified params set to `"---"`, others preserved
  - No-op reset (no `clear_parameters`): entry stays unchanged
  - Full scrap (`remove_designs: true`): entry removed from list
  - Full scrap ignores `clear_parameters` and `clear_all_parameters`
  - `clear_all_parameters: true` sets all entry params to `"---"`
  - `clear_all_parameters` takes precedence over `clear_parameters`
  - `clear_session_parameters` clears session-level params independently
  - Compound call (entry reset + session clear) works atomically
  - Omitting `design_ids` targets all designs
  - Invalid design IDs return error with no state mutation
  - Invalid parameter keys return error with no state mutation
  - Return value is a human-readable summary matching the format in specs
  - `npm run build` passes

  Stop and hand off if:
  - The `useFrontendTool` API does not support array-type parameters — document the limitation and propose an alternative shape

## 4. Agent System Prompt

- [ ] 4.1 Add `reset_design` documentation to agent system prompt

  Add a `- reset_design:` section to the system prompt string in `agent/src/agent.py`, after the existing `- update_design_parameters:` section and in the same tool documentation block as `modify_design_entry`. Include parameter descriptions, the valid parameter field names, and usage rules distinguishing partial reset from full scrap. Note that the UI automatically shows a "Design In Progress" placeholder image when fields are cleared to `"---"`.

  Done when:
  - System prompt contains `reset_design`, `clear_parameters`, `clear_all_parameters`, `design_ids`, `remove_designs`, and `clear_session_parameters`
  - System prompt lists all 9 valid parameter field names
  - System prompt includes rules: default is partial reset (keep entry, clear fields to `"---"`); `remove_designs: true` only for explicit scrap requests; UI shows placeholder for incomplete params
  - `reset_design` section appears in the same tool documentation block as `modify_design_entry`

  Stop and hand off if:
  - The system prompt string has grown too long and the agent's tool selection accuracy degrades (flag for prompt engineering review)

## 5. Verification

- [ ] 5.1 Write tests for `reset_design` tool behavior

  Create `test/test_reset_design.py` in the project `test/` directory. Test the core behavior scenarios from the spec.

  Done when:
  - Test file exists at `test/test_reset_design.py`
  - Tests cover: partial reset (clear specific fields to `"---"`, preserved fields), no-op reset, full scrap, full scrap ignoring clear_parameters, clear_all_parameters precedence, session parameter clearing, compound reset + session clear, reset all designs via omitted design_ids, invalid design ID error, invalid parameter key error
  - All tests pass

  Stop and hand off if:
  - The frontend tool handlers cannot be tested in isolation from the React component lifecycle — document what can be unit-tested vs. what requires browser/E2E testing
