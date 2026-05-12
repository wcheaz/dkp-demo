## ADDED Requirements

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

### Requirement: reset_design frontend tool

The system SHALL provide a `reset_design` frontend tool registered via `useFrontendTool` in `src/app/page.tsx` that removes design entries and selectively clears session-level parameter fields.

The tool SHALL accept these parameters:

- `design_ids` (optional, array of numbers): The IDs of design entries to remove. If omitted, ALL design entries SHALL be removed.
- `clear_parameters` (optional, array of strings): Parameter field names to clear from `AgentState.parameters`. Valid values are: `buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`, `atticUsage`, `eavesShape`, `wallConstruction`, `location`, `overhang`. If omitted, no parameters SHALL be cleared.
- `clear_all_parameters` (optional, boolean, default `false`): If `true`, ALL parameter fields SHALL be cleared. Takes precedence over `clear_parameters`.

#### Scenario: Full reset — remove all designs and clear all parameters

- **GIVEN** `AgentState` contains 3 design entries and `parameters: { buildingType: "House", roofType: "Gable", location: "Bratislava" }`
- **WHEN** the agent calls `reset_design` with no arguments (or `clear_all_parameters: true` and no `design_ids`)
- **THEN** `AgentState.designs` SHALL be an empty array
- **AND** `AgentState.parameters` SHALL be an empty object or all fields cleared
- **AND** the handler SHALL return a summary string confirming full reset

#### Scenario: Remove specific designs by ID

- **GIVEN** `AgentState.designs` contains entries with IDs `[1, 2, 3]`
- **WHEN** the agent calls `reset_design` with `design_ids: [1, 3]`
- **THEN** `AgentState.designs` SHALL contain only the entry with `id: 2`
- **AND** `AgentState.parameters` SHALL remain unchanged
- **AND** the handler SHALL return "Removed 2 design(s) (IDs: 1, 3)."

#### Scenario: Clear specific parameter fields

- **GIVEN** `AgentState.parameters` contains `{ buildingType: "House", floorPlanDimensions: "10x15m", roofType: "Gable", location: "Bratislava" }`
- **WHEN** the agent calls `reset_design` with `clear_parameters: ["floorPlanDimensions", "roofType"]`
- **THEN** `AgentState.parameters` SHALL contain `{ buildingType: "House", location: "Bratislava" }`
- **AND** `AgentState.designs` SHALL remain unchanged
- **AND** the handler SHALL return a summary listing cleared fields and remaining parameters

#### Scenario: Remove designs and clear specific parameters together

- **GIVEN** `AgentState` contains designs `[1, 2]` and `parameters: { buildingType: "House", roofType: "Gable", roofPitch: 35 }`
- **WHEN** the agent calls `reset_design` with `design_ids: [2]` and `clear_parameters: ["roofPitch"]`
- **THEN** `AgentState.designs` SHALL contain only the entry with `id: 1`
- **AND** `AgentState.parameters` SHALL contain `{ buildingType: "House", roofType: "Gable" }`

#### Scenario: Invalid design ID in design_ids

- **GIVEN** `AgentState.designs` contains entries with IDs `[1, 2]`
- **WHEN** the agent calls `reset_design` with `design_ids: [1, 99]`
- **THEN** the handler SHALL return an error string listing the invalid ID and the valid IDs
- **AND** `AgentState` SHALL remain unchanged (no partial removal)

#### Scenario: Invalid parameter key in clear_parameters

- **GIVEN** `AgentState.parameters` contains `{ buildingType: "House" }`
- **WHEN** the agent calls `reset_design` with `clear_parameters: ["invalidField"]`
- **THEN** the handler SHALL return an error string listing the invalid key and the valid keys
- **AND** `AgentState` SHALL remain unchanged

#### Scenario: clear_all_parameters takes precedence over clear_parameters

- **GIVEN** `AgentState.parameters` contains `{ buildingType: "House", roofType: "Gable" }`
- **WHEN** the agent calls `reset_design` with `clear_all_parameters: true` and `clear_parameters: ["roofType"]`
- **THEN** ALL parameter fields SHALL be cleared (not just `roofType`)

#### Scenario: Remove all designs without clearing parameters

- **GIVEN** `AgentState` contains 2 design entries and `parameters: { buildingType: "House" }`
- **WHEN** the agent calls `reset_design` with `design_ids` omitted and `clear_all_parameters: false` and `clear_parameters` omitted
- **THEN** `AgentState.designs` SHALL be an empty array
- **AND** `AgentState.parameters` SHALL remain `{ buildingType: "House" }`

### Requirement: reset_design return value format

The `reset_design` handler SHALL return a human-readable summary string describing what was done. The summary SHALL include:
- Number of designs removed and their IDs (if any)
- Parameter fields cleared (if any)
- Count of remaining designs
- Key-value pairs of remaining parameters

For error cases, the handler SHALL return an error string listing valid values and make no state changes.

#### Scenario: Successful compound reset return value

- **GIVEN** `AgentState` contains designs `[1, 2, 3]` and `parameters: { buildingType: "House", floorPlanDimensions: "10x15m", location: "Bratislava" }`
- **WHEN** the agent calls `reset_design` with `design_ids: [1, 3]` and `clear_parameters: ["floorPlanDimensions"]`
- **THEN** the return string SHALL contain "Removed 2 design(s)" and "IDs: 1, 3" and "Cleared parameters: floorPlanDimensions" and "Remaining designs: 1" and "Remaining parameters" including `buildingType` and `location`

### Requirement: reset_design documented in agent system prompt

The agent's system prompt in `agent/src/agent.py` SHALL include a `- reset_design:` section documenting the tool's parameters and usage rules. The documentation SHALL include:
- Parameter descriptions for `design_ids`, `clear_parameters`, and `clear_all_parameters`
- The list of valid `clear_parameters` field names
- Usage rules:
  - Use `clear_parameters` for selective field changes when the user wants to keep some values
  - Use `clear_all_parameters: true` only when the user explicitly says "start over", "clear everything", or equivalent
  - Always confirm to the user what was cleared and what was preserved

#### Scenario: Agent system prompt contains reset_design documentation

- **GIVEN** the agent system prompt in `agent/src/agent.py`
- **WHEN** the system prompt is read
- **THEN** it SHALL contain the string `reset_design`
- **AND** it SHALL contain the string `clear_parameters`
- **AND** it SHALL contain the string `clear_all_parameters`
- **AND** it SHALL contain the string `design_ids`
- **AND** it SHALL contain usage rules distinguishing selective clearing from full reset
