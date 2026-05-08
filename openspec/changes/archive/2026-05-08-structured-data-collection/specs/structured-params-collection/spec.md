## ADDED Requirements

### Requirement: DesignParameters model on backend
A `DesignParameters` Pydantic model SHALL be defined in `agent/src/agent.py` with the following fields, all defaulting to `None`: `buildingType: Optional[str]`, `floorPlanDimensions: Optional[str]`, `roofType: Optional[str]`, `roofPitch: Optional[int]`, `atticUsage: Optional[str]`, `eavesShape: Optional[str]`, `wallConstruction: Optional[str]`, `location: Optional[str]`, `overhang: Optional[str]`.

#### Scenario: DesignParameters instantiates with all fields None
- **WHEN** `DesignParameters()` is created with no arguments
- **THEN** all nine fields SHALL be `None`.

#### Scenario: DesignParameters accepts partial field assignment
- **WHEN** `DesignParameters(buildingType="Family house", roofPitch=35)` is created
- **THEN** `buildingType` SHALL be `"Family house"`, `roofPitch` SHALL be `35`, and all other fields SHALL be `None`.

### Requirement: DesignParameters model on frontend
A `DesignParameters` TypeScript interface SHALL be exported from `src/lib/types.ts` with the following optional fields: `buildingType?: string`, `floorPlanDimensions?: string`, `roofType?: string`, `roofPitch?: number`, `atticUsage?: string`, `eavesShape?: string`, `wallConstruction?: string`, `location?: string`, `overhang?: string`.

#### Scenario: DesignParameters interface compiles with all fields optional
- **WHEN** TypeScript compilation is run on `src/lib/types.ts`
- **THEN** the file SHALL compile without errors and `DesignParameters` SHALL be an exported interface with all nine fields optional.

#### Scenario: Empty object satisfies DesignParameters
- **WHEN** an object `{}` is assigned to a variable of type `DesignParameters`
- **THEN** TypeScript SHALL accept it without errors.

### Requirement: YourState carries DesignParameters
`YourState` in `agent/src/agent.py` SHALL include a `parameters: DesignParameters` field initialized to `DesignParameters()` (an empty instance).

#### Scenario: YourState instantiates with empty parameters
- **WHEN** `YourState()` is created
- **THEN** `state.parameters` SHALL be a `DesignParameters` instance with all fields set to `None`.

### Requirement: AgentState carries DesignParameters
`AgentState` in `src/lib/types.ts` SHALL include a `parameters: DesignParameters` field alongside the existing `designs: DesignEntry[]` field. The `initialState` passed to `useCoAgent` in `src/app/page.tsx` SHALL initialize `parameters` to an empty object `{}`.

#### Scenario: AgentState type includes parameters field
- **WHEN** TypeScript compilation is run on `src/lib/types.ts`
- **THEN** `AgentState` SHALL have exactly two fields: `designs: DesignEntry[]` and `parameters: DesignParameters`.

#### Scenario: useCoAgent initialState includes empty parameters
- **WHEN** `src/app/page.tsx` is inspected for the `useCoAgent` call
- **THEN** the `initialState` SHALL include `parameters: {}`.

### Requirement: update_design_parameters frontend tool is registered
A frontend tool named `update_design_parameters` SHALL be registered using `useFrontendTool` inside the `YourMainContent` component in `src/app/page.tsx`. The tool SHALL accept the following optional string parameters: `building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch` (string representation of number), `attic_usage`, `eaves_shape`, `wall_construction`, `location`, `overhang`. The tool handler SHALL merge any provided fields into `state.parameters` via `setState` and return a summary string.

#### Scenario: Tool updates a single field
- **WHEN** the agent calls `update_design_parameters` with `building_type: "Family house"` and no other arguments
- **THEN** `setState` SHALL be called with a new state where `state.parameters.buildingType` is `"Family house"` and all other parameter fields remain unchanged.

#### Scenario: Tool updates multiple fields simultaneously
- **WHEN** the agent calls `update_design_parameters` with `roof_type: "Gable"` and `roof_pitch: "35"`
- **THEN** `setState` SHALL be called with a new state where `state.parameters.roofType` is `"Gable"` and `state.parameters.roofPitch` is `35` (converted from string to number).

#### Scenario: Tool preserves existing parameter values
- **WHEN** `state.parameters` already has `buildingType: "Garage"` and the tool is called with `roof_type: "Flat"`
- **THEN** `state.parameters.buildingType` SHALL remain `"Garage"` after the update.

#### Scenario: Tool handles undefined parameters state
- **WHEN** `state.parameters` is `undefined`
- **THEN** the tool SHALL treat it as an empty object `{}` and merge the provided fields into it.

### Requirement: update_design_parameters returns missing-field summary
The `update_design_parameters` frontend tool SHALL return a string that lists: (a) the fields that were updated, (b) which of the four required fields (`buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`) are still missing (null or empty), and (c) whether all required fields are now complete.

#### Scenario: Return indicates missing required fields
- **WHEN** the tool is called with `building_type: "Family house"` and no other arguments
- **THEN** the return string SHALL list `buildingType` as updated and SHALL indicate that `floorPlanDimensions`, `roofType`, and `roofPitch` are still missing required values.

#### Scenario: Return indicates all required fields complete
- **WHEN** the tool is called and after the update all four required fields have non-null, non-empty values
- **THEN** the return string SHALL indicate that all required parameters are complete.

### Requirement: Agent system prompt includes collection instructions
The agent's `system_prompt` in `agent/src/agent.py` SHALL include instructions that: (1) define the four required parameter fields and their valid values, (2) instruct the agent to extract parameter values from user messages and call `update_design_parameters` with extracted values, (3) instruct the agent to check the tool's return value for missing required fields, (4) instruct the agent to ask for missing fields specifically if any remain, (5) instruct the agent to confirm all parameters with the user before proceeding to any design-related discussion.

#### Scenario: System prompt references update_design_parameters
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL contain the text `update_design_parameters`.

#### Scenario: System prompt lists required fields
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL contain the field names `buildingType` (or equivalent descriptive text), `floorPlanDimensions`, `roofType`, and `roofPitch`.

#### Scenario: System prompt preserves existing tool instructions
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL still contain references to `get_knowledge_summary`, `query_knowledge_base`, `add_design_entry`, and `modify_design_entry`.

### Requirement: useCopilotReadable includes parameters
The `useCopilotReadable` call in `src/app/page.tsx` SHALL serialize both `designs` and `state.parameters` in its `value` field so the agent can see the current parameter state.

#### Scenario: CopilotReadable value includes parameters
- **WHEN** `src/app/page.tsx` is inspected for the `useCopilotReadable` call
- **THEN** the `value` field SHALL include a JSON-serialized representation of `state.parameters`.

### Requirement: All code passes lint and type checking
The modified files SHALL pass all lint and type checking commands.

#### Scenario: Agent passes ruff check
- **WHEN** `cd agent && python -m ruff check .` is run
- **THEN** the command SHALL exit zero with no errors.

#### Scenario: Agent passes mypy
- **WHEN** `cd agent && python -m mypy .` is run
- **THEN** the command SHALL exit zero with no errors.

#### Scenario: Frontend passes TypeScript check
- **WHEN** `npx tsc --noEmit` is run
- **THEN** the command SHALL exit zero with no errors.

#### Scenario: Frontend passes lint
- **WHEN** `npm run lint` is run
- **THEN** the command SHALL exit zero with no errors.
