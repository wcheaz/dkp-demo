## Why

The agent currently has no way to selectively reset design parameters or scrap designs. The only mutation tools are `generate_design` (add), `modify_design_entry` (edit), and `update_design_parameters` (set fields). When a user says "I want to change the roof pitch and the floor plan," the agent cannot respond meaningfully — it would need to clear specific fields while keeping others, reset the design image (since any detail change invalidates the current design), and preserve the design entry in the list. The presenter also has no clean way to restart the demo flow. This change adds a `reset_design` frontend tool that supports selective field clearing with placeholder values, image reset, and optional full design removal.

## What Changes

- Add a new `reset_design` frontend tool registered via `useFrontendTool` in `src/app/page.tsx`.
- The tool operates on existing design entries by ID and supports two modes:
  - **Partial reset** (default): The design entry stays in the list. Its image is reset to a placeholder. Specified parameter fields are set to the placeholder value `"---"`. Other fields are preserved.
  - **Full scrap**: The design entry is removed entirely from the list. Used only when the user explicitly wants to discard the whole design.
- The tool accepts:
  - `design_ids` (optional): list of design entry IDs to reset. If omitted, all designs are reset.
  - `remove_designs` (optional boolean, default false): if true, removes the design entries entirely (full scrap).
  - `clear_parameters` (optional): list of parameter field names to clear (set to `"---"`). If omitted and `remove_designs` is false, no parameters are cleared (image still resets).
  - `clear_all_parameters` (optional boolean, default false): if true, sets all parameter fields to `"---"`. Takes precedence over `clear_parameters`.
  - `clear_session_parameters` (optional): list of session-level parameter field names to clear from `AgentState.parameters`. Used to reset the in-flight parameter collection state independently of design entries.
- This enables four distinct reset patterns:
  1. **Full scrap**: remove design entries entirely (user says "scrap this design" or "start over completely").
  2. **Partial reset**: keep the design entry, reset its image, clear specific parameter fields to `"---"` (user says "change the roof pitch" but keeps other fields).
  3. **Image-only reset**: keep the design entry, reset only the image, leave all parameters intact.
  4. **Session parameter clear**: clear in-flight collected parameters from `AgentState.parameters` without affecting any design entries.
- Cleared parameter fields take the placeholder value `"---"` so they remain visible in the UI as "to be re-collected" rather than disappearing entirely.
- The `DesignComponent` rendering logic is updated so that a "Design In Progress" placeholder image is shown when any parameter field is missing or set to `"---"`. The actual design image (`entry.imageUrl`) is only displayed when all parameter fields are filled with real values. This applies to all design entries — not just reset ones — ensuring that partially-complete designs never show a stale or misleading rendered image.
- Update the agent system prompt in `agent/src/agent.py` to document the new tool and instruct the agent when to use each reset pattern.

## Capabilities

### New Capabilities

- `design-reset`: Frontend tool that partially or fully resets design entries — clearing specific parameter fields to placeholder values or scrapping entries entirely — and clears session-level parameters. The UI gates image display on parameter completeness, automatically showing a "Design In Progress" placeholder when fields are incomplete.

### Modified Capabilities

- `design-entry-modify`: The system prompt documentation section must be extended to include `reset_design` alongside the existing `modify_design_entry` tool documentation.
- `design-display`: The `DesignComponent` rendering logic must be updated to gate image display on parameter completeness — showing a "Design In Progress" placeholder when any parameter is missing or `"---"`, and only showing `entry.imageUrl` when all parameters are filled.

## Non-goals

- Undo/redo or history tracking for resets — a reset is immediate and irreversible.
- Confirmation prompts in the UI before reset — the agent decides when to call the tool based on user intent.
- Resetting any state beyond `designs` entries and `DesignParameters` fields on the current session.
- Persisting reset events to a server or log.
- Changing how `generate_design` works — it continues to accept parameters as arguments and attach them to the new entry.

## Impact

- **`src/app/page.tsx`**: New `useFrontendTool` registration for `reset_design`. The `DesignParameters` fields must be stored in `AgentState` (currently they are only passed per-call and not persisted in state). This requires adding a `parameters` field to `AgentState` so that session-level parameter clearing is meaningful.
- **`src/lib/types.ts`**: `AgentState` needs a `parameters?: DesignParameters` field so that cleared session-level fields persist across tool calls. Currently `update_design_parameters` does not write to state — it only returns a summary string. This change also makes parameter state durable.
- **`agent/src/agent.py`**: System prompt updated with `reset_design` documentation and usage guidance distinguishing partial reset from full scrap.
- **`src/components/design-component.tsx`**: The UI must display parameter fields with value `"---"` as visible placeholder entries. The image rendering logic must gate on parameter completeness: show a "Design In Progress" placeholder image when any parameter field is missing or set to `"---"`, show `entry.imageUrl` only when all fields are filled with real values.
- **`public/`**: A new `design-in-progress.svg` placeholder image is needed (displays "Design In Progress" text or similar indicator).
