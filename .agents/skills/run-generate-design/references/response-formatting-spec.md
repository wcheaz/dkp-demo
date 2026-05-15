## ADDED Requirements

### Requirement: Output must not contain emojis
The system SHALL NOT include emoji or pictograph characters in any output.

#### Scenario: No emojis in output
- **WHEN** the final response is composed
- **THEN** it SHALL NOT contain any emoji or pictograph characters

### Requirement: Output must use chat-friendly formatting
The system SHALL format responses as standard markdown chat messages — using markdown headings (`##`), pipe-delimited tables, and bullet lists. The system SHALL NOT use reStructuredText-style underlines (`===`, `---`), horizontal rules made of dashes, boxed/bordered sections, or any formatting that resembles a standalone document or report file.

#### Scenario: Design summary formatting
- **WHEN** a design summary is produced
- **THEN** it SHALL use a markdown heading, a pipe-delimited parameter table, and optional bullet-point notes — NOT underlines, dash borders, or document-style sections

### Requirement: Output must not narrate actions
The system SHALL NOT include any text that describes what actions were taken, tools that were called, or information that was looked up.

#### Scenario: Forbidden narration patterns
- **WHEN** composing the final response
- **THEN** the output SHALL NOT contain any of: "Let me...", "I'll...", "I will...", "Great!", "Excellent!", "Based on...", "After checking...", "The design has been...", "Let me verify...", "I see there's...", "Now generating...", "Now creating..."

### Requirement: Output must be exactly one of three forms
The system SHALL produce exactly one of: (1) a clean design summary with parameters table and optional price, (2) a concise question listing missing required parameters, or (3) a direct answer to the user's question.

#### Scenario: Design summary output
- **WHEN** a design was generated (with or without pricing)
- **THEN** output SHALL be a parameters table showing all 9 fields (with values or `---`), plus the price if available

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
