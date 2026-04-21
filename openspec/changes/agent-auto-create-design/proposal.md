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
