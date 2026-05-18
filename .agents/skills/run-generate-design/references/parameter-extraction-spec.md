## ADDED Requirements

### Requirement: Extract all matching parameter fields from user input
The system SHALL scan the user's message for each of the 9 construction parameter fields and record any matches found. The system SHALL recognise both English and Slovak trigger patterns.

#### Scenario: Building type extracted
- **WHEN** the user mentions "house", "garage", "agricultural building", "family house", or similar building types (EN); OR "dom", "rodinný dom", "garáž", "poľnohospodárska budova", "kancelárska budova", "zmiešaná budova" (SK)
- **THEN** `building_type` SHALL be recorded with the extracted value

#### Scenario: Floor plan dimensions extracted
- **WHEN** the user mentions dimensions in the pattern `NxMm` (e.g., "10x15m", "8 x 12m")
- **THEN** `floor_plan_dimensions` SHALL be recorded with the normalized value (e.g., "10x15m")

#### Scenario: Roof type extracted
- **WHEN** the user mentions "gable", "hip", "mono-pitch", or "flat" roof (EN); OR "štítová", "valbová", "jednosklovitá", or "plochá" (SK)
- **THEN** `roof_type` SHALL be recorded with the value (must be one of: Gable, Hip, Mono-pitch, Flat)

#### Scenario: Roof pitch extracted
- **WHEN** the user mentions a degree value between 2 and 45 for roof pitch
- **THEN** `roof_pitch` SHALL be recorded as an integer

#### Scenario: Attic usage extracted
- **WHEN** the user mentions attic usage as "none", "storage", or "living space" (EN); OR "žiadne", "skladovací priestor", or "obytný priestor" (SK)
- **THEN** `attic_usage` SHALL be recorded

#### Scenario: Eaves shape extracted
- **WHEN** the user mentions "open", "boxed", or "flush" eaves (EN); OR "otvorené", "uzatvorené", or "hladké" okapy (SK)
- **THEN** `eaves_shape` SHALL be recorded

#### Scenario: Wall construction extracted
- **WHEN** the user mentions "brick", "SIP panels", "concrete block", or "mixed" wall construction (EN); OR "tehlové steny", "SIP panely", "betónové tvárnice", or "zmiešaná konštrukcia" (SK)
- **THEN** `wall_construction` SHALL be recorded

#### Scenario: Location extracted
- **WHEN** the user mentions a city or location name
- **THEN** `location` SHALL be recorded

#### Scenario: Overhang extracted
- **WHEN** the user mentions an overhang dimension (e.g., "450mm")
- **THEN** `overhang` SHALL be recorded

### Requirement: Partial extraction is valid
The system SHALL accept partial parameter sets. Any field not found in the user's message SHALL be marked as `---` (placeholder).

#### Scenario: Only some parameters provided
- **WHEN** the user provides only building_type and floor_plan_dimensions
- **THEN** those two fields SHALL have values and all other 7 fields SHALL be `---`

### Requirement: Four desirable fields identified for collection
The system SHALL prioritize collecting these four fields: `building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`.

#### Scenario: Desirable fields checklist
- **WHEN** parameter extraction completes
- **THEN** a checklist SHALL show which of the 4 desirable fields are present and which are missing
