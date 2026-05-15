## 1. Dependency and Imports

- [x] 1.1 Add `pydantic-ai-skills>=0.10.0` to the `dependencies` list in `agent/pyproject.toml`, then run `cd agent && uv sync` to install. Verify the command exits with code 0 and `pydantic_ai_skills` is importable.
- [x] 1.2 Add `from pydantic_ai_skills import SkillsCapability` import at the top of `agent/src/agent.py`. Add `SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / ".agents" / "skills"` constant. Verify the import resolves without error by running `python -c "from pydantic_ai_skills import SkillsCapability"`.

## 2. Agent Constructor Refactor

- [x] 2.1 Replace the existing `Agent(...)` call in `agent/src/agent.py` to add `capabilities=[SkillsCapability(directories=[str(SKILLS_DIR)], exclude_tools=["run_skill_script", "list_skills"], validate=True, auto_reload=True)]`. Remove the old `system_prompt=` keyword argument temporarily (it will be restored in the next task). Verify the agent initializes without errors.
- [x] 2.2 Rewrite the `system_prompt` string to the slim version containing only: agent identity, ABSOLUTE RULES (emoji prohibition, narration prohibition, forbidden phrases), the 7-tool catalog with one-line descriptions, and the skill hint instructing `load_skill("run-generate-design")` for the full workflow. Re-attach it as the `system_prompt=` parameter. Done when: the system prompt is under 25 lines, contains no intent classification rules, no parameter extraction table, no tool action simulation, and no response formatting rules.

## 3. Verification

- [x] 3.1 Run any existing test suite (`pytest` or equivalent) and confirm all tests pass. If no tests exist, start the agent and send a knowledge-base query (e.g., "What projects do you have?") confirming it responds correctly without loading the skill. Done when: agent responds with knowledge summary content.
- [x] 3.2 Send a design-related message to the agent (e.g., "I need a truss for a 10m span roof") and confirm the agent calls `load_skill("run-generate-design")`, follows the decision-loop workflow, and produces a structured design response. Done when: the response contains the expected design output format and the agent loaded the skill during the conversation.

## 4. Fix — ModuleNotFoundError for pydantic_ai_skills

The agent process runs from `/home/ncheaz/git/dkp-demo/agent/` (main worktree) using its own `.venv`, but loads source code from `/home/ncheaz/git/dkp-demo-with-specs/dkp-demo/agent/src/agent.py`. The `pydantic-ai-skills` package was installed only in the specs worktree venv, not in the main worktree venv where the process executes. Both `pyproject.toml` and `agent.py` must also be synced to the main worktree.

- [ ] 4.1 Install `pydantic-ai-skills` in the main worktree venv and sync source code

  The main worktree at `/home/ncheaz/git/dkp-demo/` has its own `.venv` that does not contain `pydantic-ai-skills`. The source code at `/home/ncheaz/git/dkp-demo/agent/src/agent.py` also lacks the `SkillsCapability` import and constructor changes. Both must be fixed.

  **Part A — Install dependency**: Run `cd /home/ncheaz/git/dkp-demo/agent && uv sync` to install `pydantic-ai-skills>=0.10.0` (already listed in `pyproject.toml` but not installed in this venv). If `pyproject.toml` in the main worktree does not contain `pydantic-ai-skills`, add it to the dependencies list first, then run `uv sync`.

  **Part B — Sync source code**: Copy `agent/src/agent.py` from the specs worktree to the main worktree: `cp /home/ncheaz/git/dkp-demo-with-specs/dkp-demo/agent/src/agent.py /home/ncheaz/git/dkp-demo/agent/src/agent.py`. Also copy `agent/pyproject.toml` if the dependency is missing: `cp /home/ncheaz/git/dkp-demo-with-specs/dkp-demo/agent/pyproject.toml /home/ncheaz/git/dkp-demo/agent/pyproject.toml`. If other files were modified by this change (e.g., `agent/src/main.py`), sync those too.

  **Done when:**
  - `/home/ncheaz/git/dkp-demo/agent/.venv/bin/python -c "from pydantic_ai_skills import SkillsCapability"` exits with code 0
  - `diff /home/ncheaz/git/dkp-demo-with-specs/dkp-demo/agent/src/agent.py /home/ncheaz/git/dkp-demo/agent/src/agent.py` shows no differences
  - `diff /home/ncheaz/git/dkp-demo-with-specs/dkp-demo/agent/pyproject.toml /home/ncheaz/git/dkp-demo/agent/pyproject.toml` shows no differences
  - `/home/ncheaz/git/dkp-demo/agent/.venv/bin/python -c "import ast; ast.parse(open('/home/ncheaz/git/dkp-demo/agent/src/agent.py').read())"` exits with code 0 (valid Python syntax)

  **Stop and hand off if:** `uv sync` fails with a dependency conflict between `pydantic-ai-skills>=0.10.0` and the existing `pydantic-ai` version — document the exact error message and version numbers.

- [ ] 4.2 Start the agent and verify it initializes without ModuleNotFoundError

  Start the agent process from `/home/ncheaz/git/dkp-demo/`. The agent MUST start without any `ModuleNotFoundError` or import errors. The uvicorn process MUST reach the "Application startup complete" log line. If the agent has a health endpoint or responds to WebSocket connections, confirm it accepts connections.

  **Done when:**
  - The agent process starts and logs no `ModuleNotFoundError` or `ImportError`
  - The uvicorn log shows "Application startup complete" (or equivalent startup message)
  - The agent is reachable (WebSocket connection accepted, or health endpoint returns 200)
  - No traceback appears in the agent process output

  **Stop and hand off if:** The agent starts but throws a runtime error from `SkillsCapability` (e.g., the skill directory path does not resolve correctly from the main worktree, or `validate=True` fails because `.agents/skills/run-generate-design/SKILL.md` does not exist in the main worktree). Document the exact error and the resolved `SKILLS_DIR` path.
