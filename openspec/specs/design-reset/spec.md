## Purpose

Provides the `reset_design` frontend tool that allows the AI agent to partially or fully reset design entries — clearing specific parameter fields to placeholder values, resetting prices, or scrapping entries entirely — and clearing session-level parameters. Also provides session-level parameter persistence in `AgentState` and `useCopilotReadable` parameter exposure.

## Requirements

### Requirement: Session-level parameters in AgentState

`AgentState` in `src/lib/types.ts` SHALL include a `parameters` field of type `DesignParameters` (or `Partial<DesignParameters>`). This field stores the current session-level parameter values collected during conversation, independent of per-design-entry parameters.

#### Scenario: Initial state has no parameters

- **GIVEN** a fresh session with no parameters collected
- **WHEN** the application initializes
- **THEN** `AgentState.parameters` SHALL be an empty object or undefined

#### Scenario: Parameters persist across agent turns

- **GIVEN** the agent has called `update_design_parameters` with `roofType: "Gable"` and `location: "Bratislava"`
- **WHEN** the next agent turn reads `AgentState`
- **THEN** `AgentState.parameters` SHALL contain `roofType: "Gable"` and `location: "Bratislava"`

### Requirement: update_design_parameters persists to state

The `update_design_parameters` frontend tool handler in `src/app/page.tsx` SHALL merge provided parameter fields into `AgentState.parameters` and call `setState`. The handler SHALL continue to return a summary string (unchanged return contract).

#### Scenario: Partial update merges into existing parameters

- **GIVEN** `AgentState.parameters` contains `{ buildingType: "House", location: "Bratislava" }`
- **WHEN** the agent calls `update_design_parameters` with `roofType: "Gable"`
- **THEN** `AgentState.parameters` SHALL contain `{ buildingType: "House", location: "Bratislava", roofType: "Gable" }`
- **AND** the handler SHALL return a summary string including "roofType" in the updated fields

#### Scenario: Update with no existing parameters

- **GIVEN** `AgentState.parameters` is undefined or empty
- **WHEN** the agent calls `update_design_parameters` with `floorPlanDimensions: "10x15m"`
- **THEN** `AgentState.parameters` SHALL contain `{ floorPlanDimensions: "10x15m" }`

### Requirement: useCopilotReadable includes parameters

The `useCopilotReadable` hook in `src/app/page.tsx` SHALL expose both `designs` and `parameters` from `AgentState` so the agent can observe current session-level parameter values.

#### Scenario: Agent can read collected parameters

- **GIVEN** `AgentState` contains `parameters: { buildingType: "House", roofType: "Gable" }`
- **WHEN** the `useCopilotReadable` hook provides state to the agent
- **THEN** the readable value SHALL include both `designs` and `parameters`
- **AND** the `parameters` value SHALL contain `{ buildingType: "House", roofType: "Gable" }`

### Requirement: Design In Progress placeholder image when parameters incomplete

The `DesignComponent` in `src/components/design-component.tsx` SHALL render a "Design In Progress" placeholder image for any design entry where one or more parameter fields are missing (undefined/null) or set to `"---"`. The actual design image (`entry.imageUrl`) SHALL only be rendered when ALL parameter fields are filled with real (non-`"---"`, non-empty) values.

A static SVG file at `public/design-in-progress.svg` SHALL exist as the placeholder image.

The rendering order for each design entry card's image area SHALL be:
1. If `status === "processing"` → show the generating spinner (existing behavior, unchanged).
2. Else if any parameter field is undefined, null, empty, or `"---"` → show the "Design In Progress" placeholder image (`/design-in-progress.svg`).
3. Else → show `entry.imageUrl` (the actual rendered design).

#### Scenario: Design entry with incomplete parameters shows placeholder

- **GIVEN** a design entry with `parameters: { buildingType: "House", roofType: "---", location: "Bratislava" }` and `imageUrl: "/design-hip.svg"`
- **WHEN** the `DesignComponent` renders the image area
- **THEN** the component SHALL render the "Design In Progress" placeholder image (`/design-in-progress.svg`)
- **AND** SHALL NOT render `entry.imageUrl`

#### Scenario: Design entry with all parameters filled shows actual image

