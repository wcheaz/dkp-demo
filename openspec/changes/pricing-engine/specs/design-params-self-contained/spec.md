## MODIFIED Requirements

### Requirement: generate_design accepts all 9 parameter fields as optional arguments
The `generate_design` frontend tool in `src/app/page.tsx` SHALL accept the following optional string parameters in addition to the existing required `prompt_text`: `building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`, `attic_usage`, `eaves_shape`, `wall_construction`, `location`, `overhang`, **and `price`**. The handler SHALL construct a `DesignParameters` object from the first 9 arguments and assign it to the new `DesignEntry.parameters` field. The `price` argument SHALL be stored directly on the `DesignEntry` as a top-level `price` field (not inside `parameters`). The handler SHALL NOT read `state.parameters` or any ref-based proxy for it.

#### Scenario: Design created with all parameter fields provided
- **WHEN** the agent calls `generate_design` with `prompt_text: "Gable house"` and all 9 parameter fields populated
- **THEN** the new `DesignEntry` SHALL have `parameters` containing all 9 fields with the provided values

#### Scenario: Design created with partial parameter fields
- **WHEN** the agent calls `generate_design` with `prompt_text: "Gable house"` and only `roof_type: "Gable"` and `roof_pitch: "35"`
- **THEN** the new `DesignEntry` SHALL have `parameters` containing `roofType: "Gable"` and `roofPitch: 35` with all other parameter fields unset

#### Scenario: Design created with no parameter fields
- **WHEN** the agent calls `generate_design` with only `prompt_text: "Gable house"` and no parameter arguments
- **THEN** the new `DesignEntry` SHALL have `parameters` set to an empty object `{}`

#### Scenario: Design created with price argument
- **WHEN** the agent calls `generate_design` with `prompt_text: "Gable house"`, `roof_type: "Gable"`, and `price: "€1,752"`
- **THEN** the new `DesignEntry` SHALL have `parameters.roofType` equal to `"Gable"` and `price` equal to `"€1,752"`
- **AND** the `price` value SHALL NOT appear inside the `parameters` object

#### Scenario: Design created without price argument
- **WHEN** the agent calls `generate_design` with `prompt_text: "Gable house"` and no `price` argument
- **THEN** the new `DesignEntry` SHALL have `price` set to `undefined` or not present

## ADDED Requirements

### Requirement: DesignEntry type includes price field
The `DesignEntry` interface in `src/lib/types.ts` SHALL include an optional `price` field of type `string`. The `DesignEntry` Pydantic model in `agent/src/agent.py` SHALL include an optional `price` field of type `Optional[str]` with default `None`.

#### Scenario: Frontend DesignEntry type accepts price
- **WHEN** a `DesignEntry` object is created with `{ id: 1, imageUrl: "/design.svg", promptText: "test", price: "€1,752" }`
- **THEN** TypeScript SHALL not raise a type error

#### Scenario: Backend DesignEntry model accepts price
- **WHEN** `DesignEntry(id=1, imageUrl="/design.svg", promptText="test", price="€1,752")` is constructed in Python
- **THEN** the model SHALL validate and store the price value
