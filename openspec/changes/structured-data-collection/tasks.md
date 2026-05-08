## 1. Data Model

- [x] 1.1 Add DesignParameters model to backend and frontend, update state types and initial state
  Add `DesignParameters` Pydantic model (9 Optional fields) to `agent/src/agent.py`, add `parameters` field to `YourState`. Add `DesignParameters` TypeScript interface to `src/lib/types.ts`, add `parameters: DesignParameters` to `AgentState`. Update `useCoAgent` initialState in `src/app/page.tsx` to include `parameters: {}`.
  Done when: `AgentState` has `parameters: DesignParameters`, `YourState` has `parameters: DesignParameters`, `useCoAgent` initializes `parameters: {}`.
  Verify by: `npx tsc --noEmit` passes and `cd agent && python -c "from agent import YourState; s = YourState(); assert s.parameters.buildingType is None"`.
  Stop and hand off if: TypeScript or Python type errors cannot be resolved without changing the existing `DesignEntry` or `designs` field structure.

- [x] 1.2 Update useCopilotReadable to include parameters in serialized state
  Update the `useCopilotReadable` call in `src/app/page.tsx` to serialize both `designs` and `state.parameters` in its `value` field so the agent sees current parameter state.
  Done when: `useCopilotReadable` value includes `state.parameters` in its JSON serialization.
  Verify by: inspect `src/app/page.tsx` for `useCopilotReadable` and confirm `state.parameters` appears in the `value` field.

## 2. Parameter Collection Tool

- [x] 2.1 Register update_design_parameters frontend tool with parameter merge and missing-field summary
  Register a `useFrontendTool` named `update_design_parameters` in `YourMainContent` (`src/app/page.tsx`). The tool accepts optional string parameters for all 9 fields (`building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`, `attic_usage`, `eaves_shape`, `wall_construction`, `location`, `overhang`). The handler merges provided fields into `state.parameters` via `setState`, converting `roof_pitch` from string to number. Returns a string listing updated fields, missing required fields, and whether all required fields are complete.
  Done when: Tool is registered, merges partial updates, preserves existing values, handles undefined `state.parameters`, returns missing-required-fields summary.
  Verify by: `npx tsc --noEmit` passes.
  Stop and hand off if: CopilotKit frontend tool parameter types do not support optional string parameters — document the constraint and adjust the tool contract.

## 3. Agent Collection Prompt

- [x] 3.1 Update agent system prompt with structured data collection instructions
  Update the `system_prompt` in `agent/src/agent.py` to include: (1) the four required parameter fields and their valid values, (2) instruction to extract parameter values from user messages and call `update_design_parameters`, (3) instruction to check the tool return value for missing required fields and ask for them, (4) instruction to confirm all parameters with the user before proceeding to design-related discussion. Preserve all existing tool references (`get_knowledge_summary`, `query_knowledge_base`, `add_design_entry`, `modify_design_entry`).
  Done when: `system_prompt` contains `update_design_parameters`, lists all four required fields, includes collection-loop instructions, and preserves existing tool references.
  Verify by: `cd agent && python -m ruff check . && python -m mypy .` both exit zero.
  Stop and hand off if: The prompt becomes too long and causes model context issues — trim non-essential instructions and document what was removed.

## 4. Remove Existing Standalone Parameters Display

- [x] 4.1 Remove the current standalone parameter panel from DesignComponent
  The current implementation in `src/components/design-component.tsx` renders a standalone "Design Parameters" panel above the design cards that is NOT tied to any individual design entry. Remove this entire panel — the heading, the 9 label-value rows, and any related helper code. The design cards scrollable container should remain as-is. Do NOT remove the `DesignParameters` type or `state.parameters` — only remove the standalone display panel.
  Done when: DesignComponent no longer renders any parameter panel above the design cards. The component still renders design cards correctly. No standalone parameter display exists anywhere in the file.
  Verify by: Search `src/components/design-component.tsx` for "Design Parameters" or "parameters" rendering above the cards — there SHALL be none. `npx tsc --noEmit && npm run lint` both exit zero.
  Stop and hand off if: The standalone panel code is interleaved with design card rendering logic in a way that cannot be safely separated — document exactly what is entangled.

## 5. Per-Design Parameter Snapshot

- [x] 5.1 Add parameters snapshot to each DesignEntry and render it inside design cards
  This task has TWO parts that must both be completed. Both are required because the first design entry is created BEFORE the user provides any parameters, so a simple creation-time snapshot is insufficient.

  **Part A — Always snapshot parameters on entry creation**: Modify the `add_design_entry` frontend tool handler in `src/app/page.tsx` to ALWAYS include `parameters: { ...(state.parameters ?? {}) }` on every new `DesignEntry`, even when all parameter values are null/empty. Remove the `hasParams` conditional — the snapshot must always be present. This ensures every entry carries a parameters object from the start.

  **Part B — Backfill existing entries when parameters update**: Modify the `update_design_parameters` frontend tool handler in `src/app/page.tsx` so that AFTER merging new parameter values into `state.parameters`, it also iterates through ALL existing `state.designs` entries. For any entry whose `parameters` field is missing, null, or has zero filled values (all fields null/empty), replace its `parameters` with a copy of the current `state.parameters`. Entries that already have their own filled parameter snapshot MUST NOT be overwritten — each design entry preserves the parameters that were active when it was created OR backfilled before any parameters existed.

  **Part C — Render parameters inside each design card**: In `src/components/design-component.tsx`, inside each design card (below the image and prompt text), render the entry's `parameters` field as a compact label-value list showing only fields that have non-null, non-empty values. Use the `PARAM_LABELS` mapping and `ALL_PARAM_KEYS` array that already exist in the file. Cards whose parameters have no filled values should show nothing extra.

  Done when: (1) Every new DesignEntry has a `parameters` object at creation time regardless of whether parameters are filled. (2) When `update_design_parameters` is called, it backfills entries that have no parameters snapshot yet. (3) Each design card renders its captured parameters below the image/prompt. (4) A design created before any parameters are set will show parameters once they are filled (via backfill).
  Verify by: Open the browser. Type a message to create design #1 (no parameters set yet). Then provide parameters (e.g. "10x15m gable roof"). Design #1 MUST now show the parameters in its card. Create design #2 — it MUST also show parameters. Run `npx tsc --noEmit && npm run lint` both exit zero.
  Stop and hand off if: The backfill logic causes React re-render loops — add a shallow-equality check before calling setState to prevent unnecessary updates.

## 6. Verification

- [ ] 6.1 Run all lint and type checks across backend and frontend
  Run `cd agent && python -m ruff check . && python -m mypy .` then `npx tsc --noEmit && npm run lint`. All commands MUST exit zero.
  Done when: All four commands exit zero with no errors.
  Verify by: Run each command and confirm zero exit code.
  Stop and hand off if: Persistent type errors from CopilotKit type mismatches — document the errors and add `# type: ignore` comments with explanations.
