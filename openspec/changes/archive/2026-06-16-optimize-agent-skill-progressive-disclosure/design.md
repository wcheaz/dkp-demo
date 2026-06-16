## Context

The `run-generate-design` skill in `.agents/skills/run-generate-design/SKILL.md` is currently a monolithic file (~12KB) containing step-by-step workflow descriptions alongside detailed trigger tables (English and Slovak), Slovak translation dictionaries, mathematical pricing formulas with worked examples, and response formatting templates. Loading this large file uses substantial context tokens on the first turn of the conversation.

The `pydantic-ai-skills` library provides the `read_skill_resource` tool, which is already registered on the agent. This allows the LLM to dynamically load individual reference files under the `references/` subdirectory. We will restructure the skill to make use of this feature to achieve progressive disclosure.

## Goals / Non-Goals

**Goals:**
- Refactor [SKILL.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/SKILL.md) into a slim workflow coordinator (routing index) under 100 lines.
- Move all dense tables, trigger patterns, mathematical pricing formulas, Slovak translation dictionaries, and formatting examples to dedicated files under [.agents/skills/run-generate-design/references/](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/references/).
- Ensure the main `SKILL.md` file contains strong, explicit instructions directing the LLM to call `read_skill_resource` dynamically for detailed steps.
- Verify that there are no overlapping rules or redundancies between the base system prompt in `agent.py` and the skill.
- Keep all unit tests passing.

**Non-Goals:**
- Modifying tool interfaces or changing tool signatures.
- Altering the pricing calculation formula logic or parameters.
- Changing frontend React components or `useFrontendTool` declarations.

## Decisions

### Decision 1: Organization of Locale Mapping & Extraction Details
- **Choice:** Move Slovak translations, field label dictionaries, and parameter trigger patterns from `SKILL.md` Step 3 directly to the existing reference file [references/parameter-extraction-spec.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/references/parameter-extraction-spec.md).
- **Alternative considered:** Create a new `references/locale-mapping.md` file.
- **Rationale:** The parameter extraction spec already describes the extraction process. Consolidating the Slovak trigger patterns, translation tables, and examples in `references/parameter-extraction-spec.md` keeps it self-contained and avoids creating a new reference file, keeping tool selection simple for the LLM.

### Decision 2: Structuring of Response Formatting Reference
- **Choice:** Consolidate formatting rules and output examples entirely in [references/response-formatting-spec.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/references/response-formatting-spec.md) and remove duplicates from `SKILL.md` Step 3 and Step 5.
- **Rationale:** Response formatting guidelines are already defined in `references/response-formatting-spec.md`. Having them there prevents copy-paste errors and saves significant tokens.

### Decision 3: Instruction phrasing in SKILL.md
- **Choice:** Add explicit, highly directive instructions to each step in `SKILL.md` directing the LLM to call `read_skill_resource("run-generate-design", "references/<spec>.md")`.
- **Rationale:** The LLM needs explicit call-to-actions to fetch resources; otherwise, it might attempt to guess or hallucinate the parameters, pricing formulas, or formatting rules instead of loading them.

## Risks / Trade-offs

- **[Risk]** The LLM fails to call `read_skill_resource` and hallucinates parameters, pricing, or Slovak mappings.
  - **Mitigation:** Place strong directive instructions at the beginning of each step in `SKILL.md` (e.g. *"To execute this step, call `read_skill_resource('run-generate-design', 'references/<name>.md')` first"*).
- **[Risk]** Multiple sequential tool calls (`load_skill` followed by `read_skill_resource`) could increase request latency in high-latency environments.
  - **Mitigation:** While there is a slight overhead of an extra tool-call turn, the token savings (~12KB system-level payload reduced to <3KB routing index) and the fact that response time concern "isn't that big of an issue anymore" makes this trade-off highly favorable for overall prompt engineering and accuracy.
