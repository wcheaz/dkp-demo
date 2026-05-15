## ADDED Requirements

### Requirement: generate_quote tool
The system SHALL register an async `generate_quote` tool on the agent that accepts `floor_plan_dimensions: str`, `roof_type: str`, `roof_pitch: int = 30`, `building_type: str = "Family house"` and returns a deterministic EUR price estimate.

#### Scenario: Valid dimensions parsed
- **WHEN** `floor_plan_dimensions` matches the pattern `(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?`
- **THEN** width and height SHALL be extracted and `floor_area` computed as `width * height`

#### Scenario: Invalid dimensions format
- **WHEN** `floor_plan_dimensions` cannot be parsed
- **THEN** the tool SHALL return `"Error: Could not parse floor plan dimensions. Expected format like '10x15m'."`

#### Scenario: Cost components calculated
- **WHEN** valid dimensions are provided
- **THEN** the following SHALL be computed: `total_joints = round(floor_area * 1.32)`, `timber_volume = floor_area * 0.254`, `total_trusses = round(floor_area * 0.147)`

#### Scenario: CZK costs computed
- **WHEN** cost components are calculated
- **THEN** `gusset_plate_cost = total_joints * 40`, `timber_cost = timber_volume * 4500`, `assembly_cost = (total_trusses / 20) * 15000`, `hanger_cost = total_trusses * 100`

#### Scenario: Roof type factor applied
- **WHEN** `roof_type` is provided (case-insensitive)
- **THEN** the factor SHALL be: Gable=1.0, Hip=1.3, Mono-pitch=0.9, Flat=0.8; unknown types default to 1.0

#### Scenario: Final EUR price formatted
- **WHEN** all calculations complete
- **THEN** `total_eur = round(total_czk / 25)` and the tool SHALL return `"Estimated price: €{formatted_eur} (excl. VAT)"` with comma-separated thousands