- **GIVEN** a design entry with `parameters: { buildingType: "House", roofType: "Gable", location: "Bratislava" }` and `imageUrl: "/design-hip.svg"`
- **WHEN** the `DesignComponent` renders the image area
- **THEN** the component SHALL render `entry.imageUrl` (`/design-hip.svg`)

#### Scenario: Design entry with no parameters shows placeholder

- **GIVEN** a design entry with `parameters: undefined` or `parameters: {}` and `imageUrl: "/design-gable.svg"`
- **WHEN** the `DesignComponent` renders the image area
- **THEN** the component SHALL render the "Design In Progress" placeholder image

#### Scenario: Cleared field triggers placeholder automatically

- **GIVEN** a design entry with `parameters: { buildingType: "House", roofType: "Gable" }` showing `entry.imageUrl`
- **WHEN** the agent calls `reset_design` with `clear_parameters: ["roofType"]` and the field is set to `"---"`
- **THEN** the `DesignComponent` SHALL re-render showing the "Design In Progress" placeholder image (because `roofType` is now `"---"`)

### Requirement: reset_design frontend tool

The system SHALL provide a `reset_design` frontend tool registered via `useFrontendTool` in `src/app/page.tsx` that partially or fully resets design entries and clears session-level parameters.

The tool SHALL accept these parameters:

- `design_ids` (optional, array of numbers): The IDs of design entries to reset. If omitted, ALL design entries SHALL be reset.
- `remove_designs` (optional, boolean, default `false`): If `true`, the targeted design entries SHALL be removed entirely from the list (full scrap). If `false` (default), the entries SHALL remain in the list with specified parameters cleared.
- `clear_parameters` (optional, array of strings): Parameter field names to set to the placeholder value `"---"` on the targeted design entries. Valid values are: `buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`, `atticUsage`, `eavesShape`, `wallConstruction`, `location`, `overhang`. If omitted and `remove_designs` is `false`, no parameters SHALL be cleared.
- `clear_all_parameters` (optional, boolean, default `false`): If `true`, ALL parameter fields on the targeted entries SHALL be set to `"---"`. Takes precedence over `clear_parameters`.
- `clear_session_parameters` (optional, array of strings): Parameter field names to clear from `AgentState.parameters` (session-level). Same valid values as `clear_parameters`. Operates independently of design entry operations.

The tool SHALL NOT modify `entry.imageUrl`. Image display is handled by the UI rendering logic based on parameter completeness (see "Design In Progress placeholder image" requirement).

When `remove_designs` is `false` (partial reset), the handler SHALL:
1. Keep the targeted design entries in the list.
2. Set specified parameter fields (via `clear_parameters` or `clear_all_parameters`) to `"---"`.
3. Set the `price` field on each targeted entry to `"---"`. Since cleared parameters invalidate the design, the price is also invalid and must be recalculated.
4. Preserve all other parameter fields and `promptText`.
5. The UI will automatically show the "Design In Progress" placeholder for entries with `"---"` fields.

When `remove_designs` is `true` (full scrap), the handler SHALL:
1. Remove the targeted design entries entirely from `AgentState.designs`.
2. Ignore `clear_parameters` and `clear_all_parameters` (entries are removed).

#### Scenario: Partial reset — clear specific fields on a design entry

- **GIVEN** `AgentState` contains design entry `#1` with `parameters: { buildingType: "House", floorPlanDimensions: "10x15m", roofType: "Gable", location: "Bratislava" }` and `price: "€1,752"`
- **WHEN** the agent calls `reset_design` with `design_ids: [1]` and `clear_parameters: ["floorPlanDimensions", "roofType"]`
- **THEN** design entry `#1` SHALL remain in the list
- **AND** its `parameters.floorPlanDimensions` SHALL be `"---"`
- **AND** its `parameters.roofType` SHALL be `"---"`
- **AND** its `parameters.buildingType` SHALL remain `"House"`
- **AND** its `parameters.location` SHALL remain `"Bratislava"`
- **AND** its `price` SHALL be `"---"`
- **AND** its `imageUrl` SHALL be unchanged (the UI will show the placeholder image because fields are `"---"`)
- **AND** the handler SHALL return a summary listing cleared fields and preserved fields

#### Scenario: No-op reset — no parameters cleared

- **GIVEN** `AgentState` contains design entry `#1` with `parameters: { buildingType: "House" }`
- **WHEN** the agent calls `reset_design` with `design_ids: [1]` and no `clear_parameters`
- **THEN** design entry `#1` SHALL remain unchanged (all fields and imageUrl preserved)

