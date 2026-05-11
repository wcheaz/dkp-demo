## Purpose

Defines the capability for the agent to create design entries by calling a frontend tool, enabling simulated design generation with processing state and parameter-mapped output.

## MODIFIED Requirements

### Requirement: add_design_entry is registered as a CopilotKit frontend tool
**RENAMED TO:** `generate_design is registered as a CopilotKit frontend tool`

The `add_design_entry` frontend tool SHALL be removed entirely from `src/app/page.tsx`. A new frontend tool named `generate_design` SHALL be registered using `useFrontendTool` inside the `YourMainContent` component. The tool SHALL accept one parameter: `prompt_text` (string). The tool handler SHALL create a `DesignEntry` with `status: "processing"`, `imageUrl` selected from `ROOF_TYPE_IMAGE_MAP` based on `state.parameters.roofType` (fallback `"/design-gable.svg"`), and `promptText` set to `prompt_text`. The entry SHALL be appended to the existing `state.designs` array and `setState` called immediately. After a configurable delay (`DESIGN_GENERATION_DELAY_MS`, default 3000ms), the handler SHALL update the entry's `status` to `"complete"` and call `setState` again. All code for this tool SHALL be wrapped in `// DEMO-ONLY` comments.

#### Scenario: generate_design creates a processing entry
- **WHEN** the agent calls the frontend tool `generate_design` with `prompt_text: "hello"`
- **THEN** `setState` SHALL be called with a new state where `state.designs` contains a new `DesignEntry` with `status: "processing"` and `promptText: "hello"`

#### Scenario: generate_design resolves entry after delay
- **WHEN** the agent calls `generate_design` and the delay elapses
- **THEN** `setState` SHALL be called with the entry's `status` updated to `"complete"` and `imageUrl` updated to the roof-type-mapped SVG path

#### Scenario: add_design_entry tool no longer exists
- **WHEN** `src/app/page.tsx` is searched for the string `add_design_entry`
- **THEN** no `useFrontendTool` registration with `name: "add_design_entry"` SHALL be found

#### Scenario: DEMO-ONLY markers present in page.tsx
- **WHEN** `src/app/page.tsx` is searched for the string `DEMO-ONLY`
- **THEN** at least 1 occurrence SHALL be found near the `generate_design` frontend tool registration

### Requirement: System prompt mandates calling add_design_entry after every response
**RENAMED TO:** `System prompt instructs calling generate_design after parameter confirmation`

The agent's `system_prompt` in `agent/src/agent.py` SHALL replace the `add_design_entry` instruction with an instruction to call `generate_design` after the user has confirmed all required parameters. The instruction SHALL specify that `generate_design` is called only once per generation, after parameter confirmation, not after every response. The instruction SHALL be wrapped in a `# DEMO-ONLY` comment indicating the simulated nature. The system prompt SHALL preserve all existing instructions for `get_knowledge_summary`, `query_knowledge_base`, `update_design_parameters`, `modify_design_entry`, and `download_test_image`.

#### Scenario: System prompt references generate_design
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL contain the text `generate_design`
- **AND** the prompt SHALL NOT contain the text `add_design_entry`

#### Scenario: System prompt no longer mandates after-every-response
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL NOT contain `CRITICAL REQUIREMENT` or `EVERY SINGLE` or `non-negotiable` in connection with design entry creation

#### Scenario: System prompt preserves existing tool instructions
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL still contain references to `get_knowledge_summary`, `query_knowledge_base`, `update_design_parameters`, `modify_design_entry`, and `download_test_image`

#### Scenario: DEMO-ONLY marker present in agent code
- **WHEN** `agent/src/agent.py` is searched for the string `DEMO-ONLY`
- **THEN** at least 1 occurrence SHALL be found near the `generate_design` instruction in the system prompt

## REMOVED Requirements

### Requirement: Backend add_design_entry tool is commented out
**Reason:** The `add_design_entry` frontend tool and its backend counterpart are fully replaced by `generate_design`. The commented-out backend tool is no longer needed as a reference.
**Migration:** The `DesignEntry` model and `designs` field on `YourState` remain active. The commented-out `add_design_entry` function is removed from `agent/src/agent.py`.

### Requirement: All temporary code is marked with TEMPORARY comments
**Reason:** All `TEMPORARY` markers related to design entry creation are replaced by `DEMO-ONLY` markers on the new `generate_design` tool and supporting code.
**Migration:** `TEMPORARY` comments on `DesignEntry`, `designs` field, and the system prompt section are removed or replaced with `DEMO-ONLY` as appropriate.

## ADDED Requirements

### Requirement: Backend DesignEntry model includes status field
The `DesignEntry` Pydantic model in `agent/src/agent.py` SHALL include a `status` field of type `str` with default value `"complete"`. The `DesignEntry` class SHALL be marked with a `# DEMO-ONLY` comment.

#### Scenario: Backend DesignEntry model has status field
- **WHEN** `agent/src/agent.py` is inspected
- **THEN** `class DesignEntry(BaseModel)` SHALL include `status: str = "complete"` as a field

#### Scenario: Backend DEMO-ONLY marker present
- **WHEN** `agent/src/agent.py` is searched for `DEMO-ONLY` near `DesignEntry`
- **THEN** at least 1 occurrence SHALL be found near the `DesignEntry` class

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
