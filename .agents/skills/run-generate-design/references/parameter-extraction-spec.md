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

### Requirement: English locale labels and parameter values
When the agent locale is `en`, the system SHALL use these English labels and parameter values for all user-facing output.

**Field labels (locale `en`):**

- Building type
- Floor plan dimensions
- Roof type
- Roof pitch
- Attic usage
- Eaves shape
- Wall construction
- Location
- Overhang

**Valid parameter values (locale `en`):**

- Building types: Family house, Apartment building, Garage, Agricultural building, Office building, Mixed-use building
- Roof types: Gable, Hip, Mono-pitch, Flat
- Attic usage: None, Storage, Living space
- Eaves shape: Open, Boxed, Flush
- Wall construction: Brick, SIP panels, Concrete block, Mixed

**Status values (locale `en`):** Design In Progress / Complete

#### Scenario: English field labels used for output
- **WHEN** locale is `en` and a design summary is rendered
- **THEN** the labels `Building type`, `Floor plan dimensions`, `Roof type`, `Roof pitch`, `Attic usage`, `Eaves shape`, `Wall construction`, `Location`, `Overhang` SHALL be used

#### Scenario: English parameter values used for output
- **WHEN** locale is `en` and a value is rendered for building type, roof type, attic usage, eaves shape, or wall construction
- **THEN** the value SHALL be drawn from the English valid parameter values list above

### Requirement: Slovak locale labels and parameter values
When the agent locale is `sk`, the system SHALL use these Slovak translations for all user-facing output (field labels, parameter values, and status text).

**Field labels (locale `sk`, English to Slovak):**

| English label | Slovak label |
|---|---|
| Building type | Typ budovy |
| Floor plan dimensions | Rozmery pôdorysu |
| Roof type | Typ strechy |
| Roof pitch | Sklon strechy |
| Attic usage | Využitie podkrovia |
| Eaves shape | Tvar rímsy |
| Wall construction | Konštrukcia stien |
| Location | Umiestnenie |
| Overhang | Previs |

**Parameter values (locale `sk`, English to Slovak):**

| English | Slovak |
|---|---|
| Family house | Rodinný dom |
| Apartment building | Bytový dom |
| Garage | Garáž |
| Agricultural building | Poľnohospodárska budova |
| Office building | Kancelárska budova |
| Mixed-use building | Zmiešaná budova |
| Gable | Štítová |
| Hip | Valbová |
| Mono-pitch | Jednosklovitá |
| Flat | Plochá |
| none | žiadne |
| storage | skladovací priestor |
| living space | obytný priestor |
| open | otvorené |
| boxed | uzatvorené |
| flush | hladké |
| brick | tehla |
| SIP panels | SIP panely |
| concrete block | betónové tvárnice |
| mixed | zmiešaná |

**Status values (locale `sk`, English to Slovak):**

| English | Slovak |
|---|---|
| Design In Progress | Návrh v procese |
| complete | dokončené |

#### Scenario: Slovak field labels used for output
- **WHEN** locale is `sk` and a design summary is rendered
- **THEN** the labels `Typ budovy`, `Rozmery pôdorysu`, `Typ strechy`, `Sklon strechy`, `Využitie podkrovia`, `Tvar rímsy`, `Konštrukcia stien`, `Umiestnenie`, `Previs` SHALL be used

#### Scenario: Slovak parameter values used for output
- **WHEN** locale is `sk` and a value is rendered
- **THEN** the value SHALL be drawn from the Slovak parameter values table above (e.g. `Rodinný dom`, `Štítová`)

### Requirement: Slovak trigger patterns recognised for extraction
In addition to the English trigger patterns, the system SHALL recognise these Slovak trigger patterns when scanning the user's message for parameter fields.

| Field | Slovak trigger patterns |
|---|---|
| `building_type` | "dom", "rodinný dom", "bytová budova", "garáž", "poľnohospodárska budova", "kancelárska budova", "zmiešaná budova" |
| `roof_type` | "štítová", "valbová", "jednosklovitá", "plochá" |
| `attic_usage` | "podkrovie", "skladovací priestor", "obytný priestor", "bez využitia", "žiadne" |
| `eaves_shape` | "otvorené okapy", "uzatvorené okapy", "hladké okapy" |
| `wall_construction` | "tehlové steny", "SIP panely", "betónové tvárnice", "zmiešaná konštrukcia" |

#### Scenario: Slovak roof type trigger recognised
- **WHEN** the user message contains "štítová", "valbová", "jednosklovitá", or "plochá"
- **THEN** `roof_type` SHALL be recorded with the corresponding English canonical value (Gable, Hip, Mono-pitch, Flat)
