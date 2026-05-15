## ADDED Requirements

### Requirement: SkillsCapability wired into Agent constructor
The agent SHALL use `SkillsCapability` from `pydantic-ai-skills` via the `capabilities` parameter of the `Agent()` constructor. The capability SHALL be configured with the skills directory at `.agents/skills/`, `auto_reload=True`, and `validate=True`.

#### Scenario: Agent initializes with SkillsCapability
- **WHEN** the agent module is loaded
- **THEN** the Agent instance has a `SkillsCapability` in its capabilities list pointing to `.agents/skills/`

#### Scenario: Skills directory path resolves correctly
- **WHEN** `agent.py` is executed from any working directory
- **THEN** the skills directory path resolves to `<project_root>/.agents/skills/` using `Path(__file__)`-relative resolution

### Requirement: Excluded tools
The `SkillsCapability` SHALL exclude `run_skill_script` and `list_skills` from the tools offered to the LLM. The `run-generate-design` skill is instruction-only and has no scripts. The skill metadata is already surfaced in the slim system prompt.

#### Scenario: run_skill_script not available to LLM
- **WHEN** the LLM receives its tool list during a request
- **THEN** `run_skill_script` is not among the available tools

#### Scenario: list_skills not available to LLM
- **WHEN** the LLM receives its tool list during a request
- **THEN** `list_skills` is not among the available tools

### Requirement: Slim base system prompt
The agent's `system_prompt` SHALL contain only: agent identity, absolute rules (emoji prohibition, narration prohibition, forbidden phrases), the tool catalog (7 tools with one-line descriptions), and a skill hint instructing the LLM to load `run-generate-design` when it needs the full workflow. The system prompt SHALL NOT contain intent classification rules, parameter extraction tables, tool action simulation instructions, or response formatting rules.

#### Scenario: Base prompt contains identity and rules
- **WHEN** the agent starts a new session
- **THEN** the system prompt includes the agent identity ("truss and roof engineering assistant"), emoji prohibition, narration prohibition, and forbidden phrase rules

#### Scenario: Base prompt contains tool catalog
- **WHEN** the agent starts a new session
- **THEN** the system prompt lists all 7 tools: `get_knowledge_summary`, `query_knowledge_base`, `generate_quote`, `generate_design`, `modify_design_entry`, `update_design_parameters`, `reset_design`

#### Scenario: Base prompt contains skill hint
- **WHEN** the agent starts a new session
- **THEN** the system prompt includes an instruction to call `load_skill("run-generate-design")` for the full decision-loop workflow, parameter extraction rules, and response-formatting guidelines

#### Scenario: Base prompt does not contain detailed workflow rules
- **WHEN** the agent starts a new session
- **THEN** the system prompt does NOT contain intent classification trigger phrases, the 9-field parameter extraction table, tool action simulation outputs, or the 3-form response formatting rules

### Requirement: On-demand skill loading via load_skill
The LLM SHALL be able to call `load_skill("run-generate-design")` to retrieve the full decision-loop workflow, parameter extraction rules, pricing formula instructions, and response formatting guidelines from the skill's SKILL.md file.

#### Scenario: load_skill returns skill content
- **WHEN** the LLM calls `load_skill("run-generate-design")` during a request
- **THEN** the tool returns the content of `.agents/skills/run-generate-design/SKILL.md`

#### Scenario: read_skill_resource returns reference files
- **WHEN** the LLM calls `read_skill_resource("run-generate-design", "references/pricing-formula.md")` during a request
- **THEN** the tool returns the content of `.agents/skills/run-generate-design/references/pricing-formula.md`

### Requirement: Dependency addition
`pydantic-ai-skills>=0.10.0` SHALL be listed in `agent/pyproject.toml` dependencies. Running `uv sync` in the `agent/` directory SHALL succeed without errors.

#### Scenario: Dependency resolves
- **WHEN** `uv sync` is run in the `agent/` directory
- **THEN** `pydantic-ai-skills` is installed and `uv sync` exits with code 0

### Requirement: Behavioral parity
After integration, the agent SHALL produce identical outputs for identical inputs compared to the pre-integration agent. The detailed workflow rules previously in the system prompt are now loaded on-demand via the skill, but the LLM SHALL follow the same rules when the skill is loaded.

#### Scenario: Design request produces same output
- **WHEN** the agent receives a design-related message (e.g., "I need a truss for a 10m span")
- **THEN** the agent loads the skill, follows the same decision-loop workflow, and produces the same structured response as the pre-integration agent

#### Scenario: Knowledge query produces same output
- **WHEN** the agent receives a knowledge-base query (e.g., "What projects do you have?")
- **THEN** the agent responds without loading the skill and produces the same response as the pre-integration agent
