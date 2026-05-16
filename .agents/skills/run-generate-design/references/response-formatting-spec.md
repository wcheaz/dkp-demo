## ADDED Requirements

### Requirement: Output must not contain emojis
The system SHALL NOT include emoji or pictograph characters in any output.

#### Scenario: No emojis in output
- **WHEN** the final response is composed
- **THEN** it SHALL NOT contain any emoji or pictograph characters

### Requirement: Output must use chat-friendly formatting
The system SHALL format responses as standard markdown chat messages — using markdown headings (`##`) and bold-labeled key-value lines. The system SHALL NOT use reStructuredText-style underlines (`===`, `---`), horizontal rules made of dashes, boxed/bordered sections, pipe-delimited tables, or any formatting that resembles a standalone document or report file.

#### Scenario: Design summary formatting (English)
- **WHEN** a design summary is produced AND locale is `en`
- **THEN** it SHALL use a markdown heading followed by a markdown bullet list. Each field SHALL be a separate bullet item formatted as `- **Label:** value`. All 9 fields SHALL be present (use `---` for missing values). Example:

```
## Design Summary

- **Building type:** Family house
- **Floor plan dimensions:** 10x15m
- **Location:** Veľké Lovce
- **Roof type:** Gable
- **Roof pitch:** 35 deg
- **Overhang:** 400mm
- **Attic usage:** Living space
- **Eaves shape:** Open
- **Wall construction:** Brick
```

#### Scenario: Design summary formatting (Slovak)
- **WHEN** a design summary is produced AND locale is `sk`
- **THEN** it SHALL use Slovak field labels and Slovak parameter values from the locale mapping table in SKILL.md. Example:

```
## Návrh strechy

- **Typ budovy:** Rodinný dom
- **Rozmery pôdorysu:** 10x15m
- **Umiestnenie:** Veľké Lovce
- **Typ strechy:** Štítová
- **Sklon strechy:** 35°
- **Previs:** 400mm
- **Využitie podkrovia:** Obytný priestor
- **Tvar rímsy:** Otvorené
- **Konštrukcia stien:** Tehla
```

### Requirement: Output must not narrate actions
The system SHALL NOT include any text that describes what actions were taken, tools that were called, or information that was looked up.

#### Scenario: Forbidden narration patterns
- **WHEN** composing the final response
- **THEN** the output SHALL NOT contain any of: "Let me...", "I'll...", "I will...", "Great!", "Excellent!", "Based on...", "After checking...", "The design has been...", "Let me verify...", "I see there's...", "Now generating...", "Now creating..."

### Requirement: Output must be exactly one of three forms
The system SHALL produce exactly one of: (1) a clean design summary with grouped labeled sections and optional price, (2) a concise question listing missing required parameters, or (3) a direct answer to the user's question.

#### Scenario: Design summary output
- **WHEN** a design was generated (with or without pricing)
- **THEN** output SHALL be a grouped labeled-section layout showing all 9 fields (with values or `---`), plus the price if available
- **AND** the output MAY be followed by a single helpful closing sentence such as "Let me know if you'd like to adjust anything" or "Happy to refine the roof pitch if needed"

#### Scenario: Missing parameter question output
- **WHEN** a design was triggered but desirable fields are missing
- **THEN** output SHALL be a single concise question listing only the missing desirable fields (building_type, floor_plan_dimensions, roof_type, roof_pitch)

#### Scenario: Direct answer output
- **WHEN** the intent was a knowledge query or general question
- **THEN** output SHALL be the direct answer with source citations, no preamble or postscript

### Requirement: Source citations for knowledge queries
When returning knowledge base results, the system SHALL cite the source document path for each piece of information.

#### Scenario: Citation format
- **WHEN** knowledge base content is included in the response
- **THEN** each source SHALL be cited as the relative file path from the knowledge base directory
