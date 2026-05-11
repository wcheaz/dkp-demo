## Purpose

Defines the structured data collection capability: the DesignParameters model shared between backend and frontend, the frontend tool for checking parameter completeness, the agent's iterative collection loop, and parameter visibility to the agent.

## Requirements

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

### Requirement: update_design_parameters frontend tool is registered
A frontend tool named `update_design_parameters` SHALL be registered using `useFrontendTool` inside the `YourMainContent` component in `src/app/page.tsx`. The tool SHALL accept the following optional string parameters: `building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch` (string representation of number), `attic_usage`, `eaves_shape`, `wall_construction`, `location`, `overhang`. The tool handler SHALL NOT call `setState` or mutate any shared state. The tool SHALL be a pure diagnostic function that computes and returns a summary of which fields were provided and which required fields are still missing.

#### Scenario: Tool returns summary without mutating state
- **WHEN** the agent calls `update_design_parameters` with `building_type: "Family house"` and no other arguments
- **THEN** the return string SHALL list `buildingType` as an updated field and SHALL indicate that `floorPlanDimensions`, `roofType`, and `roofPitch` are still missing required values
- **AND** `setState` SHALL NOT be called

#### Scenario: Tool returns all required fields complete
- **WHEN** the tool is called and all four required fields have non-null, non-empty values in the arguments
- **THEN** the return string SHALL indicate that all required parameters are complete

#### Scenario: Tool does not backfill parameters onto design entries
- **WHEN** the agent calls `update_design_parameters` with any arguments and `state.designs` contains entries with empty parameters
- **THEN** the handler SHALL NOT modify any existing `DesignEntry.parameters`

### Requirement: update_design_parameters returns missing-field summary
The `update_design_parameters` frontend tool SHALL return a string that lists: (a) the fields that were provided in the current call, (b) which of the four required fields (`buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch`) are still missing from the current call's arguments, and (c) whether all required fields are now present. The summary SHALL be computed from the tool's own arguments only, not from any persisted state.

#### Scenario: Return indicates missing required fields
- **WHEN** the tool is called with `building_type: "Family house"` and no other arguments
- **THEN** the return string SHALL list `buildingType` as provided and SHALL indicate that `floorPlanDimensions`, `roofType`, and `roofPitch` are still missing

#### Scenario: Return indicates all required fields complete
- **WHEN** the tool is called with all four required fields populated
- **THEN** the return string SHALL indicate that all required parameters are complete

### Requirement: Agent system prompt includes collection instructions
The agent's `system_prompt` in `agent/src/agent.py` SHALL include instructions that: (1) define the four required parameter fields and their valid values, (2) instruct the agent to extract parameter values from user messages and call `update_design_parameters` with extracted values to check completeness, (3) instruct the agent to check the tool's return value for missing required fields, (4) instruct the agent to ask for missing fields specifically if any remain, (5) instruct the agent to confirm all parameters with the user before proceeding to any design-related discussion, (6) instruct the agent to pass ALL collected parameter fields directly to `generate_design` when calling it.

#### Scenario: System prompt references update_design_parameters
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL contain the text `update_design_parameters`.

#### Scenario: System prompt instructs passing params to generate_design
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL instruct the agent to pass parameter fields as arguments to `generate_design`

#### Scenario: System prompt lists required fields
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL contain the field names `buildingType` (or equivalent descriptive text), `floorPlanDimensions`, `roofType`, and `roofPitch`.

#### Scenario: System prompt preserves existing tool instructions
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL still contain references to `get_knowledge_summary`, `query_knowledge_base`, `generate_design`, `modify_design_entry`, and `download_test_image`

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
