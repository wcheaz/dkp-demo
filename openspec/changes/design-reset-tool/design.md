## Context

The current system has three frontend tools for design management:
- `generate_design` — creates a new `DesignEntry` with parameters attached per-entry
- `modify_design_entry` — edits image/text/price on an existing entry
- `update_design_parameters` — accepts parameter values but does NOT persist them to `AgentState`; it only returns a summary string

Parameters exist in two places:
1. **Per-design-entry**: `DesignEntry.parameters` (persisted in state, rendered in UI)
2. **In-flight/session-level**: collected by the agent during conversation before a design is generated — currently NOT persisted anywhere in state

The `useCopilotReadable` in `src/app/page.tsx:504-507` exposes only `{ designs }` to the agent. There is no session-level parameter state for the agent to read or clear.

The UI already has per-design delete buttons (`design-component.tsx:69`) that filter the designs array, but these are user-only — the agent has no tool to trigger removal.

## Goals / Non-Goals

**Goals:**
- Provide a `reset_design` frontend tool that supports three patterns: full reset, design-only removal, selective parameter clearing.
- Enable the agent to clear specific parameter fields (e.g., floor plan dimensions) while preserving others (e.g., city, wall construction).
- Make session-level parameters durable in `AgentState` so that clearing is meaningful even before a design is generated.

**Non-Goals:**
- Undo/redo or history tracking — resets are immediate and irreversible.
- UI confirmation dialogs before reset — the agent decides based on user intent.
- Resetting state beyond `designs` and session-level `DesignParameters`.
- Changing how `generate_design` works — it continues to accept parameters as arguments and attach them to the new entry.

## Decisions

### D1: Add `parameters` field to `AgentState`

**Decision**: Add `parameters?: DesignParameters` to `AgentState` in `src/lib/types.ts`.

**Rationale**: Without session-level parameter state, selective clearing is impossible before a design is generated. The agent currently collects parameters via `update_design_parameters` which only returns a summary. If a user says "change the roof pitch but keep the city," the agent has no state to selectively clear.

**Alternative considered**: Only allow clearing parameters on existing `DesignEntry` objects. Rejected because the primary demo scenario (Step 4b) involves resetting before generating a new design, when no entries exist yet.

### D2: Update `update_design_parameters` to persist to state

**Decision**: Modify the `update_design_parameters` handler in `src/app/page.tsx` to merge provided fields into `AgentState.parameters` and call `setState`.

**Rationale**: This is a prerequisite for D1 to work. If parameters are in state but `update_design_parameters` doesn't write there, the state is always empty and clearing has no effect. This also fixes a pre-existing bug: the agent "collects" parameters that vanish between turns.

### D3: Update `useCopilotReadable` to include parameters

**Decision**: Change the `useCopilotReadable` value from `{ designs }` to `{ designs, parameters }` so the agent can see which parameters are currently set.

**Rationale**: The agent needs to know what's already collected to decide what to clear. Without this, it would have to rely on conversation history alone.

### D4: `reset_design` tool parameter shape

**Decision**: The tool accepts these parameters:

```
reset_design(
  design_ids?: number[],           // IDs to remove; omit = remove all
  clear_parameters?: string[],     // parameter keys to clear; omit = clear none
  clear_all_parameters?: boolean   // default false; if true, clear every field
)
```

Valid `clear_parameters` values are the keys of `DesignParameters`: `buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`, `atticUsage`, `eavesShape`, `wallConstruction`, `location`, `overhang`.

**Behavior matrix**:

| User intent | `design_ids` | `clear_parameters` | `clear_all_parameters` |
|---|---|---|---|
| Full restart | omit | omit | `true` |
| Remove specific designs | `[1, 3]` | omit | `false`/omit |
| Remove all designs, keep params | omit | omit | `false`/omit |
| Clear specific param fields | omit | `["floorPlanDimensions", "roofPitch"]` | `false`/omit |
| Remove designs + clear select params | `[2]` | `["roofPitch"]` | `false`/omit |

**Rationale**: Three composable parameters cover all five patterns. Using string array for `clear_parameters` lets the agent pick arbitrary field combinations. Invalid field names return an error listing valid keys.

**Alternative considered**: Separate tools for each pattern (e.g., `remove_designs`, `clear_parameters`, `full_reset`). Rejected because the agent would need to call multiple tools for compound operations, increasing latency and error surface.

### D5: Return value of `reset_design`

**Decision**: The handler returns a human-readable summary string:

```
"Removed 2 design(s) (IDs: 1, 3). Cleared parameters: floorPlanDimensions, roofPitch. Remaining designs: 1. Remaining parameters: buildingType=House, city=Bratislava."
```

For errors (e.g., invalid design ID or invalid parameter key), return an error string listing valid values.

**Rationale**: The agent relays this to the user. A structured summary prevents the agent from hallucinating what was cleared.

### D6: Agent system prompt update

**Decision**: Add a `- reset_design:` section to the system prompt in `agent/src/agent.py` after the existing tool documentation, with usage guidance:

- Use `reset_design` when the user expresses intent to start over, remove designs, or change specific parameters.
- When the user says "change X and Y but keep Z", call with `clear_parameters: ["X", "Y"]` only.
- When the user says "start over" or "clear everything", call with no arguments (defaults to full reset).
- Always confirm with the user what was cleared and what was preserved.

**Rationale**: The agent needs explicit instructions to avoid over-clearing or under-clearing. Without guidance, the LLM may call `clear_all_parameters` when selective clearing was requested.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| `update_design_parameters` refactor could break existing behavior | The handler currently returns a summary string. After the change, it still returns a summary string AND writes to state. The return value contract is unchanged. Existing agent behavior is preserved since the agent only reads the return value. |
| Agent may over-clear parameters due to misinterpreting user intent | System prompt includes explicit rules: use `clear_parameters` for selective changes, `clear_all_parameters` only when the user says "everything" or "start over". |
| Session-level `parameters` could diverge from per-entry `DesignEntry.parameters` | These serve different purposes. Session-level is the "working set" during collection. Per-entry is the snapshot at generation time. No sync needed — `generate_design` reads from its arguments, not from state. |
| Invalid `clear_parameters` keys passed by the agent | Handler validates against `ALL_PARAM_KEYS` and returns an error listing valid keys if any invalid key is provided. No state mutation on error. |
