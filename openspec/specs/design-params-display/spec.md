## Purpose

Defines the frontend rendering of collected structured design parameters within the design component area. Utilitarian display for demo/testing visibility — lists parameter field names and values.

## Requirements

### Requirement: DesignComponent renders a parameter display section
`DesignComponent` in `src/components/design-component.tsx` SHALL render a parameter display section above the design cards scrollable container. The section SHALL display when `state.parameters` exists, regardless of whether any fields are filled.

#### Scenario: Parameter section renders when parameters exist
- **WHEN** `DesignComponent` is rendered with `state.parameters` set to an object (even an empty one)
- **THEN** the component SHALL render a parameter display section above the design cards area.

#### Scenario: Parameter section title is visible
- **WHEN** the parameter display section is rendered
- **THEN** the section SHALL contain a heading with the text "Design Parameters".

### Requirement: Parameter display shows field labels and values
Each parameter field SHALL be displayed as a key-value row with a human-readable label and the current value. Labels SHALL use the following mapping: `buildingType` → "Building Type", `floorPlanDimensions` → "Floor Plan Dimensions", `roofType` → "Roof Type", `roofPitch` → "Roof Pitch", `atticUsage` → "Attic Usage", `eavesShape` → "Eaves Shape", `wallConstruction` → "Wall Construction", `location` → "Location", `overhang` → "Overhang".

#### Scenario: Filled parameter shows its value
- **WHEN** `state.parameters.buildingType` is `"Family house"`
- **THEN** the parameter display SHALL show a row with label "Building Type" and value "Family house".

#### Scenario: Empty optional parameter shows dash
- **WHEN** `state.parameters.location` is `undefined` or `null`
- **THEN** the parameter display SHALL show a row with label "Location" and value "—".

#### Scenario: Empty required parameter shows required indicator
- **WHEN** `state.parameters.roofType` is `undefined` or `null`
- **THEN** the parameter display SHALL show a row with label "Roof Type" and value "⚠ Required" with distinct styling (e.g., different text color).

### Requirement: Parameter display renders as a flat list
The parameter display SHALL render all nine fields as a flat list of rows. There SHALL be no collapsible sections, tabs, or nested groupings. The display SHALL be utilitarian — no polished styling required.

#### Scenario: All nine fields are listed
- **WHEN** the parameter display section is rendered
- **THEN** exactly nine parameter rows SHALL be visible, one for each field: Building Type, Floor Plan Dimensions, Roof Type, Roof Pitch, Attic Usage, Eaves Shape, Wall Construction, Location, Overhang.

#### Scenario: Parameter display does not use modal or overlay
- **WHEN** the parameter display section is rendered
- **THEN** the parameter values SHALL be directly visible in the page flow without requiring a click, modal, or expansion.

### Requirement: DesignComponent receives parameters from state
`DesignComponent` SHALL read `state.parameters` from its `AgentState` prop. The component SHALL NOT fetch parameters from any external source or API.

#### Scenario: Component reads parameters from state prop
- **WHEN** `DesignComponent` is rendered with `state` containing `parameters: { buildingType: "Garage", roofPitch: 15 }`
- **THEN** the parameter display SHALL show "Building Type: Garage" and "Roof Pitch: 15".

#### Scenario: Component handles undefined parameters
- **WHEN** `DesignComponent` is rendered with `state` where `parameters` is `undefined`
- **THEN** the component SHALL treat `parameters` as an empty object `{}` and render all fields with their empty-state display ("—" for optional, "⚠ Required" for missing required fields).
