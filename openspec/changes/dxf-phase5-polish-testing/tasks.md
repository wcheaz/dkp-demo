## 1. Pre-flight

- [x] **1.1 Pre-flight: record DXF test gate baselines**
  - Scope: no code edits; writes under `.ralph/baselines/`
  - Change: Capture current state of DXF-related test gates so later verification tasks can classify failures against a known baseline.
  - Done when:
    - `.ralph/baselines/dxf-phase5-test.txt` exists with full pytest output from `python3 -m pytest test/test_dxf_builder.py -q`
    - `.ralph/baselines/dxf-phase5-test.txt` ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/dxf-phase5-integration.txt` exists with full output from `python3 -m pytest test/test_generate_dxf.py test/test_dxf_endpoint.py -q`
    - `.ralph/baselines/dxf-phase5-integration.txt` ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/dxf-phase5-readme.md` lists gate names, exit codes, and test counts for each captured baseline
    - EXIT code in `.ralph/baselines/dxf-phase5-test.txt` is 0 (unit tests must be green before any skill edits)
  - Stop and hand off if: any gate is nondeterministic across two runs, or the test count for `test/test_dxf_builder.py` is not 48.

## 2. DXF Skill Integration

- [x] **2.1 Add DXF generation step to run-generate-design skill**
  - Scope: `.agents/skills/run-generate-design/SKILL.md`
  - Change: A new Step 4g (DXF generation) is added after Step 4f. It auto-triggers when `design-generation` or `design-modification` produces `"complete"` status, instructing the agent to call `generate_dxf` with the current design ID. The Step 4 introduction's auto-execution rules are updated to mention DXF alongside pricing.
  - Done when:
    - `SKILL.md` contains a `#### 4g — DXF generation` section after the existing `#### 4f` section
    - The Step 4 auto-execution exception block mentions both pricing (4c) and DXF generation (4g) as auto-triggered when status is `"complete"`
    - `grep -c "generate_dxf" .agents/skills/run-generate-design/SKILL.md` returns at least 2 matches
  - Stop and hand off if: the existing step numbering would require restructuring beyond adding a single new 4g section.

- [x] **2.2 Create DXF builder API reference doc**
  - Scope: `.agents/skills/run-generate-design/references/dxf-builder-api.md`
  - Change: A new reference document exists describing `build_dxf` function signature, `DesignParameters` field mapping, DXF output format (R2000, 5 layers), and the auto-trigger rule.
  - Done when:
    - `test -f .agents/skills/run-generate-design/references/dxf-builder-api.md` exits 0
    - File contains `build_dxf`, `DesignParameters`, `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, `Title_Block` (all 5 layer names)
    - File states the auto-trigger rule: DXF generation fires when design status is `"complete"`
    - `head -1 .agents/skills/run-generate-design/references/dxf-builder-api.md` starts with `# ` (H1 title, matching the pattern in `references/pricing-formula.md`)
  - Stop and hand off if: the new doc's heading structure (H1 title + intro paragraph + `##` sections) does not match the pattern in `references/pricing-formula.md`.

## 3. Verification

- [x] **3.1 Verify skill integration does not break existing tests**
  - Scope: no code edits; runs test suite and validates skill file syntax
  - Change: Confirm that adding the DXF step to the skill does not break any existing agent or DXF tests.
  - Done when:
    - `python3 -m pytest test/test_dxf_builder.py test/test_generate_dxf.py test/test_dxf_endpoint.py -q` exits 0, or failures match the pre-flight baseline with no new failures
    - `.agents/skills/run-generate-design/SKILL.md` YAML frontmatter between `---` delimiters is parseable: `python3 -c "import yaml; yaml.safe_load(open('.agents/skills/run-generate-design/SKILL.md').read().split('---')[1])"` exits 0
  - Stop and hand off if: any previously-passing test now fails and the failure is not caused by a trivial environmental issue, or the failure does not match the pre-flight baseline.

## Human Handoff

The following items require human execution and are NOT part of the autonomous loop:

- **Validate DXF output in external CAD tools**: Open generated DXF files (from `test/test_dxf_builder.py` `TestGenerateExampleFiles` output or via the `/api/dxf/generate` endpoint) in LibreCAD and the embedded cad-viewer. Verify layer visibility, dimension annotations, scaling, and pan/zoom work correctly. Document any visual discrepancies.
- **Evaluate cad-viewer's offline HTML export**: Assess whether the cad-viewer's one-click HTML export is useful for the demo (e.g., "Share this design" button). Low priority — pursue only if it adds demo value.
