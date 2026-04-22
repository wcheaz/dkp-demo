## ADDED Requirements

### Requirement: add_design_entry is registered as a CopilotKit frontend tool
A frontend tool named `add_design_entry` SHALL be registered using `useFrontendTool` inside the `YourMainContent` component in `src/app/page.tsx`. The tool SHALL accept one parameter: `prompt_text` (string). The tool handler SHALL create a `DesignEntry` with `imageUrl: "/next.svg"` and `promptText: prompt_text`, append it to the existing `state.designs` array, and call `setState` with the updated state. The code SHALL be wrapped in `// TEMPORARY` comments indicating it is a testing tool.

#### Scenario: Frontend tool appends entry with user's prompt text
- **WHEN** the agent calls the frontend tool `add_design_entry` with `prompt_text: "hello"`
- **THEN** `setState` SHALL be called with a new state where `state.designs` contains a new `DesignEntry` with `imageUrl: "/next.svg"` and `promptText: "hello"`

#### Scenario: Frontend tool appends without losing existing designs
- **WHEN** the agent calls `add_design_entry` with `prompt_text: "second"` and `state.designs` already contains one entry
- **THEN** `setState` SHALL be called with `state.designs` containing two entries: the original entry followed by the new entry with `promptText: "second"`

#### Scenario: Frontend tool handles undefined designs array
- **WHEN** the agent calls `add_design_entry` and `state.designs` is undefined
- **THEN** the handler SHALL treat `state.designs` as an empty array and append the new entry, resulting in a single-entry array

#### Scenario: TEMPORARY markers present in page.tsx
- **WHEN** `src/app/page.tsx` is searched for the string `TEMPORARY`
- **THEN** at least 1 occurrence SHALL be found near the `add_design_entry` frontend tool registration

### Requirement: Backend add_design_entry tool is commented out
The backend `add_design_entry` tool in `agent/src/agent.py` SHALL be commented out (not deleted). The `DesignEntry` model and `designs` field on `YourState` SHALL remain active (uncommented). All three SHALL have `# TEMPORARY` comments.

#### Scenario: Backend tool is commented out
- **WHEN** `agent/src/agent.py` is inspected for `add_design_entry`
- **THEN** the `@agent.tool` decorator and `async def add_design_entry` function SHALL be present but commented out

#### Scenario: DesignEntry model and designs field remain active
- **WHEN** `agent/src/agent.py` is inspected
- **THEN** `class DesignEntry(BaseModel)` SHALL exist uncommented
- **AND** `designs: List[DesignEntry] = []` SHALL exist uncommented on `YourState`

### Requirement: System prompt mandates calling add_design_entry after every response
The agent's `system_prompt` in `agent/src/agent.py` SHALL include an instruction using strong mandatory language (`CRITICAL REQUIREMENT`, `EVERY SINGLE response`, `non-negotiable`) telling the agent to call `add_design_entry` with the user's original prompt text after every response. The instruction SHALL be wrapped in a `# TEMPORARY` comment. The system prompt SHALL preserve all existing instructions for `get_knowledge_summary` and `query_knowledge_base`.

#### Scenario: System prompt references add_design_entry with strong language
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL contain the text `add_design_entry`
- **AND** the prompt SHALL contain at least one of: `CRITICAL REQUIREMENT`, `EVERY SINGLE`, or `non-negotiable`
- **AND** the instruction SHALL be preceded by a `# TEMPORARY` comment

#### Scenario: System prompt preserves existing tool instructions
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL still contain references to `get_knowledge_summary` and `query_knowledge_base`
- **AND** the existing instructions about knowledge base usage SHALL remain unchanged

### Requirement: All temporary code is marked with TEMPORARY comments
Every code section added or modified by this change SHALL be preceded by a `TEMPORARY` comment explaining that it is a testing tool and will be replaced when real image generation is integrated.

#### Scenario: TEMPORARY markers present in agent code
- **WHEN** `agent/src/agent.py` is searched for the string `TEMPORARY`
- **THEN** at least 3 occurrences SHALL be found: before `DesignEntry`, before `designs` field, and before the system prompt addition

### Requirement: All code passes lint and type checking
The modified files SHALL pass all lint and type checking commands.

#### Scenario: Agent passes ruff check
- **WHEN** `cd agent && python -m ruff check .` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Agent passes mypy
- **WHEN** `cd agent && python -m mypy .` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Frontend passes TypeScript check
- **WHEN** `npx tsc --noEmit` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Frontend passes lint
- **WHEN** `npm run lint` is run
- **THEN** the command SHALL exit zero with no errors
