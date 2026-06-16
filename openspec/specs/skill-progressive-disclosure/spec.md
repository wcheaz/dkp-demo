## Purpose

Defines the progressive disclosure structure for agent skills, where the main SKILL.md acts as a slim step coordinator and detailed specifications are stored in reference files loaded on-demand via `read_skill_resource`. This optimizes token usage by avoiding loading large dictionaries and formula rules until they are needed.

## Requirements

### Requirement: Slim SKILL.md coordinator
The main skill file at `.agents/skills/run-generate-design/SKILL.md` SHALL contain only the high-level decision-loop step coordinator. It SHALL NOT contain inline intent classification trigger tables, parameter extraction trigger tables, Slovak dictionaries, English labels lists, pricing formula rules, or formatting examples.

#### Scenario: SKILL.md contains only step summaries
- **WHEN** the agent loads `SKILL.md`
- **THEN** the content contains only high-level steps and instructions to load references, with no translation dictionaries or pricing mathematical code

### Requirement: Dynamic reference specifications
The detailed classification triggers, parameter dictionaries, mathematical pricing formulas, and response templates SHALL be stored under `.agents/skills/run-generate-design/references/` in distinct specification files. The steps in `SKILL.md` SHALL instruct the LLM to call `read_skill_resource` to read the corresponding reference file on-demand.

#### Scenario: Loading parameter extraction spec on-demand
- **WHEN** the LLM executes Step 3 of the workflow in `SKILL.md`
- **THEN** it calls `read_skill_resource('run-generate-design', 'references/parameter-extraction-spec.md')` to fetch the trigger patterns and translation maps

### Requirement: Optimization and token validation
The verification suite SHALL ensure that the progressive disclosure structure is verified for token efficiency and that redundant guidelines in both the system prompt and skill specifications are eliminated.

#### Scenario: Check for prompt redundancy
- **WHEN** the optimization check is run
- **THEN** the system prompt is verified to have no overlapping rules with the skill specifications
