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

## 4. Design State Bridge

Root cause: `generate_design` is a frontend `useFrontendTool` (`src/app/page.tsx:413-474`) that creates designs in React state only. `generate_dxf` is a backend `@agent.tool` (`agent/src/agent.py:413-442`) that reads `ctx.deps.state.designs` (Python). The AG-UI protocol syncs frontend→backend state once at run start via `YourState.model_validate(raw_state)`, so designs created mid-run by the frontend tool are invisible to the backend tool. Additionally, the frontend stores `"---"` strings for `price` (line 460) and `roofPitch` (line 446) when values are missing, which would fail Pydantic validation on subsequent runs since the backend models declare `Optional[int]`.

Fix: convert `generate_dxf` to a frontend `useFrontendTool` that reads the design from React state and calls the existing `/api/dxf/generate` endpoint (`agent/src/main.py:24-55`) to build the DXF.

- [x] **4.1 Pre-flight: record design-bridge test baselines**
  - Scope: no code edits; writes under `.ralph/baselines/`
  - Change: Capture current test gate output for comparison after the state bridge fix.
  - Done when:
    - `.ralph/baselines/dxf-bridge-test.txt` exists with full output from `python3 -m pytest test/test_dxf_builder.py test/test_generate_dxf.py test/test_dxf_endpoint.py -q`
    - `.ralph/baselines/dxf-bridge-test.txt` ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/dxf-bridge-readme.md` lists test file names, exit code, and test count
  - Stop and hand off if: any gate is nondeterministic across two runs.

- [x] **4.2 Convert generate_dxf from backend tool to frontend tool**
  - Scope: `agent/src/agent.py` (remove `@agent.tool`-decorated `generate_dxf` at lines 413-442), `src/app/page.tsx` (add `useFrontendTool` named `generate_dxf`)
  - Change: Remove the `@agent.tool`-decorated `generate_dxf` from `agent.py`. Add a `useFrontendTool` named `generate_dxf` in `page.tsx` that: (1) receives `design_id` from the agent, (2) looks up the design entry in `latestStateRef.current.designs`, (3) calls the agent server's `/api/dxf/generate` endpoint via `fetch` using `process.env.AGENT_URL` (default `http://localhost:8000/`) as the base URL — **not** a relative path, since the endpoint lives on the agent server (port 8000), not the Next.js UI server — with the entry's parameters (stripping `"---"` placeholder strings before sending), (4) base64-encodes the response bytes, (5) stores the result in the entry's `dxfContent` field in React state, (6) returns a confirmation string. Error cases return descriptive messages matching the original tool's behavior (design not found, no parameters, build error from non-2xx response).
  - Done when:
    - `rg "async def generate_dxf" agent/src/agent.py` returns no matches
    - `rg '"generate_dxf"' src/app/page.tsx` returns at least 2 matches
    - The frontend tool handler reads designs from `latestStateRef.current.designs` by id
    - The frontend tool handler constructs the endpoint URL using `process.env.AGENT_URL` (not a relative path like `/api/dxf/generate`) — e.g. `const agentUrl = process.env.AGENT_URL || 'http://localhost:8000/'; fetch(agentUrl + 'api/dxf/generate', ...)`
    - The frontend tool handler filters out `"---"` values from the parameters before sending as JSON body
    - The frontend tool handler base64-encodes the DXF response and stores it in the matching design entry's `dxfContent`
    - Error cases (design not found, missing required parameters, non-2xx response) return descriptive strings
    - `python3 -m pytest test/test_dxf_builder.py test/test_dxf_endpoint.py -q` exits 0 (builder and endpoint unchanged)
  - Stop and hand off if: the `/api/dxf/generate` endpoint no longer returns raw DXF bytes with `application/dxf` content type, or its request schema has changed from accepting `DesignParameters` as JSON body.

- [x] **4.3 Remove obsolete generate_dxf backend tool tests**
  - Scope: `test/test_generate_dxf.py`
  - Change: Remove `test/test_generate_dxf.py` — it tests the backend `@agent.tool` version of `generate_dxf` which no longer exists after task 4.2. The DXF builder geometry is covered by `test/test_dxf_builder.py` (48 tests) and the HTTP endpoint by `test/test_dxf_endpoint.py` (9 tests). Frontend tool behavior requires browser-level testing (outside scope).
  - Done when:
    - `test -f test/test_generate_dxf.py` returns non-zero (file removed)
    - `rg "from src.agent import.*generate_dxf" test/` returns no matches
    - `python3 -m pytest test/test_dxf_builder.py test/test_dxf_endpoint.py -q` exits 0
  - Stop and hand off if: removing the file causes import errors in other test files (check with `rg "test_generate_dxf\|from test.test_generate_dxf" test/`).

- [x] **4.4 Verify design-bridge fix passes all test gates**
  - Scope: no code edits; runs full test suite and validates artifact consistency
  - Change: Confirm all DXF-related tests pass and the tool migration is complete.
  - Done when:
    - `python3 -m pytest test/test_dxf_builder.py test/test_dxf_endpoint.py -q` exits 0
    - `rg "async def generate_dxf" agent/src/agent.py` returns no matches (backend tool removed)
    - `rg '"generate_dxf"' src/app/page.tsx` returns at least 2 matches (frontend tool present)
    - `rg "generate_dxf" .agents/skills/run-generate-design/SKILL.md` returns at least 2 matches (skill still instructs the agent to call the tool)
  - Stop and hand off if: any previously-passing test from the pre-flight baseline now fails, or the skill file no longer references `generate_dxf`.

## Human Handoff

The following items require human execution and are NOT part of the autonomous loop:

- **Validate DXF output in external CAD tools**: Open generated DXF files (from `test/test_dxf_builder.py` `TestGenerateExampleFiles` output or via the `/api/dxf/generate` endpoint) in LibreCAD and the embedded cad-viewer. Verify layer visibility, dimension annotations, scaling, and pan/zoom work correctly. Document any visual discrepancies.
- **Evaluate cad-viewer's offline HTML export**: Assess whether the cad-viewer's one-click HTML export is useful for the demo (e.g., "Share this design" button). Low priority — pursue only if it adds demo value.
- **Fix `"---"` placeholder type mismatch for Pydantic compatibility**: The frontend `generate_design` handler stores `"---"` strings for `price` and `roofPitch` when values are missing (`src/app/page.tsx:446,460`). The backend `DesignEntry.price` and `DesignParameters.roofPitch` are `Optional[int]` (`agent/src/agent.py:174,189`). On any subsequent agent run, `YourState.model_validate(raw_state)` will fail with a Pydantic `ValidationError` if designs with `"---"` values exist in the frontend state. Fix requires: (1) using `undefined`/`null` instead of `"---"` in `generate_design` parameters, (2) updating `isIncomplete()` in `src/components/design-component.tsx:38-39` to check for `undefined`/`null` instead of `"---"`, (3) updating price display at line 202 to handle `undefined`/`null`. This is deferred because the immediate DXF fix (task 4.2) sidesteps the issue by filtering `"---"` in the frontend tool before calling the endpoint.
