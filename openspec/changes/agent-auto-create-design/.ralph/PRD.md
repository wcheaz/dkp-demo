# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

## Why

The application has a `design-component` that renders design entries from shared agent state, and an `AddDesignButton` for manually creating test designs. Currently, the agent has commented-out code for an `add_design_entry` tool (disabled because the tool-to-frontend state propagation did not work). For testing purposes, we need the agent to automatically create a design entry after every prompt it receives — using the user's prompt text as the `promptText` field — so that the design display pipeline can be verified end-to-end without manual button clicks.

## What Changes

- Uncomment and modify the `DesignEntry` Pydantic model in `agent/src/agent.py` (currently commented out at lines ~71-75).
- Uncomment the `designs` field on `YourState` (currently commented out at line ~85).
- Uncomment and modify the `add_design_entry` tool (currently commented out at lines ~284-300): change the tool to use the user's actual prompt text as `promptText` instead of a generic test string.
- Update the agent's `system_prompt` to mandate that the agent calls `add_design_entry` after every response, passing the user's original prompt text.
- Wrap all uncommented code in `# TEMPORARY` comments marking it as a testing tool that will be replaced when real image generation is integrated.

## Capabilities

### New Capabilities

- `design-auto-creation`: Agent tool (`add_design_entry`) that appends a `DesignEntry` with `imageUrl: "/next.svg"` and the user's prompt text to `state.designs` after every agent response. The system prompt mandates calling this tool on every interaction. All code is wrapped in `# TEMPORARY` comments indicating it is a testing tool.

### Modified Capabilities

_(None — no existing specs are being modified.)_

## Impact

- **Files modified**: `agent/src/agent.py` — uncomment `DesignEntry` model, `designs` field on `YourState`, and `add_design_entry` tool; update `system_prompt` to mandate tool usage; add `# TEMPORARY` comment markers.
- **Dependencies added**: None — uses existing Pydantic and PydanticAI imports.
- **State shape**: `YourState` gains an active `designs: List[DesignEntry]` field. This is already expected by the frontend's `AgentState.designs` via CopilotKit shared state.
- **Behavioral change**: Every agent response will produce a new design card in the UI with the user's prompt text and a placeholder image (`/next.svg`).

## Non-Goals

- Real image generation — this is a testing tool that uses a placeholder image (`/next.svg`).
- Conditional or selective design creation — the tool MUST be called after every prompt for testing consistency.
- Removing or replacing the `AddDesignButton` component — it remains available for manual testing.
- Changing the frontend `DesignComponent` or `AgentState` type — they already support the required data shape.
- Persisting designs across sessions or page reloads.

## Testing Approach

- Send a message to the agent (e.g., "hello") and verify that a new `DesignEntry` appears in `state.designs` with `promptText: "hello"` and `imageUrl: "/next.svg"`.
- Send a second message and verify a second entry is appended.
- Run `cd agent && python -m ruff check . && python -m mypy .` to confirm no lint or type errors.

## Human Handoff

_(None — this change is fully implementable without manual intervention.)_

## Specifications

design-auto-creation/spec.md
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



## Design

## Context

The application uses CopilotKit to share state between a Next.js frontend and a PydanticAI agent. The frontend has a `DesignComponent` that renders `DesignEntry` objects from `state.designs`, and an `AddDesignButton` for manual testing. The agent (`agent/src/agent.py`) already contains commented-out code for a `DesignEntry` model, a `designs` field on `YourState`, and an `add_design_entry` tool. This code was disabled because the tool-to-frontend state propagation did not work in a prior attempt. The commented-out code is preserved at lines ~71-75 (model), ~85 (field), and ~284-300 (tool).

The current agent system prompt instructs the agent to use `get_knowledge_summary` and `query_knowledge_base` tools. It does not mention any design-related tool.

## Goals / Non-Goals

**Goals:**

- Uncomment and activate the `DesignEntry` model, `designs` field, and `add_design_entry` tool in `agent/src/agent.py`.
- Modify `add_design_entry` to use the user's actual prompt text (not a generic test string like `"Test design #N"`).
- Update the system prompt to mandate calling `add_design_entry` after every response.
- Mark all uncommented code with `# TEMPORARY` comments indicating it is a testing tool.

