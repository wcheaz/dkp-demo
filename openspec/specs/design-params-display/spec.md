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
Each parameter field SHALL be displayed as a key-value row with a human-readable label and the current value. Labels SHALL use the following mapping: `buildingType` → "Building Type", `floorPlanDimensions` → "Floor Plan Dimensions", `roofType` → "Roof Type", `roofPitch` → "Roof Pitch", `atticUsage` → "Attic Usage", `eavesShape` → "Eaves Shape", `wallConstruction` → "Wall Construction", `location` → "Location", `overhang` → "Overhang". **When a design entry has a `price` field, the price SHALL be rendered as an additional cell in the parameter grid with label "Price" and the price value, using CSS custom property classes defined in `src/app/globals.css` (e.g. `bg-design-price-bg`) with a light green background distinct from the teal background (`bg-design-param-bg`) used by other parameter cells.**

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

#### Scenario: Design entry with price renders price cell with green background
- **WHEN** a `DesignEntry` has `price: "€1,752"` and at least one other filled parameter
- **THEN** the parameter grid SHALL include a cell with label "Price" and value "€1,752"
- **AND** the price cell SHALL have a light green background class (e.g. `bg-green-100`)
- **AND** all other parameter cells SHALL retain their existing teal background (`bg-design-param-bg`)

#### Scenario: Design entry without price renders no price cell
- **WHEN** a `DesignEntry` has no `price` field (undefined or null)
- **THEN** the parameter grid SHALL NOT include a "Price" cell
- **AND** the grid SHALL render only the filled parameter fields as before

#### Scenario: Price cell completes the 5×2 grid
- **WHEN** a `DesignEntry` has all 9 parameter fields filled AND a `price` value
- **THEN** the parameter grid SHALL render exactly 10 cells (9 parameters + 1 price) in a 5-row × 2-column layout with no empty trailing cell

### Requirement: DesignComponent receives parameters from state
`DesignComponent` SHALL read `state.parameters` from its `AgentState` prop. The component SHALL NOT fetch parameters from any external source or API.

#### Scenario: Component reads parameters from state prop
- **WHEN** `DesignComponent` is rendered with `state` containing `parameters: { buildingType: "Garage", roofPitch: 15 }`
- **THEN** the parameter display SHALL show "Building Type: Garage" and "Roof Pitch: 15".

#### Scenario: Component handles undefined parameters
- **WHEN** `DesignComponent` is rendered with `state` where `parameters` is `undefined`
- **THEN** the component SHALL treat `parameters` as an empty object `{}` and render all fields with their empty-state display ("—" for optional, "⚠ Required" for missing required fields).

### Requirement: Price cell uses distinct green styling via CSS custom properties
The price cell in the parameter grid SHALL use CSS custom properties defined in `src/app/globals.css` under the `@theme` block, following the existing `--color-design-param-*` pattern. New variables SHALL include `--color-design-price-bg` (light green background, e.g. `rgba(34, 197, 94, 0.15)`), `--color-design-price-label` (green-tinted label text), and `--color-design-price-value` (price value text color). The component SHALL use `bg-design-price-bg` (not an inline Tailwind utility like `bg-green-100`) for the price cell background. The price cell label SHALL be "Price" and the value SHALL display the price string exactly as provided by the agent.

#### Scenario: Price cell background is green not teal
- **WHEN** the parameter grid renders both a regular parameter cell and a price cell
- **THEN** the regular parameter cell SHALL have `bg-design-param-bg` (teal) as its background class
- **AND** the price cell SHALL have `bg-design-price-bg` (light green) as its background class
- **AND** the two cells SHALL be visually distinguishable by background color

#### Scenario: Price styling uses CSS variables not inline classes
- **WHEN** the price cell implementation in `src/components/design-component.tsx` is inspected
- **THEN** the price cell background SHALL use `bg-design-price-bg` (a CSS custom property class)
- **AND** the price cell SHALL NOT use inline Tailwind color utilities like `bg-green-100` or `bg-green-500`
- **AND** `src/app/globals.css` SHALL contain `--color-design-price-bg` in the `@theme` block

#### Scenario: Price value displays as provided
- **WHEN** a `DesignEntry` has `price: "€2,340"`
- **THEN** the price cell SHALL display "€2,340" as the value text
- **AND** the price value SHALL NOT be reformatted, recalculated, or truncated
