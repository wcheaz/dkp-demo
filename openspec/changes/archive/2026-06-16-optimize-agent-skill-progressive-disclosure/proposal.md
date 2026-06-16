## Why

The `run-generate-design` agent skill currently embeds all detailed trigger tables, Slovak translation dictionaries, deterministic pricing formulas, and formatting examples directly in its main `SKILL.md` file (~12KB). Loading this monolithic skill on the first turn wastes LLM context window tokens and increases response latency. Moving these detailed rules to reference documents and prompting the agent to fetch them dynamically when needed will significantly optimize token consumption and response time.

## What Changes

- **Slim Main Skill Workflow:** Refactor the main `SKILL.md` file to contain only the high-level decision-loop steps. Remove inline tables, mathematical formulas, translation maps, and formatting examples.
- **Dynamic Resource Instruction:** Add explicit instructions to each step in `SKILL.md` telling the LLM to call `read_skill_resource('run-generate-design', 'references/<resource-file>.md')` to fetch the specific rules dynamically.
- **Locale Dictionary Separation:** Move Slovak translation dictionaries and English label lists out of the main `SKILL.md` file and into reference specifications.
- **Check for Other Optimizations:** Analyze the agent's base system prompt in the codebase and check if there are other potential optimizations (e.g. redundant rules or parameters) that can be slimmed down.

## Non-goals

- Altering the actual logic of intent classification, parameter extraction, pricing calculations, or response formatting.
- Modifying the frontend application logic or the React components.
- Rewriting the python implementations of the agent tools.

## Capabilities

### New Capabilities
- `skill-progressive-disclosure`: Implements dynamic on-demand loading of skill reference documents using the `read_skill_resource` tool, turning the main `SKILL.md` into a workflow routing index.

### Modified Capabilities
- `skill-based-prompting`: The routing mechanism and dynamic resolution of reference specifications within the `run-generate-design` skill are modified to enforce progressive disclosure.

## Impact

- **Affected Files:**
  - [.agents/skills/run-generate-design/SKILL.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/SKILL.md) (workflow definitions and instructions)
  - References folder [.agents/skills/run-generate-design/references/](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/references/) (moving dictionaries and examples to spec files)
  - [agent/src/agent.py](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py) (system prompt and skill capability configuration)
