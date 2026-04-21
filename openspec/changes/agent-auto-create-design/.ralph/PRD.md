# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

## Why

The application has a `design-component` that renders design entries from shared agent state, and an `AddDesignButton` for manually creating test designs. For testing purposes, we need the agent to automatically create a design entry after every prompt it receives — using the user's prompt text as the `promptText` field — so that the design display pipeline can be verified end-to-end without manual button clicks.

A prior attempt used a backend `@agent.tool` in PydanticAI that mutated `ctx.deps.state.designs`, but the AG-UI state protocol did not propagate those mutations back to the frontend. The backend tool approach was commented out with the note: *"Commented out because the agent tool approach did not work for automatic state propagation."* This change solves both the state propagation problem and the tool-call compliance problem.

## What Changes

- Keep the `DesignEntry` Pydantic model and `designs` field on `YourState` in `agent/src/agent.py` as active (TEMPORARY) code — they may be useful for future agent-side state tracking.
- Comment out the backend `add_design_entry` tool in `agent/src/agent.py` since it does not propagate state to the frontend.
- Register `add_design_entry` as a CopilotKit **frontend tool** (`useFrontendTool`) in `src/app/page.tsx` inside `YourMainContent`. This tool directly calls `setState` to append a `DesignEntry`, bypassing AG-UI state sync entirely. This is the same pattern already working for `setThemeColor`.
- Update the agent's `system_prompt` to instruct the agent to call `add_design_entry` with the user's prompt text after every response. Use stronger language (`CRITICAL REQUIREMENT`, `every single response`) to improve LLM compliance.
- Wrap all temporary code in `# TEMPORARY` comments.

## Capabilities

### New Capabilities

- `design-auto-creation`: A CopilotKit frontend tool (`add_design_entry`, registered via `useFrontendTool`) that the agent calls after every response. The tool accepts `prompt_text` and directly appends a `DesignEntry` with `imageUrl: "/next.svg"` and the user's prompt text to `state.designs` via `setState`. The system prompt mandates calling this tool on every interaction.

### Modified Capabilities

_(None — no existing specs are being modified.)_

## Impact

- **Files modified**: 
  - `agent/src/agent.py` — keep `DesignEntry` model and `designs` field active; comment out the backend `add_design_entry` tool; update `system_prompt` to reference the frontend tool with stronger mandatory language.
  - `src/app/page.tsx` — add `useFrontendTool` for `add_design_entry` inside `YourMainContent`, with access to `state` and `setState`.
- **Dependencies added**: None — uses existing CopilotKit hooks.
- **Behavioral change**: Every agent response will produce a new design card in the UI with the user's prompt text and a placeholder image (`/next.svg`).

## Non-Goals

- Real image generation — this is a testing tool that uses a placeholder image (`/next.svg`).
- Conditional or selective design creation — the tool MUST be called after every prompt for testing consistency.
- Removing or replacing the `AddDesignButton` component — it remains available for manual testing.
- Changing the frontend `DesignComponent` or `AgentState` type — they already support the required data shape.
- Fixing the underlying AG-UI state propagation mechanism — that is a separate concern.
- Persisting designs across sessions or page reloads.

## Testing Approach

- Send a message to the agent (e.g., "hello") and verify that a new `DesignEntry` appears in the design list with `promptText: "hello"` and the placeholder image.
- Send a second message and verify a second entry is appended.
- Run `cd agent && python -m ruff check . && python -m mypy .` to confirm no lint or type errors.
- Run `npx tsc --noEmit` to confirm no TypeScript errors.

## Human Handoff

_(None — this change is fully implementable without manual intervention.)_

## Specifications

design-auto-creation/spec.md
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



## Design

## Context

The application uses CopilotKit to share state between a Next.js frontend and a PydanticAI agent connected via the AG-UI protocol. The frontend has a `DesignComponent` that renders `DesignEntry` objects from `state.designs`, and an `AddDesignButton` for manual testing.

A prior implementation used a backend `@agent.tool` (`add_design_entry`) that mutated `ctx.deps.state.designs` via `.append()`. The tool was called successfully by the agent, but the state change did not propagate to the frontend through the AG-UI protocol. The code was commented out with the note: *"Commented out because the agent tool approach did not work for automatic state propagation."*

The application already uses CopilotKit frontend tools successfully — `setThemeColor` in `CopilotKitPage` uses `useFrontendTool` to directly update React state from agent tool calls. This pattern works because the frontend tool handler has direct access to `setState`, bypassing AG-UI state sync entirely.

## Goals / Non-Goals

**Goals:**

- Register `add_design_entry` as a CopilotKit frontend tool (`useFrontendTool`) in `YourMainContent` so it can directly update `state.designs` via `setState`.
- Comment out the backend `add_design_entry` tool in `agent/src/agent.py` since it does not propagate state.
- Keep `DesignEntry` model and `designs` field on `YourState` active (they may be useful for future agent-side state tracking).
- Update the system prompt with stronger mandatory language to improve LLM compliance with calling the tool after every response.
- Mark all temporary code with `# TEMPORARY` comments.

**Non-Goals:**

