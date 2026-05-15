## ADDED Requirements

### Requirement: Agent instantiated with DeepSeekModel and StateDeps
The system SHALL create an `Agent` instance with the `model` (DeepSeekModel), `deps_type=StateDeps`, and a comprehensive `system_prompt` string.

#### Scenario: Agent accepts correct deps type
- **WHEN** the agent is used with `StateDeps(state=YourState())`
- **THEN** tools SHALL receive `RunContext[StateDeps]` with access to state

### Requirement: System prompt enforces ASCII-only output
The system prompt SHALL instruct the agent to NEVER use emojis, Unicode symbols, or pictographs. All output MUST be plain ASCII.

#### Scenario: Emoji prohibition in prompt
- **WHEN** the system prompt is read
- **THEN** it SHALL contain the phrase "NEVER include emojis" and list forbidden example emojis

### Requirement: System prompt enforces silent tool calls
The system prompt SHALL instruct the agent to call ALL tools silently with zero text output, and only output the final result after all tool calls complete.

#### Scenario: Narration prohibition
- **WHEN** the system prompt is read
- **THEN** it SHALL list forbidden patterns including "Let me...", "I'll...", "Great!", "Based on..."

### Requirement: System prompt defines tool usage rules
The system prompt SHALL contain detailed instructions for each tool: `get_knowledge_summary`, `query_knowledge_base`, `generate_design`, `modify_design_entry`, `update_design_parameters`, `generate_quote`, and `reset_design`.

#### Scenario: Tool rules present
- **WHEN** the system prompt is read
- **THEN** it SHALL contain sections for each of the 7 tools with usage conditions and parameter descriptions

### Requirement: System prompt defines parameter collection loop
The system prompt SHALL instruct the agent to extract parameter values from every user message and immediately call `update_design_parameters` with partial data when a design is requested.

#### Scenario: Collection loop instructions
- **WHEN** the system prompt is read
- **THEN** it SHALL contain a numbered "COLLECTION LOOP INSTRUCTIONS" section with at least 5 steps

### Requirement: System prompt defines output style rules
The system prompt SHALL restrict agent text output to exactly three forms: (1) clean design summary, (2) concise question for missing parameters, or (3) direct answer.

#### Scenario: Output style rules present
- **WHEN** the system prompt is read
- **THEN** it SHALL contain an "OUTPUT STYLE" section enumerating the three allowed output forms
