## 1. Dependency and Imports

- [x] 1.1 Add `pydantic-ai-skills>=0.10.0` to the `dependencies` list in `agent/pyproject.toml`, then run `cd agent && uv sync` to install. Verify the command exits with code 0 and `pydantic_ai_skills` is importable.
- [x] 1.2 Add `from pydantic_ai_skills import SkillsCapability` import at the top of `agent/src/agent.py`. Add `SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / ".agents" / "skills"` constant. Verify the import resolves without error by running `python -c "from pydantic_ai_skills import SkillsCapability"`.

## 2. Agent Constructor Refactor

- [x] 2.1 Replace the existing `Agent(...)` call in `agent/src/agent.py` to add `capabilities=[SkillsCapability(directories=[str(SKILLS_DIR)], exclude_tools=["run_skill_script", "list_skills"], validate=True, auto_reload=True)]`. Remove the old `system_prompt=` keyword argument temporarily (it will be restored in the next task). Verify the agent initializes without errors.
- [x] 2.2 Rewrite the `system_prompt` string to the slim version containing only: agent identity, ABSOLUTE RULES (emoji prohibition, narration prohibition, forbidden phrases), the 7-tool catalog with one-line descriptions, and the skill hint instructing `load_skill("run-generate-design")` for the full workflow. Re-attach it as the `system_prompt=` parameter. Done when: the system prompt is under 25 lines, contains no intent classification rules, no parameter extraction table, no tool action simulation, and no response formatting rules.

## 3. Verification

- [x] 3.1 Run any existing test suite (`pytest` or equivalent) and confirm all tests pass. If no tests exist, start the agent and send a knowledge-base query (e.g., "What projects do you have?") confirming it responds correctly without loading the skill. Done when: agent responds with knowledge summary content.
- [x] 3.2 Send a design-related message to the agent (e.g., "I need a truss for a 10m span roof") and confirm the agent calls `load_skill("run-generate-design")`, follows the decision-loop workflow, and produces a structured design response. Done when: the response contains the expected design output format and the agent loaded the skill during the conversation.

## 4. Fix — Verify in-worktree dependency install and import

The original `ModuleNotFoundError` occurred because the agent process loaded source from this worktree but used a venv from `/home/ncheaz/git/dkp-demo/`. Additionally, `pydantic-ai-skills` pulled in `pydantic-ai-slim==1.96.1` which does not include the `ag-ui-protocol` package needed by `agent.to_ag_ui()` in `main.py`. Both `pydantic-ai-skills` and `ag-ui-protocol` must be declared in `pyproject.toml`.

- [ ] 4.1 Verify `pydantic-ai-skills` and `ag-ui-protocol` are installed and importable in this worktree's venv

  Confirm that `agent/pyproject.toml` contains both `pydantic-ai-skills>=0.10.0` AND `ag-ui-protocol` in the `dependencies` list. Run `cd agent && uv sync` if either is missing from the venv. Verify all three critical imports work: `pydantic_ai_skills.SkillsCapability`, `ag_ui.core`, and `src.agent.agent`.

  **Done when:**
  - `agent/pyproject.toml` contains `pydantic-ai-skills>=0.10.0` in the `dependencies` list
  - `agent/pyproject.toml` contains `ag-ui-protocol` in the `dependencies` list
  - `agent/.venv/bin/python -c "from pydantic_ai_skills import SkillsCapability"` exits with code 0
  - `agent/.venv/bin/python -c "from ag_ui.core import *"` exits with code 0
  - `agent/.venv/bin/python -c "from src.agent import agent"` exits with code 0 (full agent module loads)
  - `agent/.venv/bin/python -c "import ast; ast.parse(open('agent/src/agent.py').read())"` exits with code 0 (valid syntax)

  **Stop and hand off if:** `uv sync` fails with a dependency conflict between `pydantic-ai-skills>=0.10.0` and the existing `pydantic-ai-slim` version — document the exact error message and version numbers.

## Human Handoff — Cross-worktree sync

> The following steps require access to `/home/ncheaz/git/dkp-demo/` (main worktree) which is outside the Ralph loop's workspace. These MUST be performed manually by the operator.

The agent process runs from the main worktree at `/home/ncheaz/git/dkp-demo/` using its own `.venv`. When the agent starts, it loads source from this specs worktree but resolves dependencies from the main worktree's venv. After the Ralph loop completes all checkbox tasks above, the operator MUST:

1. **Sync source files** to the main worktree:
   ```bash
   cp /home/ncheaz/git/dkp-demo-with-specs/dkp-demo/agent/src/agent.py /home/ncheaz/git/dkp-demo/agent/src/agent.py
   cp /home/ncheaz/git/dkp-demo-with-specs/dkp-demo/agent/pyproject.toml /home/ncheaz/git/dkp-demo/agent/pyproject.toml
   ```

2. **Install dependencies** in the main worktree's venv:
   ```bash
   cd /home/ncheaz/git/dkp-demo/agent && uv sync
   ```

3. **Verify** all imports work in the main worktree:
   ```bash
   /home/ncheaz/git/dkp-demo/agent/.venv/bin/python -c "from pydantic_ai_skills import SkillsCapability"
   /home/ncheaz/git/dkp-demo/agent/.venv/bin/python -c "from ag_ui.core import *"
   /home/ncheaz/git/dkp-demo/agent/.venv/bin/python -c "from src.agent import agent"
   ```

4. **Re-start the agent** and confirm no `ModuleNotFoundError` or `ImportError` appears.
