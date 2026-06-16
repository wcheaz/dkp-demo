## 1. Pre-flight Baseline

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under [baselines/](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/)
  - Change: Capture the current state of all quality gates required by subsequent tasks:
    - Test: `PYTHONPATH=agent/src uv run pytest test/ > .ralph/baselines/optimize-agent-skill-progressive-disclosure-test.txt; echo "EXIT=$?" >> .ralph/baselines/optimize-agent-skill-progressive-disclosure-test.txt`
    - Lint: `uv run ruff check agent/src/agent.py > .ralph/baselines/optimize-agent-skill-progressive-disclosure-lint.txt; echo "EXIT=$?" >> .ralph/baselines/optimize-agent-skill-progressive-disclosure-lint.txt`
    - Typecheck: `uv run mypy agent/src/agent.py > .ralph/baselines/optimize-agent-skill-progressive-disclosure-typecheck.txt; echo "EXIT=$?" >> .ralph/baselines/optimize-agent-skill-progressive-disclosure-typecheck.txt`
    - README: Create `.ralph/baselines/optimize-agent-skill-progressive-disclosure-readme.md` detailing the exit codes and any failures.
  - Done when:
    - `test -f .ralph/baselines/optimize-agent-skill-progressive-disclosure-test.txt` exits 0
    - `tail -n 1 .ralph/baselines/optimize-agent-skill-progressive-disclosure-test.txt | grep -q "^EXIT=[0-9]\+$"` exits 0
    - `test -f .ralph/baselines/optimize-agent-skill-progressive-disclosure-lint.txt` exits 0
    - `tail -n 1 .ralph/baselines/optimize-agent-skill-progressive-disclosure-lint.txt | grep -q "^EXIT=[0-9]\+$"` exits 0
    - `test -f .ralph/baselines/optimize-agent-skill-progressive-disclosure-typecheck.txt` exits 0
    - `tail -n 1 .ralph/baselines/optimize-agent-skill-progressive-disclosure-typecheck.txt | grep -q "^EXIT=[0-9]\+$"` exits 0
    - `test -f .ralph/baselines/optimize-agent-skill-progressive-disclosure-readme.md` exits 0
  - Stop and hand off if:
    - any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command

## 2. Relocate Slovak trigger patterns and translations to parameter extraction spec

Note: Task 2 and Task 3 are independent and can be executed in parallel or in any order.

- [x] **Add Slovak/English parameter mappings to parameter extraction spec**
  - Scope: [parameter-extraction-spec.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/references/parameter-extraction-spec.md)
  - Change: Slovak translations, English label lists, and valid parameter values dictionaries from Step 3 of the monolithic `SKILL.md` are added to the parameter extraction specification.
  - Done when:
    - `grep -q "Building type" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` exits 0
    - `grep -q "Typ budovy" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` exits 0
    - `grep -q "štítová" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` exits 0
    - `grep -q "Využitie podkrovia" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` exits 0
    - `grep -q "Family house" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` exits 0
    - `grep -q "Rodinný dom" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` exits 0
  - Stop and hand off if:
    - there is any ambiguity regarding the Slovak or English field mapping tables or trigger patterns in `SKILL.md`

## 3. Consolidate formatting examples in response formatting spec

- [ ] **Consolidate formatting examples in response formatting spec**
  - Scope: [response-formatting-spec.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/references/response-formatting-spec.md)
  - Change: Response formatting examples and mappings in the response formatting spec are updated to reference `parameter-extraction-spec.md` instead of `SKILL.md`.
  - Done when:
    - `grep -q "parameter-extraction-spec.md" .agents/skills/run-generate-design/references/response-formatting-spec.md` exits 0
    - `! grep -q "SKILL.md" .agents/skills/run-generate-design/references/response-formatting-spec.md` exits 0
  - Stop and hand off if:
    - there is any ambiguity in how formatting rules and examples should be consolidated under `response-formatting-spec.md`

## 4. Refactor Main SKILL.md for Progressive Disclosure

- [ ] **Refactor SKILL.md to act as a slim workflow coordinator**
  - Scope: [SKILL.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/SKILL.md)
  - Change: `SKILL.md` is refactored to be under 100 lines, removing inline classification trigger tables, parameter extraction patterns, language mapping tables, pricing formulas, and response templates, and adding directive instructions to call `read_skill_resource`.
  - Done when:
    - `test $(wc -l < .agents/skills/run-generate-design/SKILL.md) -lt 100` exits 0
    - `grep -q "read_skill_resource" .agents/skills/run-generate-design/SKILL.md` exits 0
    - `! grep -q "Rozmery pôdorysu" .agents/skills/run-generate-design/SKILL.md` exits 0
    - `! grep -F -q "floor_area = width * height" .agents/skills/run-generate-design/SKILL.md` exits 0
  - Stop and hand off if:
    - the workflow coordination steps in `SKILL.md` cannot be cleanly formulated under 100 lines, or the LLM directive instructions for `read_skill_resource` are ambiguous

## 5. Prompt Redundancy Review & Verification

- [ ] **Update agent base system prompt to reference progressive disclosure**
  - Scope: [agent.py](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py)
  - Change: The system prompt in `agent.py` is updated to explicitly instruct the agent to fetch detailed rules dynamically using `read_skill_resource` when the skill is loaded, and any duplicated instructions are removed.
  - Done when:
    - `grep -q "read_skill_resource" agent/src/agent.py` exits 0
    - `! grep -q "get_knowledge_summary:" agent/src/agent.py` exits 0
    - `! grep -q "generate_design:" agent/src/agent.py` exits 0
    - `python3 -m py_compile agent/src/agent.py` exits 0
    - `ruff check agent/src/agent.py` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - `mypy agent/src/agent.py` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if:
    - there is ambiguity in how the base system prompt should direct the agent to load and use skill resources, or editing `agent.py` causes syntax/compilation errors

- [ ] **Verify entire agent decision loop behaves identically**
  - Scope: no code edits; runs pytest verification suite on [test/](file:///home/ncheaz/git/dkp-demo/test/)
  - Change: Run the full test suite to verify that the progressive disclosure routing behaves exactly as before.
  - Done when:
    - `PYTHONPATH=agent/src uv run pytest test/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if:
    - test failures occur that cannot be resolved within the scope of this OpenSpec, or if there are new failures indicating a regression in core logic
