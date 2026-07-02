## 1. Baselines and Pre-flight

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/mxf-eaves-height-alignment-test.txt`, `.ralph/baselines/mxf-eaves-height-alignment-typecheck.txt`, and `.ralph/baselines/mxf-eaves-height-alignment-lint.txt` exist with full outputs.
    - every captured gate file ends with a literal `EXIT=<integer>` line.
    - `.ralph/baselines/mxf-eaves-height-alignment-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers.
  - Stop and hand off if:
    - any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Geometry Engine and Test Implementation

- [ ] **Anchor eaves height to 3.12m in MXF roof geometry**
  - Scope: `agent/src/geometry_solver.py`, `test/test_mxf_builder.py`, `test/test_mxf_endpoint.py`
  - Change: Anchor the eaves vertical height at exactly 3.12m and recalculate flat, mono-pitch, gable, and hip roof surface Z coordinates based on this baseline, updating unit test assertions to match.
  - Done when:
    - `rg "MXF_ROOF_EAVES_Z = MXF_ROOF_Z_BASE \+ 0.07" agent/src/geometry_solver.py` exits 0.
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py test/test_mxf_endpoint.py` exits 0.
    - `uv run --project agent ruff check agent/src/geometry_solver.py` exits 0.
    - `uv run --project agent mypy agent/src/geometry_solver.py` exits 0.
  - Stop and hand off if:
    - modifying files introduces syntax errors, or unexpected geometry errors occur that are not resolved by the design formula.

## 3. Quality Gates Verification

- [ ] **Verify final integrated quality gates**
  - Scope: no code edits; project-wide quality gates
  - Change: Confirm no typecheck, lint, or test regressions have been introduced across the entire repository.
  - Done when:
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest` exits 0.
    - `uv run --project agent ruff check agent/src` exits 0.
    - `uv run --project agent mypy agent/src` exits 0.
  - Stop and hand off if:
    - any regression is found in files untouched by this change.

