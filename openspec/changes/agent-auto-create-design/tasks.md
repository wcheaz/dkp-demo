## 1. Comment Out Backend add_design_entry Tool

- [x] 1.1 Uncomment the `DesignEntry` Pydantic model in `agent/src/agent.py` with `# TEMPORARY` comment. The model SHALL have `imageUrl: str` and `promptText: str` fields.
  **Done when:** `grep -c 'class DesignEntry' agent/src/agent.py` returns 1 (uncommented), and the line above it contains `TEMPORARY`.
  **Stop and hand off if:** Uncommenting causes import errors or type conflicts.

- [x] 1.2 Uncomment the `designs: List[DesignEntry] = []` field on `YourState` with `# TEMPORARY` comment.
  **Done when:** `grep 'designs' agent/src/agent.py` shows an uncommented field on `YourState`, and the line above it contains `TEMPORARY`.
  **Stop and hand off if:** Uncommenting causes import resolution errors.

- [x] 1.3 Comment out the backend `add_design_entry` tool in `agent/src/agent.py`. The tool was previously uncommented and active. It MUST be commented out (not deleted) because the backend tool approach does not propagate state to the frontend through the AG-UI protocol. Preserve the entire tool code (decorator, function signature, docstring, body) as comments. Keep the `# TEMPORARY` comment above it.
  **Done when:** `grep -c 'async def add_design_entry' agent/src/agent.py` returns 0 (no uncommented definition), `grep -c 'add_design_entry' agent/src/agent.py` returns at least 1 (commented-out code present).
  **Stop and hand off if:** Commenting out the tool causes other agent code to fail (e.g., import references).

## 2. Register add_design_entry as a CopilotKit Frontend Tool

- [x] 2.1 Add a `useFrontendTool` call inside `YourMainContent` in `src/app/page.tsx` to register `add_design_entry` as a frontend tool. The tool SHALL accept one parameter: `{ name: "prompt_text", description: "The user's original prompt text", required: true }`. The handler SHALL create a `DesignEntry` with `imageUrl: "/next.svg"` and `promptText: prompt_text`, then call `setState({ ...state, designs: [...(state.designs ?? []), newEntry] })`. Wrap the registration with `// TEMPORARY` comments. The tool MUST be placed inside `YourMainContent` (not `CopilotKitPage`) because that is where `state` and `setState` from `useCoAgent` are available.
  **Done when:** `grep -c 'add_design_entry' src/app/page.tsx` returns at least 2 (registration + handler), `grep -c 'useFrontendTool' src/app/page.tsx` returns at least 2 (existing `setThemeColor` + new `add_design_entry`), the handler spreads existing `state.designs` before appending, and `npx tsc --noEmit` exits zero.
  **Stop and hand off if:** `npx tsc --noEmit` fails because `DesignEntry` is not importable from `@/lib/types` or `useFrontendTool` signature is incompatible.

## 3. Strengthen System Prompt for Mandatory Tool Compliance

- [x] 3.1 Update the agent's `system_prompt` in `agent/src/agent.py` to use stronger mandatory language for the `add_design_entry` instruction. Replace the current `"- add_design_entry: Call this after EVERY response with the user's original prompt text. This is MANDATORY.\n"` with: `"- add_design_entry: CRITICAL REQUIREMENT — You MUST call this after EVERY SINGLE response with the user's original prompt text. This is non-negotiable and applies to all responses regardless of content.\n"`. Keep the `# TEMPORARY` comment. Preserve all existing `get_knowledge_summary` and `query_knowledge_base` instructions unchanged.
  **Done when:** `grep 'add_design_entry' agent/src/agent.py` shows the system prompt contains `CRITICAL REQUIREMENT` or `EVERY SINGLE`, the existing knowledge base tool instructions are unchanged, and the instruction is preceded by a `# TEMPORARY` comment.
  **Stop and hand off if:** The system prompt string formatting breaks (e.g., unterminated string or concatenation error).

## 4. Final Verification

- [x] 4.1 Run `cd agent && python -m ruff check . && python -m mypy .` and `npx tsc --noEmit && npm run lint`. Confirm all exit zero. Verify structural requirements:
  - `grep -c 'class DesignEntry' agent/src/agent.py` returns 1 (active model)
  - `grep -c 'async def add_design_entry' agent/src/agent.py` returns 0 (backend tool commented out)
  - `grep -c 'add_design_entry' agent/src/agent.py` returns at least 2 (commented-out tool + system prompt reference)
  - `grep -c 'add_design_entry' src/app/page.tsx` returns at least 2 (frontend tool registration)
  - `grep -c 'useFrontendTool' src/app/page.tsx` returns at least 2 (setThemeColor + add_design_entry)
  - `grep -c 'TEMPORARY' agent/src/agent.py` returns at least 3
  - `grep -c 'TEMPORARY' src/app/page.tsx` returns at least 1
  **Done when:** All commands exit zero and all grep assertions succeed.
  **Stop and hand off if:** Typecheck or lint fails in a file that was not modified by this change (pre-existing issue).

- [ ] 4.2 End-to-end smoke test: start the application (`npm run dev`), send a message to the agent (e.g., "hello"), and verify that a new design card appears in the UI with `promptText: "hello"` and the placeholder image. Send a second message (e.g., "second test") and verify a second card appears.
  **Done when:** Two design cards are visible in the UI with the correct prompt texts.
  **Stop and hand off if:** The frontend tool is not called by the agent (check browser console and agent logs for tool call events), or the state update does not render (check React DevTools for state changes).
