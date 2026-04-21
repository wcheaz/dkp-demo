## ADDED Requirements

### Requirement: DesignEntry Pydantic model is active
The `DesignEntry` Pydantic model SHALL be defined (uncommented) in `agent/src/agent.py` with fields `imageUrl: str` and `promptText: str`. The model SHALL be wrapped in `# TEMPORARY` comments indicating it is a testing model that will be replaced when real image generation is integrated.

#### Scenario: DesignEntry model compiles and is importable
- **WHEN** `agent/src/agent.py` is inspected
- **THEN** a `class DesignEntry(BaseModel)` SHALL exist (not commented out) with `imageUrl: str` and `promptText: str` fields
- **AND** the model SHALL be preceded by a `# TEMPORARY` comment

#### Scenario: DesignEntry passes type checking
- **WHEN** `cd agent && python -m mypy .` is run
- **THEN** the command SHALL exit zero with no errors related to `DesignEntry`

### Requirement: YourState has an active designs field
The `YourState` class in `agent/src/agent.py` SHALL have an active (uncommented) `designs: List[DesignEntry] = []` field. The field SHALL be wrapped in a `# TEMPORARY` comment indicating it is for testing purposes.

#### Scenario: designs field exists on YourState
- **WHEN** `agent/src/agent.py` is inspected for the `YourState` class
- **THEN** the class SHALL contain an active `designs: List[DesignEntry] = []` field (not commented out)
- **AND** the field SHALL be preceded by a `# TEMPORARY` comment

#### Scenario: YourState instantiates with empty designs
- **WHEN** `YourState()` is instantiated
- **THEN** `state.designs` SHALL equal an empty list `[]`

### Requirement: add_design_entry tool is active and uses user prompt text
An `add_design_entry` tool SHALL be registered on the agent (uncommented, decorated with `@agent.tool`) in `agent/src/agent.py`. The tool SHALL accept `prompt_text: str` as a parameter. The tool SHALL create a `DesignEntry` with `imageUrl="/next.svg"` and `promptText=prompt_text`, append it to `ctx.deps.state.designs`, and return a confirmation string. The tool SHALL be wrapped in `# TEMPORARY` comments indicating it is a testing tool.

#### Scenario: Tool appends entry with user's prompt text
- **WHEN** the agent calls `add_design_entry` with `prompt_text="hello"`
- **THEN** a `DesignEntry` with `imageUrl="/next.svg"` and `promptText="hello"` SHALL be appended to `ctx.deps.state.designs`
- **AND** the tool SHALL return a confirmation string containing "hello"

#### Scenario: Tool appends entry with a longer prompt
- **WHEN** the agent calls `add_design_entry` with `prompt_text="Draw a flowchart of user login"`
- **THEN** a `DesignEntry` with `imageUrl="/next.svg"` and `promptText="Draw a flowchart of user login"` SHALL be appended to `ctx.deps.state.designs`

#### Scenario: Multiple calls append multiple entries
- **WHEN** the agent calls `add_design_entry` twice with `prompt_text="first"` then `prompt_text="second"`
- **THEN** `ctx.deps.state.designs` SHALL contain two entries in order: first with `promptText="first"`, second with `promptText="second"`

### Requirement: System prompt mandates calling add_design_entry after every response
The agent's `system_prompt` in `agent/src/agent.py` SHALL include an instruction that the agent MUST call `add_design_entry` with the user's original prompt text after every response. The instruction SHALL be wrapped in `# TEMPORARY` comments. The system prompt SHALL list `add_design_entry` as an available tool alongside the existing `get_knowledge_summary` and `query_knowledge_base` tools.

#### Scenario: System prompt references add_design_entry
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL contain the text `add_design_entry`
- **AND** the prompt SHALL instruct the agent to call it after every response
- **AND** the instruction SHALL be preceded by a `# TEMPORARY` comment

#### Scenario: System prompt preserves existing tool instructions
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL still contain references to `get_knowledge_summary` and `query_knowledge_base`
- **AND** the existing instructions about knowledge base usage SHALL remain unchanged

### Requirement: All temporary code is marked with TEMPORARY comments
Every code section activated by this change (`DesignEntry` model, `designs` field, `add_design_entry` tool, and system prompt addition) SHALL be preceded by a `# TEMPORARY` comment explaining that it is a testing tool and will be replaced when real image generation is integrated.

#### Scenario: TEMPORARY markers present
- **WHEN** `agent/src/agent.py` is searched for the string `TEMPORARY`
- **THEN** at least 4 occurrences SHALL be found: one before `DesignEntry`, one before `designs` field, one before `add_design_entry` tool, and one before the system prompt addition

### Requirement: Agent code passes lint and type checking
The modified `agent/src/agent.py` SHALL pass both `ruff check` and `mypy` without errors.

#### Scenario: Ruff check passes
- **WHEN** `cd agent && python -m ruff check .` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Mypy passes
- **WHEN** `cd agent && python -m mypy .` is run
- **THEN** the command SHALL exit zero with no errors
