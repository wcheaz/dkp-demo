## Why

The agent currently has no way to remove designs or selectively clear collected parameters. The only mutation tools are `generate_design` (add), `modify_design_entry` (edit), and `update_design_parameters` (set fields). When a user says "I want to change the roof pitch and the floor plan — let's start over," the agent cannot respond meaningfully. The presenter also has no clean way to restart the demo flow. This change adds a `reset_design` frontend tool that supports bulk design removal and selective parameter field clearing, so the agent can handle iterative design requests and full do-overs without losing fields the user wants to keep.

## What Changes

- Add a new `reset_design` frontend tool registered via `useFrontendTool` in `src/app/page.tsx`.
- The tool accepts:
  - `design_ids` (optional): list of design entry IDs to remove. If omitted, all designs are removed.
  - `clear_parameters` (optional): list of parameter field names to clear (e.g., `floorPlanDimensions`, `roofPitch`). If omitted, no parameters are cleared.
  - `clear_all_parameters` (optional boolean): if true, clears every parameter field. Defaults to false.
- This enables three distinct reset patterns:
  1. **Full reset**: remove all designs + clear all parameters (demo restart).
  2. **Design-only reset**: remove one or more specific designs, leave parameters intact.
  3. **Selective parameter clear**: clear specific fields (e.g., floor plan area) while preserving others (e.g., city, lumber type).
- Update the agent system prompt in `agent/src/agent.py` to document the new tool and instruct the agent when to use each reset pattern.

## Capabilities

### New Capabilities

- `design-reset`: Frontend tool that removes design entries (individually or all) and selectively clears parameter fields without a full state wipe.

### Modified Capabilities

- `design-entry-modify`: The system prompt documentation section must be extended to include `reset_design` alongside the existing `modify_design_entry` tool documentation.

## Non-goals

- Undo/redo or history tracking for resets — a reset is immediate and irreversible.
- Confirmation prompts in the UI before reset — the agent decides when to call the tool based on user intent.
- Resetting any state beyond the `designs` array and `DesignParameters` fields on the current session.
- Persisting reset events to a server or log.

## Impact

- **`src/app/page.tsx`**: New `useFrontendTool` registration for `reset_design`. The `DesignParameters` fields must be stored in `AgentState` (currently they are only passed per-call and not persisted in state). This may require adding a `parameters` field to `AgentState` so that selective clearing is meaningful.
- **`src/lib/types.ts`**: `AgentState` needs a `parameters?: DesignParameters` field (or similar) so that cleared fields persist across tool calls. Currently `update_design_parameters` does not write to state — it only returns a summary string. This change may need to make parameter state durable.
- **`agent/src/agent.py`**: System prompt updated with `reset_design` documentation and usage guidance.
- **`src/components/`**: If parameter state becomes durable, the UI components that display parameters may need to read from the new state location.