- Real image generation — `imageUrl` is hardcoded to `"/next.svg"`.
- Making design creation conditional or user-controllable — it must happen on every prompt.
- Changing the `DesignComponent` or `AgentState` type.
- Investigating or fixing the underlying AG-UI state propagation mechanism.
- Persisting designs across sessions.

## Decisions

### D1: Use frontend tool instead of backend tool for state propagation

**Decision**: Register `add_design_entry` as a CopilotKit frontend tool via `useFrontendTool` in `YourMainContent` (inside `src/app/page.tsx`), not as a PydanticAI backend tool. Comment out the backend tool.

**Rationale**: The backend `@agent.tool` approach was already proven to not propagate state changes to the frontend through the AG-UI protocol. The `useFrontendTool` pattern already works in this application — `setThemeColor` uses it successfully. The frontend tool handler has direct access to `setState`, so there is zero reliance on AG-UI state sync. The agent calls the tool by name; CopilotKit routes the call to the frontend handler.

**Alternative considered**: Fix the AG-UI state propagation. Rejected because that is a protocol-level issue outside the scope of this testing tool. Alternative considered: Use `useCopilotAction` instead of `useFrontendTool`. `useFrontendTool` is preferred because it is the pattern already working for `setThemeColor` in this codebase.

### D2: Place useFrontendTool in YourMainContent

**Decision**: Register the `add_design_entry` frontend tool inside the `YourMainContent` component (not `CopilotKitPage`) because `YourMainContent` is where `useCoAgent` provides `state` and `setState`.

**Rationale**: The tool handler needs access to `state` and `setState` to append a `DesignEntry`. These are only available inside `YourMainContent` where `useCoAgent` is called. The existing `setThemeColor` tool is in `CopilotKitPage` because it only needs `setThemeColor` state, which is available at that level.

**Alternative considered**: Lift `state`/`setState` to `CopilotKitPage`. Rejected because `useCoAgent` is already correctly placed in `YourMainContent` and lifting it would require unnecessary refactoring.

### D3: Comment out backend tool, keep model and state field

**Decision**: Comment out the backend `add_design_entry` tool in `agent/src/agent.py`. Keep `DesignEntry` model and `designs` field on `YourState` active (uncommented) with `# TEMPORARY` markers.

**Rationale**: The model and state field may be useful for future agent-side state tracking when real image generation is integrated. The backend tool, however, serves no purpose without state propagation and should be commented out to avoid confusion.

### D4: Stronger system prompt language

**Decision**: Rewrite the system prompt's `add_design_entry` instruction to use stronger mandatory language: `CRITICAL REQUIREMENT: You MUST call add_design_entry after EVERY SINGLE response with the user's original prompt text. This is non-negotiable and applies to all responses regardless of content.`

**Rationale**: The prior system prompt used `MANDATORY` but the agent still skipped the tool on some prompts. Stronger language with emphasis (`CRITICAL REQUIREMENT`, `EVERY SINGLE`, `non-negotiable`) improves LLM compliance. The instruction is placed prominently in the system prompt.

**Alternative considered**: Use a `result_validator` to enforce the tool call. Rejected because result validators cannot trigger additional tool calls — they can only validate or reject the final output. Alternative considered: Add a second reminder at the end of the system prompt. This is a good complementary approach and may be added if the primary instruction proves insufficient.

### D5: TEMPORARY comment markers

**Decision**: All code sections added or modified by this change (frontend tool registration, system prompt changes, and any remaining active agent code) SHALL be wrapped with `# TEMPORARY` comments (Python) or `// TEMPORARY` comments (TypeScript) indicating they are testing tools.

**Rationale**: The user explicitly requested comments as a reminder that this is a testing tool. This ensures future developers know to replace or remove this code.

## Risks / Trade-offs

- **[LLM may still occasionally skip the tool]** → Even with stronger prompt language, LLMs do not guarantee 100% compliance. Mitigation: the prompt uses very strong language; if the agent still skips, the user can retry or add a second reminder at the end of the system prompt.
- **[Frontend tool depends on CopilotKit hooks]** → The tool only works when the React component is mounted. Mitigation: the component is always mounted in the current application layout.
- **[No backend state tracking]** → Commenting out the backend tool means the agent doesn't track designs in its own state. Mitigation: the frontend state is the source of truth; the agent receives it at the start of each run via AG-UI protocol.

## Current Task Context

## Current Task
- 1.3 Comment out the backend `add_design_entry` tool in `agent/src/agent.py`. The tool was previously uncommented and active. It MUST be commented out (not deleted) because the backend tool approach does not propagate state to the frontend through the AG-UI protocol. Preserve the entire tool code (decorator, function signature, docstring, body) as comments. Keep the `# TEMPORARY` comment above it.
## Completed Tasks for Git Commit
- [x] 1.1 Uncomment the `DesignEntry` Pydantic model in `agent/src/agent.py` with `# TEMPORARY` comment. The model SHALL have `imageUrl: str` and `promptText: str` fields.
- [x] 1.2 Uncomment the `designs: List[DesignEntry] = []` field on `YourState` with `# TEMPORARY` comment.