#### Scenario: Full scrap — remove design entry entirely

- **GIVEN** `AgentState.designs` contains entries with IDs `[1, 2, 3]`
- **WHEN** the agent calls `reset_design` with `design_ids: [1, 3]` and `remove_designs: true`
- **THEN** `AgentState.designs` SHALL contain only the entry with `id: 2`
- **AND** the handler SHALL return "Removed 2 design entry/entries entirely."

#### Scenario: Full scrap ignores clear_parameters

- **GIVEN** `AgentState` contains design entry `#1`
- **WHEN** the agent calls `reset_design` with `design_ids: [1]`, `remove_designs: true`, and `clear_parameters: ["roofType"]`
- **THEN** design entry `#1` SHALL be removed from the list entirely
- **AND** the handler SHALL return a removal summary (not a field-clearing summary)

#### Scenario: Clear all parameters on entries with clear_all_parameters

- **GIVEN** `AgentState` contains design entry `#1` with `parameters: { buildingType: "House", roofType: "Gable", location: "Bratislava" }` and `price: "€1,752"`
- **WHEN** the agent calls `reset_design` with `design_ids: [1]` and `clear_all_parameters: true`
- **THEN** design entry `#1` SHALL remain in the list
- **AND** ALL its parameter fields SHALL be set to `"---"`
- **AND** its `price` SHALL be `"---"`

#### Scenario: clear_all_parameters takes precedence over clear_parameters

- **GIVEN** `AgentState` contains design entry `#1` with `parameters: { buildingType: "House", roofType: "Gable" }`
- **WHEN** the agent calls `reset_design` with `design_ids: [1]`, `clear_all_parameters: true`, and `clear_parameters: ["roofType"]`
- **THEN** ALL parameter fields SHALL be set to `"---"` (not just `roofType`)

#### Scenario: Clear session-level parameters independently

- **GIVEN** `AgentState.parameters` contains `{ buildingType: "House", floorPlanDimensions: "10x15m" }`
- **WHEN** the agent calls `reset_design` with `clear_session_parameters: ["floorPlanDimensions"]`
- **THEN** `AgentState.parameters` SHALL contain `{ buildingType: "House" }`
- **AND** `AgentState.designs` SHALL remain unchanged

#### Scenario: Compound reset — partial entry reset plus session clear

- **GIVEN** `AgentState` contains design entry `#1` with `parameters: { buildingType: "House", roofPitch: 35 }` and `price: "€2,100"` and `AgentState.parameters` contains `{ buildingType: "House", roofPitch: 35 }`
- **WHEN** the agent calls `reset_design` with `design_ids: [1]`, `clear_parameters: ["roofPitch"]`, and `clear_session_parameters: ["roofPitch"]`
- **THEN** design entry `#1` SHALL remain with `parameters.roofPitch` set to `"---"` and `parameters.buildingType` preserved as `"House"`
- **AND** entry `#1` `price` SHALL be `"---"`
- **AND** `AgentState.parameters.roofPitch` SHALL be removed
- **AND** `AgentState.parameters.buildingType` SHALL remain `"House"`

#### Scenario: Reset all designs (design_ids omitted) — partial reset

- **GIVEN** `AgentState` contains design entries `#1` and `#2`
- **WHEN** the agent calls `reset_design` with `design_ids` omitted and `clear_parameters: ["roofType"]`
- **THEN** both design entries SHALL remain in the list
- **AND** both entries SHALL have `parameters.roofType` set to `"---"`

#### Scenario: Remove all designs (full scrap)

- **GIVEN** `AgentState` contains 3 design entries and `parameters: { buildingType: "House" }`
- **WHEN** the agent calls `reset_design` with `design_ids` omitted and `remove_designs: true`
- **THEN** `AgentState.designs` SHALL be an empty array
- **AND** `AgentState.parameters` SHALL remain `{ buildingType: "House" }` (session params not affected by remove_designs)

#### Scenario: Invalid design ID in design_ids

- **GIVEN** `AgentState.designs` contains entries with IDs `[1, 2]`
- **WHEN** the agent calls `reset_design` with `design_ids: [1, 99]`
- **THEN** the handler SHALL return an error string listing the invalid ID and the valid IDs
- **AND** `AgentState` SHALL remain unchanged (no partial reset)

