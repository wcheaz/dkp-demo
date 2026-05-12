## MODIFIED Requirements

### Requirement: Parameter display shows field labels and values
Each parameter field SHALL be displayed as a key-value row with a human-readable label and the current value. Labels SHALL use the following mapping: `buildingType` → "Building Type", `floorPlanDimensions` → "Floor Plan Dimensions", `roofType` → "Roof Type", `roofPitch` → "Roof Pitch", `atticUsage` → "Attic Usage", `eavesShape` → "Eaves Shape", `wallConstruction` → "Wall Construction", `location` → "Location", `overhang` → "Overhang". **When a design entry has a `price` field, the price SHALL be rendered as an additional cell in the parameter grid with label "Price" and the price value, using CSS custom property classes defined in `src/app/globals.css` (e.g. `bg-design-price-bg`) with a light green background distinct from the teal background (`bg-design-param-bg`) used by other parameter cells.** The price cell SHALL also include an inline SVG info icon ("!" in a circle) after the price value. The info icon SHALL be 16×16px, use a muted color, and have `cursor: pointer`. Clicking the info icon SHALL open the `PricingBreakdownModal` component (from `src/components/pricing-breakdown-modal.tsx`) by setting the modal open state to `true`.

#### Scenario: Filled parameter shows its value
- **WHEN** `state.parameters.buildingType` is `"Family house"`
- **THEN** the parameter display SHALL show a row with label "Building Type" and value "Family house".

#### Scenario: Empty optional parameter shows dash
- **WHEN** `state.parameters.location` is `undefined` or `null`
- **THEN** the parameter display SHALL show a row with label "Location" and value "—".

#### Scenario: Empty required parameter shows required indicator
- **WHEN** `state.parameters.roofType` is `undefined` or `null`
- **THEN** the parameter display SHALL show a row with label "Roof Type" and value "⚠ Required" with distinct styling (e.g., different text color).

#### Scenario: Design entry with price renders price cell with green background and info icon
- **WHEN** a `DesignEntry` has `price: "€1,752"` and at least one other filled parameter
- **THEN** the parameter grid SHALL include a cell with label "Price" and value "€1,752"
- **AND** the price cell SHALL have a light green background class (e.g. `bg-design-price-bg`)
- **AND** all other parameter cells SHALL retain their existing teal background (`bg-design-param-bg`)
- **AND** the price cell SHALL render an SVG info icon ("!" circle, 16×16px) after the price value text

#### Scenario: Design entry without price renders no price cell or info icon
- **WHEN** a `DesignEntry` has no `price` field (undefined or null)
- **THEN** the parameter grid SHALL NOT include a "Price" cell
- **AND** no info icon SHALL be rendered

#### Scenario: Price cell completes the 5×2 grid
- **WHEN** a `DesignEntry` has all 9 parameter fields filled AND a `price` value
- **THEN** the parameter grid SHALL render exactly 10 cells (9 parameters + 1 price) in a 5-row × 2-column layout with no empty trailing cell

#### Scenario: Clicking info icon opens pricing breakdown modal
- **WHEN** a `DesignEntry` has a `price` field and the user clicks the info icon in the price cell
- **THEN** the `PricingBreakdownModal` SHALL open with the entry's `parameters` and `price` passed as props

#### Scenario: Closing modal hides pricing breakdown
- **WHEN** the `PricingBreakdownModal` is open and the user dismisses it (backdrop click or Escape)
- **THEN** the modal SHALL close and the price cell with info icon SHALL remain visible
