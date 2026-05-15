## Why

The agent's monolithic system prompt injects ~1500 tokens of workflow rules, parameter extraction tables, pricing formulas, and response-formatting guidelines on every request — even when the user only asks a simple knowledge-base question. This wastes tokens and makes the prompt harder to maintain. The `run-generate-design` skill already exists at `.agents/skills/run-generate-design/SKILL.md` with the complete decision-loop workflow, but the agent does not load it through progressive disclosure.

## What Changes

- Add `pydantic-ai-skills>=0.10.0` to `agent/pyproject.toml` dependencies
- Wire `SkillsCapability` into the `Agent()` constructor in `agent/src/agent.py`
- Exclude `run_skill_script` and `list_skills` tools (this skill is instruction-only, and metadata is already in the slim prompt)
- Refactor the system prompt into a slim base (identity, tone rules, tool catalog, skill hint)
- Move detailed decision-loop instructions out of the system prompt — they are already in `run-generate-design/SKILL.md` and will be loaded on-demand via `load_skill("run-generate-design")`
- Agent behavior and outputs remain identical; only the delivery mechanism changes

## Capabilities

### New Capabilities
- `skill-based-prompting`: Progressive disclosure of agent instructions via `pydantic-ai-skills`. Covers the two-tier prompt architecture (slim base + on-demand skill loading), `SkillsCapability` wiring, tool exclusions, and the contract between base prompt and skill content.

### Modified Capabilities
_(None — this is a structural refactor. All existing tool behaviors, parameter extraction rules, response formatting, and knowledge-base interactions remain unchanged. The existing specs describe agent behavior, not prompt structure.)_

## Impact

- **`agent/pyproject.toml`**: New dependency `pydantic-ai-skills>=0.10.0`
- **`agent/src/agent.py`**: Agent constructor changes (`capabilities=[SkillsCapability(...)]`), system prompt string shrinks from ~100 lines to ~20 lines
- **`.agents/skills/run-generate-design/`**: No changes — SKILL.md and references already exist and conform to the Agent Skills specification
- **Runtime**: One additional tool call (`load_skill`) on design-related requests; no change on simple knowledge queries
- **Token cost**: ~50 tokens always (skill metadata) + ~800 tokens on-demand (skill content) vs ~1500 tokens always (current)
