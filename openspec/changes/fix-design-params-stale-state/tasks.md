## 1. Frontend: Remove stale-state workarounds

- [x] 1.1 Remove `latestStateRef` declaration, the `useEffect(() => { latestStateRef.current = state })` sync, the cleanup `useEffect` for `generationTimerRef`, and all `latestStateRef.current` reads from the three `useFrontendTool` handlers in `src/app/page.tsx`. The handlers shall read `state` directly from the `useCoAgent` closure. The `generationTimerRef` for the `setTimeout` cleanup SHALL remain.
  - Note: Removing the ref was premature — `useFrontendTool` captures a stale closure. Task 7 restores the ref with synchronous updates.
  - Done when: grep for `latestStateRef` in `src/app/page.tsx` returns zero matches; `npm run lint` passes.

## 2. Frontend: Remove global parameters from AgentState

- [x] 2.1 Remove the `parameters: DesignParameters` field from the `AgentState` type in `src/lib/types.ts`. Remove `parameters: {}` from the `useCoAgent` `initialState` object in `src/app/page.tsx`. Update the `useCopilotReadable` call to serialize only `designs` (remove `parameters: state.parameters`). Remove any remaining references to `state.parameters` in `src/app/page.tsx`.
  - Done when: `AgentState` has exactly one field (`designs: DesignEntry[]`); `useCoAgent` `initialState` has no `parameters` key; `useCopilotReadable` `value` does not reference `state.parameters`; `npm run lint` passes.

## 3. Frontend: Rewrite generate_design to accept parameters directly

- [x] 3.1 Add the 9 optional parameter arguments (`building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`, `attic_usage`, `eaves_shape`, `wall_construction`, `location`, `overhang`) to the `generate_design` `useFrontendTool` parameters array in `src/app/page.tsx`. Update the handler to construct `DesignEntry.parameters` from these arguments instead of reading from any global state. Use the `roof_type` argument (not state) for the `ROOF_TYPE_IMAGE_MAP` lookup. The handler reads `state.designs` from the `useCoAgent` closure to compute the next ID.
  - Done when: `generate_design` handler body does not reference `state.parameters` or `latestStateRef`; the tool parameters array includes all 9 fields marked as `required: false`; `npm run lint` passes.

## 4. Frontend: Convert update_design_parameters to a pure diagnostic tool

- [x] 4.1 Rewrite the `update_design_parameters` handler in `src/app/page.tsx` to be a pure function: compute the summary of provided fields and missing required fields from the tool's own arguments only. Remove the `setState` call, the backfill logic that overwrites existing `DesignEntry.parameters`, and all reads of `state.designs` or `state.parameters`. The handler returns the summary string and performs no state mutations.
  - Done when: `update_design_parameters` handler body contains zero `setState` calls and zero references to `state.designs` or `state.parameters`; the return value still lists updated fields and missing required fields; `npm run lint` passes.

## 5. Backend: Remove global parameters from YourState

- [x] 5.1 Remove the `parameters: DesignParameters = DesignParameters()` field from the `YourState` class in `agent/src/agent.py`. Keep the `DesignParameters` class itself (still used by `DesignEntry.parameters`). Remove any code that references `state.parameters` or mutates the global parameters field.
  - Done when: `YourState` class has no `parameters` field; `DesignParameters` class still exists; `agent` passes linting.

## 6. Backend: Update agent system prompt

- [x] 6.1 Update the `system_prompt` in `agent/src/agent.py` to instruct the agent to: (1) call `update_design_parameters` with extracted values to check completeness, (2) pass ALL collected parameter fields directly to `generate_design` as arguments when generating a design. Update the `generate_design` tool description to list the 9 parameter arguments. Preserve all existing tool references (`get_knowledge_summary`, `query_knowledge_base`, `modify_design_entry`, `download_test_image`, `update_design_parameters`).
  - Done when: system prompt contains `generate_design` with instructions to pass params directly; system prompt still references all 5 other tools; agent starts without errors.

## 7. Fix stale-closure bugs in all useFrontendTool handlers and setTimeout callback

The previous fix for task 7 introduced a functional `setState((prevState) => ...)` updater on line 370, but `useCoAgent`'s `setState` does NOT support functional updaters — it expects a full `AgentState` object, not a function. This silently fails, causing designs to vanish.

Additionally, removing `latestStateRef` in task 1.1 was premature. `useFrontendTool` registers handlers once and the closure captures the initial `state`. Without a ref, every handler that reads `state` or `state.designs` gets stale data. The parameter-specific state problem is solved (params come from tool arguments), but the **designs array** still needs fresh state access for:
- `generate_design`: computing the next ID from the current designs list
- `modify_design_entry`: finding the target design by ID
- The `setTimeout` callback: resolving processing→complete without clobbering other designs

The correct fix is to restore `latestStateRef` with synchronous updates after each `setState` call, AND use it in the `setTimeout` callback. This works because:
- The ref is updated synchronously after `setState`, so sequential handler calls see the latest designs.
- The `useEffect(() => { latestStateRef.current = state })` that syncs from `useCoAgent` only fires after render, so it does NOT clobber the ref between synchronous handler calls.
- The `setTimeout` callback fires 3 seconds later, by which time the `useEffect` has synced the ref to the true current state.

- [ ] 7.1 Restore `latestStateRef` in `src/app/page.tsx`: add `const latestStateRef = useRef(state)` and `useEffect(() => { latestStateRef.current = state })`. Update ALL three `useFrontendTool` handlers (`generate_design`, `modify_design_entry`) to read state via `latestStateRef.current` instead of the closure-captured `state`. After each `setState(newState)` call, immediately set `latestStateRef.current = newState` to keep the ref in sync for rapid sequential tool calls. Remove the broken functional `setState((prevState) => ...)` call in the `setTimeout` callback and replace with a ref-based read: `const timerState = latestStateRef.current`. Ensure the `generationTimerRef` cleanup `useEffect` remains. The `update_design_parameters` handler needs no changes (it is already a pure function with no state access).
  - Done when: designs appear when generated; designs persist through the processing→complete lifecycle; `generate_design` and `modify_design_entry` handlers read state only from `latestStateRef.current`; `npm run lint` passes.

## 8. Verification

- [ ] 8.1 Run `npm run lint` and verify zero errors in `src/app/page.tsx` and `src/lib/types.ts`. Verify no references to `state.parameters` remain in `src/app/page.tsx`. Verify `AgentState` in `src/lib/types.ts` has exactly one field (`designs`). Verify designs persist through the processing→complete lifecycle without vanishing.
  - Done when: `npm run lint` exits zero; `grep -c "state.parameters" src/app/page.tsx` returns 0; designs remain visible after the 3-second generation delay resolves.
