## 1. Frontend: Remove stale-state workarounds

- [ ] 1.1 Remove `latestStateRef` declaration, the `useEffect(() => { latestStateRef.current = state })` sync, the cleanup `useEffect` for `generationTimerRef`, and all `latestStateRef.current` reads from the three `useFrontendTool` handlers in `src/app/page.tsx`. The handlers shall read `state` directly from the `useCoAgent` closure. The `generationTimerRef` for the `setTimeout` cleanup SHALL remain.
  - Done when: grep for `latestStateRef` in `src/app/page.tsx` returns zero matches; `npm run lint` passes.

## 2. Frontend: Remove global parameters from AgentState

- [ ] 2.1 Remove the `parameters: DesignParameters` field from the `AgentState` type in `src/lib/types.ts`. Remove `parameters: {}` from the `useCoAgent` `initialState` object in `src/app/page.tsx`. Update the `useCopilotReadable` call to serialize only `designs` (remove `parameters: state.parameters`). Remove any remaining references to `state.parameters` in `src/app/page.tsx`.
  - Done when: `AgentState` has exactly one field (`designs: DesignEntry[]`); `useCoAgent` `initialState` has no `parameters` key; `useCopilotReadable` `value` does not reference `state.parameters`; `npm run lint` passes.

## 3. Frontend: Rewrite generate_design to accept parameters directly

- [ ] 3.1 Add the 9 optional parameter arguments (`building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`, `attic_usage`, `eaves_shape`, `wall_construction`, `location`, `overhang`) to the `generate_design` `useFrontendTool` parameters array in `src/app/page.tsx`. Update the handler to construct `DesignEntry.parameters` from these arguments instead of reading from any global state. Use the `roof_type` argument (not state) for the `ROOF_TYPE_IMAGE_MAP` lookup. The handler reads `state.designs` from the `useCoAgent` closure to compute the next ID.
  - Done when: `generate_design` handler body does not reference `state.parameters` or `latestStateRef`; the tool parameters array includes all 9 fields marked as `required: false`; `npm run lint` passes.

## 4. Frontend: Convert update_design_parameters to a pure diagnostic tool

- [ ] 4.1 Rewrite the `update_design_parameters` handler in `src/app/page.tsx` to be a pure function: compute the summary of provided fields and missing required fields from the tool's own arguments only. Remove the `setState` call, the backfill logic that overwrites existing `DesignEntry.parameters`, and all reads of `state.designs` or `state.parameters`. The handler returns the summary string and performs no state mutations.
  - Done when: `update_design_parameters` handler body contains zero `setState` calls and zero references to `state.designs` or `state.parameters`; the return value still lists updated fields and missing required fields; `npm run lint` passes.

## 5. Backend: Remove global parameters from YourState

- [ ] 5.1 Remove the `parameters: DesignParameters = DesignParameters()` field from the `YourState` class in `agent/src/agent.py`. Keep the `DesignParameters` class itself (still used by `DesignEntry.parameters`). Remove any code that references `state.parameters` or mutates the global parameters field.
  - Done when: `YourState` class has no `parameters` field; `DesignParameters` class still exists; `agent` passes linting.

## 6. Backend: Update agent system prompt

- [ ] 6.1 Update the `system_prompt` in `agent/src/agent.py` to instruct the agent to: (1) call `update_design_parameters` with extracted values to check completeness, (2) pass ALL collected parameter fields directly to `generate_design` as arguments when generating a design. Update the `generate_design` tool description to list the 9 parameter arguments. Preserve all existing tool references (`get_knowledge_summary`, `query_knowledge_base`, `modify_design_entry`, `download_test_image`, `update_design_parameters`).
  - Done when: system prompt contains `generate_design` with instructions to pass params directly; system prompt still references all 5 other tools; agent starts without errors.

## 7. Verification

- [ ] 7.1 Run `npm run lint` and verify zero errors in `src/app/page.tsx` and `src/lib/types.ts`. Verify no references to `latestStateRef` or `state.parameters` remain in `src/app/page.tsx`. Verify `AgentState` in `src/lib/types.ts` has exactly one field (`designs`).
  - Done when: `npm run lint` exits zero; `grep -c "latestStateRef" src/app/page.tsx` returns 0; `grep -c "state.parameters" src/app/page.tsx` returns 0.
