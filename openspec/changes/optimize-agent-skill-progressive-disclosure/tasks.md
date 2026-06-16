## 1. Pre-flight Baseline

- [ ] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all tests later tasks require.
  - Done when:
    - `.ralph/baselines/pytest.txt` exists with full output
    - the captured file ends with a literal `EXIT=0` line
    - `.ralph/baselines/optimize-agent-skill-readme.md` lists pytest as passing and baseline details
  - Stop and hand off if: `pytest` is non-deterministic or fails on the first run.

## 2. Relocate Detailed Spec Rules to References

- [ ] **Relocate Slovak trigger patterns and translations to parameter extraction spec**
  - Scope: `.agents/skills/run-generate-design/references/parameter-extraction-spec.md`
  - Change: Slovak translations, dictionaries, and label mappings from Step 3 of the monolithic `SKILL.md` are added to the parameter extraction specification.
  - Done when:
    - `grep -q "Slovak trigger patterns" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` returns match (exit 0)
    - `grep -q "Slovak label" .agents/skills/run-generate-design/references/parameter-extraction-spec.md` returns match (exit 0)
    - `pytest` exits 0
  - Stop and hand off if: `parameter-extraction-spec.md` is not writeable or the schema fails validation.

- [ ] **Consolidate formatting examples in response formatting spec**
  - Scope: `.agents/skills/run-generate-design/references/response-formatting-spec.md`
  - Change: Ensure that response formatting examples (the English and Slovak design summaries) are consolidated under the formatting spec.
  - Done when:
    - `grep -q "## Návrh strechy" .agents/skills/run-generate-design/references/response-formatting-spec.md` returns match (exit 0)
    - `pytest` exits 0
  - Stop and hand off if: the formatting spec file does not exist or cannot be parsed.

## 3. Refactor Main SKILL.md for Progressive Disclosure

- [ ] **Refactor SKILL.md to act as a slim workflow coordinator**
  - Scope: `.agents/skills/run-generate-design/SKILL.md`
  - Change: `SKILL.md` is refactored to be under 100 lines, removing inline classification trigger tables, parameter extraction patterns, language mapping tables, pricing formulas, and response templates, and adding directive instructions to call `read_skill_resource`.
  - Done when:
    - `wc -l .agents/skills/run-generate-design/SKILL.md | cut -d' ' -f1` returns less than 100
    - `grep -q "read_skill_resource" .agents/skills/run-generate-design/SKILL.md` returns match (exit 0)
    - `grep -q "pricing-formula" .agents/skills/run-generate-design/SKILL.md` returns match (exit 0)
    - `pytest` exits 0
  - Stop and hand off if: the count of lines in `SKILL.md` is greater than or equal to 100 after refactoring.

## 4. Prompt Redundancy Review & Verification

- [ ] **Check agent base system prompt for redundant rules**
  - Scope: `agent/src/agent.py`
  - Change: The system prompt in `agent.py` is reviewed for any redundant workflow rules that are already defined inside the skill or reference specifications and cleaned up if necessary.
  - Done when:
    - `agent/src/agent.py` contains a system prompt focusing on identity, absolute rules, tool catalog, and the progressive disclosure hint, with no detailed classification or extraction rules
    - `pytest` exits 0
  - Stop and hand off if: any changes to the system prompt break existing tool discovery or capability routing.

- [ ] **Verify entire agent decision loop behaves identically**
  - Scope: `test/`
  - Change: Run the full test suite to verify that the progressive disclosure routing behaves exactly as before.
  - Done when:
    - `pytest` exits 0
  - Stop and hand off if: `pytest` failures are detected that are related to the modified skill loading format.