**Non-Goals:**

- Real image generation — `imageUrl` is hardcoded to `"/next.svg"`.
- Making design creation conditional or user-controllable — it must happen on every prompt.
- Changing the frontend `DesignComponent`, `AddDesignButton`, or `AgentState` type.
- Fixing the underlying CopilotKit state propagation issue (if it persists, that is a separate concern).

## Decisions

### D1: Uncomment existing code rather than writing new code

**Decision**: Uncomment the existing `DesignEntry`, `designs` field, and `add_design_entry` tool rather than creating new implementations.

**Rationale**: The commented-out code is already well-structured and close to what is needed. The only modification required is changing `promptText` from a computed test string to the user's actual prompt text. Uncommenting preserves the original intent and avoids duplicating logic.

**Alternative considered**: Rewrite the tool from scratch. Rejected because the existing code is already correct in structure — only the `promptText` value needs to change.

### D2: Use the user's prompt text as `promptText`

**Decision**: The `add_design_entry` tool accepts a `prompt_text: str` parameter and uses it directly as the `promptText` field on the `DesignEntry`. The system prompt instructs the agent to pass the user's original prompt text.

**Rationale**: This is the user's explicit requirement — if the user says "hello", the design entry should have `promptText: "hello"`. The original commented-out code used a generic test string (`"Test design #N"`), which is replaced by the actual prompt.

**Alternative considered**: Auto-generate a design name from the prompt (e.g., first 50 chars). Rejected because the requirement is to use the prompt text verbatim.

### D3: Hardcode `imageUrl` to `"/next.svg"`

**Decision**: Keep `imageUrl` hardcoded to `"/next.svg"` in the tool, matching the pattern used by `AddDesignButton` (which uses `"/next.svg"`).

**Rationale**: This is a testing tool. Real image generation will replace this in a future change. The value `"/next.svg"` is the existing test image in the repository.

### D4: System prompt mandates tool usage on every response

**Decision**: Add an instruction to the system prompt that says: "After every response, you MUST call the `add_design_entry` tool with the user's original prompt text."

**Rationale**: The requirement is for the agent to create a design after every prompt. A mandatory instruction in the system prompt is the most reliable way to ensure this behavior in a PydanticAI agent. The tool's docstring also reinforces when to call it.

**Alternative considered**: Use a `@agent.result_validator` to auto-inject the call. Rejected because result validators are for post-processing output, not for triggering tool calls. The agent must explicitly call the tool.

### D5: `# TEMPORARY` comment markers

**Decision**: All uncommented code sections (`DesignEntry` model, `designs` field, `add_design_entry` tool, and the system prompt addition) SHALL be wrapped with `# TEMPORARY` comments indicating this is a testing tool that will be replaced when real image generation is integrated.

**Rationale**: The user explicitly requested comments as a reminder that this is a testing tool. This ensures future developers know to replace or remove this code.

## Risks / Trade-offs

- **[State propagation may still not work]** → The original code was commented out because "the agent tool approach did not work for automatic state propagation." Uncommenting it may reproduce the same issue. Mitigation: this is explicitly a testing exercise; if propagation still fails, the issue should be investigated as a separate change.
- **[System prompt instruction may be ignored]** → LLMs do not always follow system prompt instructions perfectly. The agent may occasionally skip the tool call. Mitigation: the tool's docstring reinforces the requirement; the system prompt uses "MUST" language.
- **[No conditional logic]** → The tool is called on every prompt regardless of context. Mitigation: this is intentional for testing purposes.

## Current Task Context

## Current Task
- 1.1 Uncomment the `DesignEntry` Pydantic model in `agent/src/agent.py` (currently commented out at lines ~71-75). Add a `# TEMPORARY` comment above it: `# TEMPORARY - DesignEntry model for design component; will be replaced when real image generation is integrated`. The model SHALL have `imageUrl: str` and `promptText: str` fields.
