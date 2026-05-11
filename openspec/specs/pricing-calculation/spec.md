## Purpose

Defines the backend pricing engine that computes deterministic cost estimates from design parameters. Used by the agent to generate price quotes for roof/truss designs based on floor plan area, roof type, and building type.

## Requirements

### Requirement: generate_quote backend tool computes deterministic price
The agent SHALL expose a `generate_quote` backend tool in `agent/src/agent.py` that accepts design parameters and returns a deterministic cost estimate. The tool SHALL accept these arguments: `floor_plan_dimensions` (string, e.g. "10x15m"), `roof_type` (string: Gable, Hip, Mono-pitch, or Flat), `roof_pitch` (integer, degrees), `building_type` (string). The tool SHALL return a formatted string containing the total estimated price in EUR.

#### Scenario: Gable roof family house pricing
- **WHEN** `generate_quote` is called with `floor_plan_dimensions: "10x15m"`, `roof_type: "Gable"`, `roof_pitch: 35`, `building_type: "Family house"`
- **THEN** the tool SHALL return a string containing a total price in EUR (e.g. "€1,752") computed deterministically from the pricing formula
- **AND** calling with identical arguments SHALL always produce the same total price

#### Scenario: Hip roof pricing
- **WHEN** `generate_quote` is called with `floor_plan_dimensions: "17x11m"`, `roof_type: "Hip"`, `roof_pitch: 25`, `building_type: "Family house"`
- **THEN** the tool SHALL return a total price that is higher than the gable roof example for the same floor area, due to the hip roof complexity factor

#### Scenario: Missing optional parameters still produces a price
- **WHEN** `generate_quote` is called with only `floor_plan_dimensions: "10x15m"` and `roof_type: "Gable"`
- **THEN** the tool SHALL still compute and return a price using defaults for missing parameters (default pitch: 30, default building type: "Family house")

### Requirement: Pricing formula uses fixed coefficients
The `generate_quote` tool SHALL compute the total price using the following deterministic formula:

1. Parse `floor_plan_dimensions` (e.g. "10x15m") to extract width and height in meters. Floor area = width × height.
2. Compute simulated structural outputs: `totalJoints` = floor_area × 1.32 (rounded), `timberVolume` = floor_area × 0.254, `totalTrusses` = floor_area × 0.147 (rounded).
3. Apply roof type complexity factor: Gable = 1.0, Hip = 1.3, Mono-pitch = 0.9, Flat = 0.8.
4. Compute components: `gussetPlateCost` = totalJoints × 40 CZK, `timberCost` = timberVolume × 4500 CZK/m³, `assemblyCost` = (totalTrusses / 20) × 15000 CZK, `hangerCost` = totalTrusses × 100 CZK.
5. `totalCZK` = (gussetPlateCost + timberCost + assemblyCost + hangerCost) × roofTypeFactor.
6. `totalEUR` = totalCZK / 25 (rounded to nearest integer).
7. Return formatted string: "Estimated price: €{totalEUR} (excl. VAT)".

#### Scenario: Formula produces consistent results for known input
- **WHEN** `generate_quote` is called with `floor_plan_dimensions: "10x15m"`, `roof_type: "Gable"`, `roof_pitch: 35`, `building_type: "Family house"`
- **THEN** floor area SHALL be 150 m², totalJoints ≈ 198, timberVolume ≈ 38.1, totalTrusses ≈ 22
- **AND** the returned price SHALL be identical across repeated calls with the same arguments

#### Scenario: Roof type factor affects price
- **WHEN** the same floor plan dimensions are used with `roof_type: "Hip"` vs `roof_type: "Gable"`
- **THEN** the Hip roof price SHALL be exactly 1.3× the Gable roof price (before rounding)

### Requirement: Agent system prompt instructs when to call generate_quote
The agent's system prompt in `agent/src/agent.py` SHALL include instructions telling the agent to call `generate_quote` when the user asks about pricing, cost, or estimated price for a design. The agent SHALL pass the collected design parameters to the tool and relay the result to the user. The agent SHALL also pass the returned price value to `generate_design` as the `price` argument when creating or updating a design entry.

#### Scenario: User asks for price estimate
- **WHEN** the user asks "What is the estimated price?" after design parameters have been collected
- **THEN** the agent SHALL call `generate_quote` with the collected parameters
- **AND** the agent SHALL include the price in its response to the user

#### Scenario: Agent passes price to generate_design
- **WHEN** the agent calls `generate_quote` and receives a price
- **AND** the agent subsequently calls `generate_design` for the same design
- **THEN** the agent SHALL pass the price value as the `price` argument to `generate_design`
