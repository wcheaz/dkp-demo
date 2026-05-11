## Purpose

Defines the capability for the agent to automatically create design entries by calling a frontend tool, enabling automatic population of the design gallery during agent responses.

## Requirements

### Requirement: generate_design is registered as a CopilotKit frontend tool
A frontend tool named `generate_design` SHALL be registered using `useFrontendTool` inside the `YourMainContent` component in `src/app/page.tsx`. The tool SHALL accept one required parameter: `prompt_text` (string). The tool SHALL also accept the following optional string parameters: `building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`, `attic_usage`, `eaves_shape`, `wall_construction`, `location`, `overhang`. The tool handler SHALL create a `DesignEntry` with `imageUrl: "/design-gable.svg"`, `promptText: prompt_text`, `status: "processing"`, and `parameters` constructed from the provided parameter arguments. The handler SHALL append the entry to `state.designs` and call `setState` with the updated state. The handler SHALL NOT read `state.parameters` or any ref-based proxy. The code SHALL be wrapped in `// DEMO-ONLY` comments. The handler SHALL start a 3-second `setTimeout` that resolves the entry to `status: "complete"` with the roof-type-mapped image URL.

#### Scenario: Frontend tool creates entry with design-specific parameters
- **WHEN** the agent calls `generate_design` with `prompt_text: "Gable house"` and `roof_type: "Gable"`, `roof_pitch: "35"`, `building_type: "Family house"`
- **THEN** `setState` SHALL be called with a new `DesignEntry` whose `parameters` contains `roofType: "Gable"`, `roofPitch: 35`, `buildingType: "Family house"`, and no other parameter fields

#### Scenario: Frontend tool appends without losing existing designs
- **WHEN** the agent calls `generate_design` and `state.designs` already contains one entry
- **THEN** `setState` SHALL be called with `state.designs` containing two entries: the original entry followed by the new entry

#### Scenario: Frontend tool handles undefined designs array
- **WHEN** the agent calls `generate_design` and `state.designs` is undefined
- **THEN** the handler SHALL treat `state.designs` as an empty array and append the new entry

#### Scenario: Processing spinner shown then resolved to complete
- **WHEN** the agent calls `generate_design`
- **THEN** the new entry SHALL have `status: "processing"` initially
- **AND** after 3 seconds the entry SHALL be updated to `status: "complete"` with the roof-type-mapped `imageUrl`

### Requirement: System prompt mandates calling generate_design after parameter confirmation
The agent's `system_prompt` in `agent/src/agent.py` SHALL include instructions telling the agent to call `generate_design` with the user's prompt text and all collected parameter fields after the user has confirmed all required parameters. The system prompt SHALL instruct the agent to pass every collected parameter field directly as an argument to `generate_design`.

#### Scenario: System prompt references generate_design with parameter passing
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL contain the text `generate_design`
- **AND** the prompt SHALL instruct the agent to pass parameter fields as arguments to `generate_design`

#### Scenario: System prompt preserves existing tool instructions
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL still contain references to `get_knowledge_summary`, `query_knowledge_base`, `modify_design_entry`, `download_test_image`, and `update_design_parameters`

### Requirement: All code passes lint and type checking
The modified files SHALL pass all lint and type checking commands.

#### Scenario: Agent passes ruff check
- **WHEN** `cd agent && python -m ruff check .` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Agent passes mypy
- **WHEN** `cd agent && python -m mypy .` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Frontend passes TypeScript check
- **WHEN** `npx tsc --noEmit` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Frontend passes lint
- **WHEN** `npm run lint` is run
- **THEN** the command SHALL exit zero with no errors