#### Scenario: Invalid parameter key in clear_parameters

- **GIVEN** `AgentState` contains design entry `#1`
- **WHEN** the agent calls `reset_design` with `clear_parameters: ["invalidField"]`
- **THEN** the handler SHALL return an error string listing the invalid key and the valid keys
- **AND** `AgentState` SHALL remain unchanged

#### Scenario: Invalid parameter key in clear_session_parameters

- **GIVEN** `AgentState.parameters` contains `{ buildingType: "House" }`
- **WHEN** the agent calls `reset_design` with `clear_session_parameters: ["invalidField"]`
- **THEN** the handler SHALL return an error string listing the invalid key and the valid keys
- **AND** `AgentState` SHALL remain unchanged

### Requirement: Cleared parameter fields display as placeholder

Parameter fields set to the placeholder value `"---"` SHALL be displayed in the design card UI. The `DesignComponent` in `src/components/design-component.tsx` currently filters parameters to show only non-null, non-empty values. Since `"---"` is a non-empty string, fields with this value SHALL pass the filter and render visibly in the parameter grid.

#### Scenario: Cleared field shows placeholder in UI

- **GIVEN** a design entry with `parameters: { buildingType: "House", roofType: "---" }`
- **WHEN** the `DesignComponent` renders the parameter grid
- **THEN** `roofType` SHALL appear in the grid with the displayed value `"---"`

### Requirement: reset_design return value format

The `reset_design` handler SHALL return a human-readable summary string describing what was done. The summary format depends on the operation:

- **Partial reset**: "Reset N design entry/entries (IDs: ...). Cleared parameters: .... Preserved parameters: key=value, ...."
- **Full scrap**: "Removed N design entry/entries (IDs: ...) entirely."
- **Session-only clear**: "Cleared session parameters: .... Remaining session parameters: key=value, ...."
- **Compound**: Combined partial reset + session clear summary.

For error cases, the handler SHALL return an error string listing valid values and make no state changes.

#### Scenario: Successful partial reset return value

- **GIVEN** `AgentState` contains design entry `#1` with `parameters: { buildingType: "House", floorPlanDimensions: "10x15m", location: "Bratislava" }`
- **WHEN** the agent calls `reset_design` with `design_ids: [1]` and `clear_parameters: ["floorPlanDimensions"]`
- **THEN** the return string SHALL contain "Reset 1 design entry" and "ID: 1" and "Cleared parameters: floorPlanDimensions" and "Preserved parameters" including `buildingType` and `location`

#### Scenario: Successful full scrap return value

- **GIVEN** `AgentState` contains design entries `#1` and `#3`
- **WHEN** the agent calls `reset_design` with `design_ids: [1, 3]` and `remove_designs: true`
- **THEN** the return string SHALL contain "Removed 2 design entry/entries" and "IDs: 1, 3" and "entirely"

### Requirement: reset_design documented in agent system prompt

The agent's system prompt in `agent/src/agent.py` SHALL include a `- reset_design:` section documenting the tool's parameters and usage rules. The documentation SHALL include:
- Parameter descriptions for `design_ids`, `remove_designs`, `clear_parameters`, `clear_all_parameters`, and `clear_session_parameters`
- The list of valid parameter field names
- Usage rules:
  - Default behavior (`remove_designs: false`) keeps the design entry in the list and clears specified fields to `"---"`. The UI automatically shows a "Design In Progress" placeholder image when fields are incomplete.
  - Use `remove_designs: true` only when the user explicitly wants to scrap the entire design
  - Use `clear_session_parameters` to reset in-flight collected parameters independently
  - When the user says "change X and Y but keep Z", call with `clear_parameters: ["X", "Y"]` only
  - Always confirm with the user what was cleared and what was preserved

#### Scenario: Agent system prompt contains reset_design documentation

- **GIVEN** the agent system prompt in `agent/src/agent.py`
- **WHEN** the system prompt is read
- **THEN** it SHALL contain the string `reset_design`
- **AND** it SHALL contain the string `clear_parameters`
- **AND** it SHALL contain the string `clear_all_parameters`
- **AND** it SHALL contain the string `design_ids`
- **AND** it SHALL contain the string `remove_designs`
- **AND** it SHALL contain the string `clear_session_parameters`
- **AND** it SHALL contain usage rules distinguishing partial reset from full scrap
