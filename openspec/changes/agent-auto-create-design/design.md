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
