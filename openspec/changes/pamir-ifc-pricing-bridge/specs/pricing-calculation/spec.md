## MODIFIED Requirements

### Requirement: Pricing formula uses fixed coefficients
The `generate_quote` tool SHALL compute the total price using the following calibrated deterministic formula to align with Pamir quote metrics:

1. Parse `floor_plan_dimensions` (e.g. "10x15m") to extract width and height in meters. Floor area = width × height.
2. Compute simulated structural outputs:
   - `totalJoints` = floor_area × 1.32 (rounded)
   - `timberVolume` = floor_area × 0.254
   - `totalTrusses` = floor_area × 0.147 (rounded)
   - `supportNodes` = totalTrusses * 2
   - `bracketCount` = round(supportNodes * 1.6)
3. Apply roof type complexity factor: Gable = 1.0, Hip = 1.3, Mono-pitch = 0.9, Flat = 0.8.
4. Compute components:
   - `gussetPlateCost` = totalJoints * 50 CZK
   - `timberCost` = timberVolume * 6200 CZK/m³
   - `assemblyCost` = (totalTrusses / 20) * 18000 CZK
   - `hangerCost` = totalTrusses * 120 CZK
   - `metalworkCost` = bracketCount * 370 CZK
5. `totalCZK` = (gussetPlateCost + timberCost + assemblyCost + hangerCost + metalworkCost) * roofTypeFactor.
6. `totalEUR` = totalCZK / 25 (rounded to nearest integer).
7. Return formatted string: "Estimated price: €{totalEUR} (excl. VAT)".

#### Scenario: Formula produces consistent results for known input
- **WHEN** `generate_quote` is called with `floor_plan_dimensions: "10x15m"`, `roof_type: "Gable"`, `roof_pitch: 35`, `building_type: "Family house"`
- **THEN** floor area SHALL be 150 m², totalJoints ≈ 198, timberVolume ≈ 38.1, totalTrusses ≈ 22, bracketCount ≈ 70
- **AND** the returned price SHALL be identical across repeated calls with the same arguments

#### Scenario: Roof type factor affects price
- **WHEN** the same floor plan dimensions are used with `roof_type: "Hip"` vs `roof_type: "Gable"`
- **THEN** the Hip roof price SHALL be exactly 1.3× the Gable roof price (before rounding)
