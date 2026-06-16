## 1. Pre-flight Baseline

- [ ] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/optimize-agent-skill-progressive-disclosure-pytest.txt` exists with full output
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/optimize-agent-skill-progressive-disclosure-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Relocate Detailed Spec Rules to References

- [ ] **Relocate Slovak trigger patterns and translations to parameter extraction spec**
  - Scope: `.agents/skills/run-generate-design/references/parameter-extraction-spec.md`
  - Change: Slovak translations, dictionaries, and label mappings from Step 3 of the monolithic `SKILL.md` are added to the parameter extraction specification.
  - Done when:
    - `grep -q "Slovak trigger patterns" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` exits 0
    - `grep -q "Slovak label" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` exits 0
    - `PYTHONPATH=agent/src uv run pytest test/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: `.agents/skills/run-generate-design/references/parameter-extraction-spec.md` is not writable or is missing.

- [ ] **Consolidate formatting examples in response formatting spec**
  - Scope: `.agents/skills/run-generate-design/references/response-formatting-spec.md`
  - Change: Response formatting examples (the English and Slovak design summaries) are consolidated under the response formatting spec.
  - Done when:
    - `grep -q "## Návrh strechy" .agents/skills/run-generate-design/references/response-formatting-spec.md` exits 0
    - `PYTHONPATH=agent/src uv run pytest test/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: `.agents/skills/run-generate-design/references/response-formatting-spec.md` is not writable or is missing.

## 3. Refactor Main SKILL.md for Progressive Disclosure

- [ ] **Refactor SKILL.md to act as a slim workflow coordinator**
  - Scope: `.agents/skills/run-generate-design/SKILL.md`
  - Change: `SKILL.md` is refactored to be under 100 lines, removing inline classification trigger tables, parameter extraction patterns, language mapping tables, pricing formulas, and response templates, and adding directive instructions to call `read_skill_resource`.
  - Done when:
    - `[ $(wc -l < .agents/skills/run-generate-design/SKILL.md) -lt 100 ]` exits 0
    - `grep -q "read_skill_resource" .agents/skills/run-generate-design/SKILL.md` exits 0
    - `grep -q "pricing-formula" .agents/skills/run-generate-design/SKILL.md` exits 0
    - `PYTHONPATH=agent/src uv run pytest test/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: the count of lines in `SKILL.md` is greater than or equal to 100 after refactoring.

## 4. Prompt Redundancy Review & Verification

- [ ] **Remove redundant workflow rules from agent base system prompt**
  - Scope: `agent/src/agent.py`
  - Change: Any detailed workflow rules, parameter lists, or pricing instructions that duplicate skill content are removed from the system prompt in `agent.py`.
  - Done when:
    - `grep -q "load_skill" agent/src/agent.py` exits 0
    - `PYTHONPATH=agent/src uv run pytest test/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: any changes to the system prompt break existing tool discovery or capability routing.

- [ ] **Verify entire agent decision loop behaves identically**
  - Scope: `test/test_reset_design.py`, `test/test_dxf_builder.py`, `test/test_dxf_endpoint.py`
  - Change: Run the full test suite to verify that the progressive disclosure routing behaves exactly as before.
  - Done when:
    - `PYTHONPATH=agent/src uv run pytest test/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: any test fails due to the modified skill loading format or resource resolution.
