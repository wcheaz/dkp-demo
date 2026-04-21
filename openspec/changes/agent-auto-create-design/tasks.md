## 1. Activate DesignEntry Model and designs Field

- [x] 1.1 Uncomment the `DesignEntry` Pydantic model in `agent/src/agent.py` (currently commented out at lines ~71-75). Add a `# TEMPORARY` comment above it: `# TEMPORARY - DesignEntry model for design component; will be replaced when real image generation is integrated`. The model SHALL have `imageUrl: str` and `promptText: str` fields.
  **Done when:** `grep -c 'class DesignEntry' agent/src/agent.py` returns 1 (uncommented), and the line above it contains `TEMPORARY`.
  **Stop and hand off if:** Uncommenting causes import errors or type conflicts with existing code.

- [x] 1.2 Uncomment the `designs: List[DesignEntry] = []` field on `YourState` in `agent/src/agent.py` (currently commented out at line ~85). Add a `# TEMPORARY` comment above it: `# TEMPORARY - designs field for design component; will be replaced when real image generation is integrated`.
  **Done when:** `grep 'designs' agent/src/agent.py` shows an uncommented `designs: List[DesignEntry] = []` field on `YourState`, and the line above it contains `TEMPORARY`.
  **Stop and hand off if:** Uncommenting causes `List` or `DesignEntry` import resolution errors.

## 2. Activate and Modify add_design_entry Tool

- [x] 2.1 Uncomment the `add_design_entry` tool in `agent/src/agent.py` (currently commented out at lines ~284-300). Modify the tool so that `DesignEntry` is constructed with `imageUrl="/next.svg"` and `promptText=prompt_text` (using the tool's `prompt_text` parameter, not a generic test string). Add a `# TEMPORARY` comment above the tool: `# TEMPORARY - add_design_entry tool for design component; will be replaced when real image generation is integrated`. The tool docstring SHALL state: `Add a design entry to the shared state. Call this after every response with the user's original prompt text.`
  **Done when:** `grep -c 'async def add_design_entry' agent/src/agent.py` returns 1 (uncommented), the tool body uses `prompt_text` (not a hardcoded test string), and `grep -c 'TEMPORARY' agent/src/agent.py` shows at least 3 occurrences (model + field + tool).
  **Stop and hand off if:** Uncommenting causes decorator or type errors with the `@agent.tool` decorator.

## 3. Update System Prompt

- [x] 3.1 Update the agent's `system_prompt` in `agent/src/agent.py` to include `add_design_entry` as an available tool and mandate its usage after every response. Add a `# TEMPORARY` comment inline before the addition. The prompt addition SHALL read: `"- add_design_entry: Call this after EVERY response with the user's original prompt text. This is MANDATORY.\n"`. Insert this into the existing tool list (after the `query_knowledge_base` description, before the "Always use" instruction).
  **Done when:** `grep -c 'add_design_entry' agent/src/agent.py` returns at least 3 (tool definition + docstring + system prompt reference), the system prompt contains `MANDATORY` or `MUST` language about calling the tool, and the existing `get_knowledge_summary` and `query_knowledge_base` instructions are unchanged.
  **Stop and hand off if:** The system prompt string formatting breaks (e.g., unterminated string or concatenation error).

## 4. Verification

- [x] 4.1 Run `cd agent && python -m ruff check . && python -m mypy .` and confirm both exit zero. Verify structural requirements: `grep -c 'class DesignEntry' agent/src/agent.py` returns 1, `grep -c 'async def add_design_entry' agent/src/agent.py` returns 1, `grep -c 'TEMPORARY' agent/src/agent.py` returns at least 4, and `grep 'add_design_entry' agent/src/agent.py` shows the tool in both the definition and the system prompt.
  **Done when:** All commands exit zero and all grep assertions succeed.
  **Stop and hand off if:** Typecheck or lint fails in a file that was not modified by this change (pre-existing issue).
