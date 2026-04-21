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
