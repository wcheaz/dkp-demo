## ADDED Requirements

### Requirement: Simulate get_knowledge_summary output
When the intent is `knowledge-query` with sub-type `summary`, the system SHALL read the locale-appropriate summary file and return its full contents. When locale is `sk`, read `agent/knowledge/trusses-ai-slovak/summary.md`. When locale is `en`, read `agent/knowledge/trusses-ai-english/summary.md`.

#### Scenario: Summary returned
- **WHEN** knowledge summary is requested
- **THEN** the output SHALL be the complete text of `summary.md`

### Requirement: Simulate query_knowledge_base output
When the intent is `knowledge-query` with sub-type `specific`, the system SHALL perform keyword scoring across the 33 project subdirectories and return markdown content from the top 3 matches.

#### Scenario: Keyword search across projects
- **WHEN** a specific knowledge query is received
- **THEN** the system SHALL select the knowledge base directory matching the current locale (`trusses-ai-slovak` for `sk`, `trusses-ai-english` for `en`)
- **THEN** each subdirectory in the selected knowledge base SHALL be scored: name matches get 2 points per word, section-content matches get 1 point per word
- **THEN** the top 3 scoring subdirectories SHALL have their `.md` files read and returned with `--- Source: <relative-path> ---` headers

#### Scenario: No matches found
- **WHEN** no subdirectory scores above zero
- **THEN** the first 3 subdirectories alphabetically SHALL be used as fallback

### Requirement: Simulate generate_quote output
When the intent is `pricing-quote`, the system SHALL compute the price using the deterministic calibrated Pamir formula and return a formatted string.

#### Scenario: Valid dimensions pricing
- **WHEN** `floor_plan_dimensions` is parseable as `NxMm`
- **THEN** compute: `floor_area = N * M`, `total_joints = round(floor_area * 1.32)`, `timber_volume = floor_area * 0.254`, `total_trusses = round(floor_area * 0.147)`, `support_nodes = total_trusses * 2`, `bracket_count = round(support_nodes * 1.6)`
- **THEN** compute CZK costs: `gusset_plates = joints * 50`, `timber = volume * 6200`, `assembly = (trusses/20) * 18000`, `hangers = trusses * 120`, `metalwork = bracket_count * 370`
- **THEN** apply roof type factor: Gable=1.0, Hip=1.3, Mono-pitch=0.9, Flat=0.8
- **THEN** compute `total_czk = (gusset_plates + timber + assembly + hangers + metalwork) * factor` and `total_eur = round(total_czk / 25)`
- **THEN** return the formatted string `"Estimated price: €{total_eur} (excl. VAT)"` where total_eur is an integer (EUR, excl. VAT)

#### Scenario: Missing floor_plan_dimensions
- **WHEN** `floor_plan_dimensions` was not extracted
- **THEN** the output SHALL ask the user to provide floor plan dimensions before a quote can be generated

### Requirement: Simulate generate_design output
When the intent is `design-generation`, the system SHALL produce a design entry with the extracted parameters and a prompt text summarizing the request.

#### Scenario: Design with partial parameters
- **WHEN** some parameters are `---`
- **THEN** the design entry SHALL show `---` for missing fields and include a "Design In Progress" status

#### Scenario: Design with full parameters
- **WHEN** all desirable fields are present
- **THEN** the design entry SHALL show all parameter values, "complete" status, and an automatically computed price from `generate_quote`

#### Scenario: Design with price
- **WHEN** pricing was also requested
- **THEN** the design entry SHALL include the price from `generate_quote` output

### Requirement: Simulate modify_design_entry output
When the intent is `design-modification`, the system SHALL produce a modified design entry with updated image and/or prompt text.

#### Scenario: Modification with preset image
- **WHEN** the user requests a design change with image name "design-alpha.svg" or "design-beta.svg"
- **THEN** the design entry SHALL be updated with the specified image

### Requirement: Simulate reset_design output
When the intent is `design-reset`, the system SHALL produce a confirmation of what was cleared and what was preserved.

#### Scenario: Partial reset
- **WHEN** `remove_designs=false` and specific `clear_parameters` are listed
- **THEN** only the named parameter fields SHALL be set to `---`, all others preserved, and the design entry SHALL remain in the list

#### Scenario: Full removal
- **WHEN** `remove_designs=true`
- **THEN** the targeted design entries SHALL be removed entirely from the list
