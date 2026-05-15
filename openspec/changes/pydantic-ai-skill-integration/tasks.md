## 1. Dependency and Imports

- [ ] 1.1 Add `pydantic-ai-skills>=0.10.0` to the `dependencies` list in `agent/pyproject.toml`, then run `cd agent && uv sync` to install. Verify the command exits with code 0 and `pydantic_ai_skills` is importable.
- [ ] 1.2 Add `from pydantic_ai_skills import SkillsCapability` import at the top of `agent/src/agent.py`. Add `SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / ".agents" / "skills"` constant. Verify the import resolves without error by running `python -c "from pydantic_ai_skills import SkillsCapability"`.

## 2. Agent Constructor Refactor

- [ ] 2.1 Replace the existing `Agent(...)` call in `agent/src/agent.py` to add `capabilities=[SkillsCapability(directories=[str(SKILLS_DIR)], exclude_tools=["run_skill_script", "list_skills"], validate=True, auto_reload=True)]`. Remove the old `system_prompt=` keyword argument temporarily (it will be restored in the next task). Verify the agent initializes without errors.
- [ ] 2.2 Rewrite the `system_prompt` string to the slim version containing only: agent identity, ABSOLUTE RULES (emoji prohibition, narration prohibition, forbidden phrases), the 7-tool catalog with one-line descriptions, and the skill hint instructing `load_skill("run-generate-design")` for the full workflow. Re-attach it as the `system_prompt=` parameter. Done when: the system prompt is under 25 lines, contains no intent classification rules, no parameter extraction table, no tool action simulation, and no response formatting rules.

## 3. Verification

- [ ] 3.1 Run any existing test suite (`pytest` or equivalent) and confirm all tests pass. If no tests exist, start the agent and send a knowledge-base query (e.g., "What projects do you have?") confirming it responds correctly without loading the skill. Done when: agent responds with knowledge summary content.
- [ ] 3.2 Send a design-related message to the agent (e.g., "I need a truss for a 10m span roof") and confirm the agent calls `load_skill("run-generate-design")`, follows the decision-loop workflow, and produces a structured design response. Done when: the response contains the expected design output format and the agent loaded the skill during the conversation.
