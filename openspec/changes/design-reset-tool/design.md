## Context

The current system has three frontend tools for design management:
- `generate_design` — creates a new `DesignEntry` with parameters attached per-entry
- `modify_design_entry` — edits image/text/price on an existing entry
- `update_design_parameters` — accepts parameter values but does NOT persist them to `AgentState`; it only returns a summary string

Parameters exist in two places:
1. **Per-design-entry**: `DesignEntry.parameters` (persisted in state, rendered in UI)
2. **In-flight/session-level**: collected by the agent during conversation before a design is generated — currently NOT persisted anywhere in state

The `useCopilotReadable` in `src/app/page.tsx:504-507` exposes only `{ designs }` to the agent. There is no session-level parameter state for the agent to read or clear.

The UI already has per-design delete buttons (`design-component.tsx:69`) that filter the designs array, but these are user-only — the agent has no tool to trigger removal or partial reset.

The UI currently filters out null/empty parameter fields (`design-component.tsx:95-98`), so only filled values are shown. Cleared fields with a placeholder value like `"---"` will render visibly, which is the desired behavior.

## Goals / Non-Goals

**Goals:**
- Provide a `reset_design` frontend tool that supports partial resets (clear specific fields, keep the design entry) and full scraps (remove the entry entirely).
- Always reset the design image when any reset occurs, since any detail change invalidates the current rendered design.
- Cleared parameter fields take a `"---"` placeholder value so they remain visible in the UI as "to be re-collected."
- Enable session-level parameter clearing independently of design entries.

**Non-Goals:**
- Undo/redo or history tracking — resets are immediate and irreversible.
- UI confirmation dialogs before reset — the agent decides based on user intent.
- Resetting state beyond `designs` entries and session-level `DesignParameters`.
- Changing how `generate_design` works — it continues to accept parameters as arguments and attach them to the new entry.

## Decisions

### D1: Add `parameters` field to `AgentState`

**Decision**: Add `parameters?: DesignParameters` to `AgentState` in `src/lib/types.ts`.

**Rationale**: Without session-level parameter state, clearing in-flight parameters is impossible before a design is generated. The agent currently collects parameters via `update_design_parameters` which only returns a summary. If a user says "change the roof pitch but keep the city," the agent has no session-level state to selectively clear.

**Alternative considered**: Only allow clearing parameters on existing `DesignEntry` objects. Rejected because the primary demo scenario involves resetting before generating a new design, when no entries may exist yet.

### D2: Update `update_design_parameters` to persist to state

**Decision**: Modify the `update_design_parameters` handler in `src/app/page.tsx` to merge provided fields into `AgentState.parameters` and call `setState`.

**Rationale**: Prerequisite for D1. If parameters are in state but `update_design_parameters` doesn't write there, the state is always empty and clearing has no effect. This also fixes a pre-existing issue: the agent "collects" parameters that vanish between turns.

### D3: Update `useCopilotReadable` to include parameters

**Decision**: Change the `useCopilotReadable` value from `{ designs }` to `{ designs, parameters }` so the agent can see which parameters are currently set.

**Rationale**: The agent needs to know what's already collected to decide what to clear.

### D4: `reset_design` tool parameter shape — partial reset vs. full scrap

**Decision**: The tool accepts these parameters:

```
reset_design(
  design_ids?: number[],              // IDs to reset; omit = all designs
  remove_designs?: boolean,           // default false; true = remove entries entirely (full scrap)
  clear_parameters?: string[],        // param keys to set to "---" on the design entries
  clear_all_parameters?: boolean,     // default false; true = set ALL entry params to "---"
  clear_session_parameters?: string[] // param keys to clear from AgentState.parameters
)
```

Valid `clear_parameters` and `clear_session_parameters` values are the keys of `DesignParameters`: `buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`, `atticUsage`, `eavesShape`, `wallConstruction`, `location`, `overhang`.

**Behavior when `remove_designs` is false (default — partial reset)**:
- Design entries remain in the list.
- Specified parameter fields on the entries are set to `"---"`.
- Other parameter fields and the `promptText` are preserved.
- The tool does NOT modify `imageUrl`. The UI rendering logic handles image display — it shows the "Design In Progress" placeholder automatically when any field is `"---"` (see D5).

**Behavior when `remove_designs` is true (full scrap)**:
- Design entries are removed entirely from the list.
- `clear_parameters` and `clear_all_parameters` are ignored (the entries are gone).

**Behavior matrix**:

| User intent | `design_ids` | `remove_designs` | `clear_parameters` | `clear_all_parameters` | `clear_session_parameters` | UI image result |
|---|---|---|---|---|---|---|
| "Change the roof pitch" | `[1]` | `false` | `["roofPitch"]` | — | — | Placeholder (roofPitch = `"---"`) |
| "Scrap this design entirely" | `[1]` | `true` | — | — | — | Entry removed |
| "Start over completely" | omit | `true` | — | — | — | All entries removed |
| "Reset image, keep all params" | `[1]` | `false` | omit | — | — | No change (all params intact → actual image shown) |
| "Clear floor plan from session" | omit | `false` | — | — | `["floorPlanDimensions"]` | No change to entries |
| Compound: reset entry + session | `[1]` | `false` | `["roofPitch"]` | — | `["roofPitch"]` | Placeholder (roofPitch = `"---"`) |

