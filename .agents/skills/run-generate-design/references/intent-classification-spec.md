## ADDED Requirements

### Requirement: Classify user input into one of six intent categories
The system SHALL analyze the user's message and classify it into exactly one of: `design-generation`, `knowledge-query`, `pricing-quote`, `design-modification`, `design-reset`, or `general-response`.

#### Scenario: Design generation intent
- **WHEN** the user's message contains any of: "I need a design", "design for", "show me", "build me", "create", "generate", "plan for", "I want", or describes a construction project (EN); OR "potrebujem návrh", "navrhni", "chcem návrh", "potrebujem strechu", "návrh pre", "chcem" (SK)
- **THEN** the intent SHALL be classified as `design-generation`

#### Scenario: Knowledge query intent — overview
- **WHEN** the user asks "What projects do you have?", "What do you know?", or similar general questions about available information (EN); OR "aké projekty máte", "čo viete", "aké informácie máte", "prehľad" (SK)
- **THEN** the intent SHALL be classified as `knowledge-query` with sub-type `summary`

#### Scenario: Knowledge query intent — specific
- **WHEN** the user asks about projects, load calculations, materials, truss designs, or engineering specifications (EN); OR otázky o zaťažení, materiáloch, väzníkoch, technických parametroch (SK)
- **THEN** the intent SHALL be classified as `knowledge-query` with sub-type `specific`

#### Scenario: Pricing quote intent
- **WHEN** the user asks about pricing, cost, or estimated price (EN); OR "cena", "koľko", "odhadovaná cena", "stojí" (SK)
- **THEN** the intent SHALL be classified as `pricing-quote`

#### Scenario: Design modification intent
- **WHEN** the user wants to modify an existing design entry's image or prompt text
- **THEN** the intent SHALL be classified as `design-modification`

#### Scenario: Design reset intent — partial
- **WHEN** the user says "change X and Y but keep Z" (EN); OR "zmeň X a Y ale nechaj Z" (SK)
- **THEN** the intent SHALL be classified as `design-reset` with `remove_designs=false`

#### Scenario: Design reset intent — full removal
- **WHEN** the user says "scrap this design", "delete this design", or "start over completely" (EN); OR "začnime odznova", "zmazať návrh", "vymazať", "odznova" (SK)
- **THEN** the intent SHALL be classified as `design-reset` with `remove_designs=true`

#### Scenario: General response intent
- **WHEN** the user's message does not match any of the above patterns
- **THEN** the intent SHALL be classified as `general-response`

<!-- ---- KNOWLEDGE BOUNDARY CONSTRAINTS (remove if agent becomes too weak) ---- -->
- **AND** the agent SHALL first search the knowledge base before responding.
  If no relevant KB results exist, the agent SHALL inform the user that the
  information is not available, rather than answering from general knowledge.
<!-- ---- END KNOWLEDGE BOUNDARY CONSTRAINTS ---- -->

### Requirement: Multiple intents may co-occur
The system SHALL detect when both `design-generation` and `pricing-quote` are present in the same message (e.g., "I need a design with a price").

#### Scenario: Design plus pricing
- **WHEN** the user requests a design AND mentions pricing
- **THEN** both `design-generation` and `pricing-quote` intents SHALL be flagged, with pricing executed first and the price passed to the design generation
