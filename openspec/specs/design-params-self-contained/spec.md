## Purpose

Defines the capability for each design entry to carry its own self-contained parameters, provided directly by the agent at design creation time. No parameter data is read from or written to global shared state during design creation.

## Requirements

### Requirement: generate_design accepts all 9 parameter fields as optional arguments
The `generate_design` frontend tool in `src/app/page.tsx` SHALL accept the following optional string parameters in addition to the existing required `prompt_text`: `building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`, `attic_usage`, `eaves_shape`, `wall_construction`, `location`, `overhang`. The handler SHALL construct a `DesignParameters` object from these arguments and assign it to the new `DesignEntry.parameters` field. The handler SHALL NOT read `state.parameters` or any ref-based proxy for it.

#### Scenario: Design created with all parameter fields provided
- **WHEN** the agent calls `generate_design` with `prompt_text: "Gable house"` and all 9 parameter fields populated
- **THEN** the new `DesignEntry` SHALL have `parameters` containing all 9 fields with the provided values

#### Scenario: Design created with partial parameter fields
- **WHEN** the agent calls `generate_design` with `prompt_text: "Gable house"` and only `roof_type: "Gable"` and `roof_pitch: "35"`
- **THEN** the new `DesignEntry` SHALL have `parameters` containing `roofType: "Gable"` and `roofPitch: 35` with all other parameter fields unset

#### Scenario: Design created with no parameter fields
- **WHEN** the agent calls `generate_design` with only `prompt_text: "Gable house"` and no parameter arguments
- **THEN** the new `DesignEntry` SHALL have `parameters` set to an empty object `{}`

### Requirement: generate_design handler does not read global state parameters
The `generate_design` handler SHALL NOT reference `state.parameters`, `currentState.parameters`, `latestStateRef`, or any other global state proxy for parameter data. All parameter data on the new `DesignEntry` SHALL come exclusively from the tool's own arguments.

#### Scenario: generate_design handler contains no state.parameters reference
- **WHEN** the `generate_design` handler implementation in `src/app/page.tsx` is inspected
- **THEN** the handler body SHALL NOT contain the string `state.parameters` or `currentState.parameters`

#### Scenario: Multiple designs generated with different parameters
- **WHEN** the agent calls `generate_design` with Design 1 params (Gable, 35 degrees) followed by `generate_design` with Design 2 params (Mono-pitch, 2.5 degrees) in rapid succession
- **THEN** Design 1's `parameters.roofType` SHALL be `"Gable"` and Design 2's `parameters.roofType` SHALL be `"Mono-pitch"`
- **AND** Design 2 SHALL NOT contain any parameter values from Design 1

### Requirement: roof_type parameter determines design image
The `generate_design` handler SHALL use the `roof_type` tool argument (not `state.parameters.roofType`) to select the image via the `ROOF_TYPE_IMAGE_MAP` lookup. If `roof_type` is not provided or not in the map, the handler SHALL default to `"/design-gable.svg"`.

#### Scenario: roof_type argument selects correct image
- **WHEN** the agent calls `generate_design` with `roof_type: "Hip"`
- **THEN** the design entry SHALL resolve to `imageUrl: "/design-hip.svg"` after the generation delay

#### Scenario: Missing roof_type defaults to gable
- **WHEN** the agent calls `generate_design` without `roof_type`
- **THEN** the design entry SHALL resolve to `imageUrl: "/design-gable.svg"` after the generation delay

### Requirement: latestStateRef and related useEffect are removed
The `latestStateRef` ref, the `useEffect` that syncs it (`latestStateRef.current = state`), and all `latestStateRef.current` reads SHALL be removed from `src/app/page.tsx`. No ref-based state access workarounds SHALL exist in any tool handler.

#### Scenario: No latestStateRef in page.tsx
- **WHEN** `src/app/page.tsx` is searched for the string `latestStateRef`
- **THEN** zero occurrences SHALL be found
