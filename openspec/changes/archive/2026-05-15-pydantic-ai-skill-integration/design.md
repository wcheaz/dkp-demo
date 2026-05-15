## Context

The agent (`agent/src/agent.py`) uses Pydantic AI with a monolithic system prompt (~100 lines, ~1500 tokens) that includes identity, tone rules, tool descriptions, the full decision-loop workflow, parameter extraction tables, pricing formula instructions, and response-formatting rules. This content is injected on every request regardless of whether the user needs design services.

The `.agents/skills/run-generate-design/` directory already contains a complete `SKILL.md` with the same workflow content plus 7 reference documents. This skill conforms to the Agent Skills specification but is not wired into the agent through progressive disclosure.

Current agent constructor:
```python
agent = Agent(model, deps_type=StateDeps, system_prompt=(<~100 line string>))
```

No `capabilities` or `toolsets` are currently configured.

## Goals / Non-Goals

**Goals:**
- Reduce per-request token cost by moving detailed workflow instructions to on-demand skill loading
- Wire `pydantic-ai-skills` into the agent via `SkillsCapability` (the recommended integration path)
- Keep agent behavior identical — same outputs for same inputs
- Enable future skill additions by dropping new SKILL.md files into `.agents/skills/`

**Non-Goals:**
- Adding new agent capabilities or tools
- Changing the `run-generate-design` skill content or reference documents
- Adding a skill registry (GitSkillsRegistry) — local directory discovery is sufficient
- Creating additional skills (e.g., `knowledge-query`, `pricing-estimation`)
- Changing any frontend tool behavior or registration

## Decisions

### D1: Use `SkillsCapability` over `SkillsToolset`

**Choice**: `SkillsCapability` via `capabilities=[...]`

**Alternatives considered**:
- `SkillsToolset` via `toolsets=[...]` — same runtime behavior but requires manual toolset management; the capabilities API is the recommended path per library docs

**Rationale**: `SkillsCapability` wraps `SkillsToolset` and injects both tools and instructions through the higher-level capabilities API. Cleaner integration, fewer manual steps.

### D2: Exclude `run_skill_script` and `list_skills`

**Choice**: `exclude_tools=["run_skill_script", "list_skills"]`

**Rationale**:
- `run_skill_script`: The `run-generate-design` skill is instruction-only (no scripts directory). Offering this tool to the LLM would invite a no-op call.
- `list_skills`: The slim system prompt already lists available skills with a brief description. An extra tool call to list them is redundant and wastes a turn.

### D3: Skills directory path resolution

**Choice**: Resolve relative to `agent.py` using `Path(__file__).resolve().parent.parent.parent / ".agents" / "skills"`

**Rationale**: The skill directory is at `.agents/skills/` relative to the project root. `agent.py` lives at `agent/src/agent.py`, so three parents up reaches the project root. This avoids hardcoded absolute paths and works across environments.

### D4: System prompt split — what stays vs what moves

**Stays in base system prompt** (always loaded, ~20 lines):
- Agent identity ("truss and roof engineering assistant")
- ABSOLUTE RULES: emoji prohibition, narration prohibition, forbidden phrases
- Tool catalog: list of 7 tool names with one-line descriptions
- Skill hint: "Load run-generate-design for the full decision-loop workflow"

**Moves to skill** (on-demand, already in SKILL.md):
- Intent classification rules and trigger phrases
- 9-field parameter extraction table
- Tool action simulation instructions
- Response formatting rules (3-form output)
- Collection loop instructions
- Knowledge base search algorithm details

### D5: `auto_reload=True`

**Choice**: Enable `auto_reload=True` on `SkillsCapability`

**Rationale**: During development, edits to `SKILL.md` or reference files are picked up without restarting the agent. Performance cost is negligible for a single skill.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Extra LLM turn to call `load_skill` on design requests | The ~1 extra tool call costs fewer tokens than always injecting the full workflow. Net savings even with the extra turn. |
| LLM forgets to load the skill before attempting design tasks | The slim system prompt explicitly instructs: "Load run-generate-design for the full decision-loop workflow." The skill hint appears on every request. |
| `pydantic-ai-skills` library compatibility with `pydantic-ai==1.69.0` | Pin `pydantic-ai-skills>=0.10.0` which targets pydantic-ai >=1.0. Verify with `uv sync` and a smoke test. |
| Skill directory path changes | Path is resolved relative to `agent.py` using `Path(__file__)`, not hardcoded. If the file moves, the path expression updates. |
| Behavior regression after prompt refactor | Run existing test suite and manual smoke tests comparing agent outputs before and after. The skill content is identical to what was in the system prompt. |
