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
