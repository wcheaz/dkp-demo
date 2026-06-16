## MODIFIED Requirements

### Requirement: On-demand skill loading via load_skill
The LLM SHALL call `load_skill("run-generate-design")` to retrieve the high-level decision-loop workflow. The LLM MUST call `read_skill_resource` to dynamically retrieve the specific parameter extraction rules, translation dictionaries, pricing formula instructions, and response formatting guidelines from the reference files when executing those steps.

#### Scenario: load_skill returns high-level skill content
- **WHEN** the LLM calls `load_skill("run-generate-design")` during a request
- **THEN** the tool returns the slimmed-down workflow content of `.agents/skills/run-generate-design/SKILL.md`

#### Scenario: read_skill_resource returns reference files
- **WHEN** the LLM calls `read_skill_resource("run-generate-design", "references/pricing-formula.md")` during a request
- **THEN** the tool returns the content of `.agents/skills/run-generate-design/references/pricing-formula.md`

### Requirement: Behavioral parity
After integration of progressive disclosure routing, the agent SHALL produce identical outputs for identical inputs compared to the monolithic skill setup. The detailed workflow rules and dictionaries are loaded on-demand via reference files, and the LLM SHALL follow these rules correctly to produce correct designs, quotes, and formatted responses.

#### Scenario: Design request produces same output
- **WHEN** the agent receives a design-related message (e.g., "I need a truss for a 10m span")
- **THEN** the agent loads the skill, calls `read_skill_resource` to read the required reference specifications on-demand, and produces the same structured response
- **AND** the response contains the expected design output format with no emojis and no narration

#### Scenario: Knowledge query produces same output
- **WHEN** the agent receives a knowledge-base query (e.g., "What projects do you have?")
- **THEN** the agent responds without loading the skill or any parameter/pricing references and produces the same response