**Rationale**: The default behavior (partial reset) preserves the design entry in the UI while signaling that specific fields need re-collection. The `"---"` placeholder keeps the field visible and triggers the "Design In Progress" placeholder image via the UI rendering logic (D5). Full scrap is opt-in because the user must explicitly request discarding the entire design. The tool does not touch `imageUrl` — image display is entirely UI-driven based on parameter completeness.

**Alternative considered**: Two separate tools — `reset_design_fields` and `scrap_design`. Rejected because the agent would need to call multiple tools for compound operations, and the parameter sets overlap (both need `design_ids`).

### D5: Placeholder image gated on parameter completeness

**Decision**: The `DesignComponent` in `src/components/design-component.tsx` gates image display on parameter completeness. When ANY parameter field on a `DesignEntry` is missing (undefined/null) or set to `"---"`, the component renders a "Design In Progress" placeholder image instead of `entry.imageUrl`. When ALL parameter fields are filled with real (non-`"---"`, non-empty) values, the component renders `entry.imageUrl`.

A new SVG file `public/design-in-progress.svg` serves as the placeholder. It displays "Design In Progress" text with muted styling consistent with the existing design card aesthetic.

This logic replaces the current rendering at `design-component.tsx:76-89`, which only checks `entry.status === "processing"`. The new rendering order is:
1. If `status === "processing"` → show spinner (unchanged)
2. Else if any parameter field is missing or `"---"` → show "Design In Progress" placeholder image
3. Else → show `entry.imageUrl` (the actual design)

**Rationale**: The image should always reflect the current state of the parameters. If a field is cleared to `"---"`, the previously-rendered design image is stale and misleading. The "Design In Progress" placeholder visually signals that the design needs updated parameters before it can be rendered. This is driven by the UI, not the tool — so any future tool that changes parameters automatically gets the correct image behavior.

**Alternative considered**: Have the `reset_design` tool explicitly set `imageUrl` to the placeholder. Rejected because it couples data operations to visual state, and would require every tool that modifies parameters to also update `imageUrl`. The UI-driven approach is a single source of truth.

### D6: Placeholder value for cleared fields

**Decision**: Cleared parameter fields are set to the string `"---"`.

**Rationale**: The UI's `design-component.tsx` filters parameters with `entry.parameters?.[k] != null && entry.parameters?.[k] !== ""`. Using `"---"` passes this filter, so the field remains visible in the card with the placeholder shown as the value. Additionally, `"---"` triggers the "Design In Progress" placeholder image (see D5), since it counts as an incomplete field.

**Alternative considered**: `null` or `undefined`. Rejected because the UI would hide these fields entirely, giving no visual signal that the field was intentionally cleared and needs re-collection.

### D7: Return value of `reset_design`

**Decision**: The handler returns a human-readable summary string:

```
"Reset 1 design entry (ID: 1). Cleared parameters: roofPitch. Preserved parameters: buildingType=House, location=Bratislava."
```

Or for full scrap:
```
"Removed 1 design entry (ID: 1) entirely."
```

Or for session-only clear:
```
"Cleared session parameters: floorPlanDimensions. Remaining session parameters: buildingType=House."
```

For errors (invalid design ID or invalid parameter key), return an error string listing valid values. No state mutation on error.

**Rationale**: The agent relays this to the user. A structured summary prevents the agent from hallucinating what was cleared.

### D8: Agent system prompt update

**Decision**: Add a `- reset_design:` section to the system prompt in `agent/src/agent.py` after the existing tool documentation, with usage guidance:

- Use `remove_designs: false` (default) with `clear_parameters` when the user wants to change specific fields but keep the design. The image will always reset.
- Use `remove_designs: true` only when the user explicitly says "scrap this design," "delete this design," or "start over completely."
- Use `clear_session_parameters` to clear in-flight collected parameters independently of design entries.
- When the user says "change X and Y but keep Z", call with `clear_parameters: ["X", "Y"]` only.
- Always confirm with the user what was cleared and what was preserved.
- After clearing fields, the UI will automatically show the "Design In Progress" placeholder image for entries with incomplete parameters.

**Rationale**: The agent needs explicit instructions to distinguish between partial reset (keep entry, clear fields) and full scrap (remove entry). Without guidance, the LLM may remove entries when the user only wanted to change specific fields.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| `update_design_parameters` refactor could break existing behavior | The handler currently returns a summary string. After the change, it still returns a summary string AND writes to state. The return value contract is unchanged. |
| Agent may confuse partial reset with full scrap | System prompt includes explicit rules: default is partial reset (keep entry), `remove_designs: true` only for explicit scrap requests. |
| `"---"` placeholder value could be confused with real data | The placeholder is visually distinct. The agent's system prompt instructs it to treat `"---"` fields as "needs re-collection." The UI shows "Design In Progress" image when any field is `"---"`. |
| Session-level `parameters` could diverge from per-entry `DesignEntry.parameters` | These serve different purposes. Session-level is the working set during collection. Per-entry is the snapshot at generation time. No sync needed. |
| Invalid `clear_parameters` keys passed by the agent | Handler validates against `ALL_PARAM_KEYS` and returns an error listing valid keys. No state mutation on error. |
| Design entries with no parameters at all always show placeholder | This is acceptable and correct behavior — a design with no parameters is incomplete and should not show a rendered image. The `generate_design` tool always attaches parameters, so entries created normally will have parameters. |
