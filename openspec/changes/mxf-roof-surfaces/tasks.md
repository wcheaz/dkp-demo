## 1. Pre-flight and Baselines

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `[.ralph/baselines/](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/)`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `[.ralph/baselines/mxf-roof-surfaces-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-roof-surfaces-lint.txt)`, `[.ralph/baselines/mxf-roof-surfaces-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-roof-surfaces-typecheck.txt)`, and `[.ralph/baselines/mxf-roof-surfaces-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-roof-surfaces-test.txt)` exist with full command outputs
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `[.ralph/baselines/mxf-roof-surfaces-readme.md](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-roof-surfaces-readme.md)` lists passing/failing gates, exit codes, and exact failing identifiers
    - `[ -f .ralph/baselines/mxf-roof-surfaces-lint.txt ] && [ -f .ralph/baselines/mxf-roof-surfaces-typecheck.txt ] && [ -f .ralph/baselines/mxf-roof-surfaces-test.txt ] && [ -f .ralph/baselines/mxf-roof-surfaces-readme.md ]` exits 0
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Core Geometry and XML Builder Implementation

- [x] **Implement overhang parsing helper in geometry solver**
  - Scope: `[geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py)`, `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)`
  - Change: Expose parsed numeric values for overhang parameter matching raw numbers, "mm", or "m" units in millimetres.
  - Done when:
    - `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)` defines unit tests for overhang parsing (e.g. `test_overhang_parsing`)
    - `uv run --project agent ruff check agent/src/geometry_solver.py` exits 0
    - `uv run --project agent mypy agent/src/geometry_solver.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_overhang_parsing` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: modifying `geometry_solver.py` breaks existing imports/tests for DXF or IFC generation, or overhang parsing rules cannot be reconciled with design.md.

- [x] **Generate Flat roof and floor surfaces**
  - Scope: `[mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py)`, `[geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py)`, `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)`
  - Change: Add `<RoofList>`, `<FloorList>`, and `<SurfaceList>` nodes into the output XML mapping Flat roof structures and building floors with exact 3D coordinates.
  - Done when:
    - `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)` defines unit tests for Flat roof coordinate calculations (e.g. `test_flat_roof_generation`)
    - `uv run --project agent ruff check agent/src/mxf_builder.py agent/src/geometry_solver.py` exits 0
    - `uv run --project agent mypy agent/src/mxf_builder.py agent/src/geometry_solver.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_flat` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: XML namespace definitions cause import errors or schema validation warnings, or geometry calculation formulas in design.md result in self-intersecting polygons.

- [x] **Generate Mono-pitch roof surfaces**
  - Scope: `[mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py)`, `[geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py)`, `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)`
  - Change: Add `<RoofList>` and `<SurfaceList>` nodes into the output XML mapping Mono-pitch roof structures with exact 3D coordinates.
  - Done when:
    - `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)` defines unit tests for Mono-pitch roof coordinate calculations (e.g. `test_monopitch_roof_generation`)
    - `uv run --project agent ruff check agent/src/mxf_builder.py agent/src/geometry_solver.py` exits 0
    - `uv run --project agent mypy agent/src/mxf_builder.py agent/src/geometry_solver.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_mono` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: calculated coordinates fail to match specifications due to precision discrepancies or slope run calculation logic is undefined.

- [x] **Generate Gable roof surfaces**
  - Scope: `[mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py)`, `[geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py)`, `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)`
  - Change: Add `<RoofList>` and `<SurfaceList>` nodes into the output XML mapping Gable roof structures with exact 3D coordinates.
  - Done when:
    - `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)` defines unit tests for Gable roof coordinate calculations (e.g. `test_gable_roof_generation`)
    - `uv run --project agent ruff check agent/src/mxf_builder.py agent/src/geometry_solver.py` exits 0
    - `uv run --project agent mypy agent/src/mxf_builder.py agent/src/geometry_solver.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_gable` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: calculated coordinates fail due to precision discrepancies, or Gable roof peak logic violates the geometry formulas.

- [ ] **Generate Hip roof surfaces**
  - Scope: `[mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py)`, `[geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py)`, `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)`
  - Change: Add `<RoofList>` and `<SurfaceList>` nodes into the output XML mapping Hip roof structures with exact 3D coordinates.
  - Done when:
    - `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)` defines unit tests for Hip roof coordinate calculations (e.g. `test_hip_roof_generation`)
    - `uv run --project agent ruff check agent/src/mxf_builder.py agent/src/geometry_solver.py` exits 0
    - `uv run --project agent mypy agent/src/mxf_builder.py agent/src/geometry_solver.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_hip` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: calculated coordinates fail to match specifications, or Hip roof ridge span calculation logic is undefined for non-rectangular aspects.

## 3. Test Validation and Quality Gates

- [ ] **Integrate roof/floor surface parameters into layout generation endpoint**
  - Scope: `[main.py](file:///home/ncheaz/git/dkp-demo/agent/src/main.py)`, `[test_mxf_endpoint.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_endpoint.py)`
  - Change: Support `roofType`, `roofPitch`, and `overhang` parameters in the `/api/mxf/generate` POST request body and return layouts with generated surfaces.
  - Done when:
    - `[test_mxf_endpoint.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_endpoint.py)` verifies that `/api/mxf/generate` processes requests with `roofType`, `roofPitch`, and `overhang` and returns the expected surface XML nodes
    - `uv run --project agent ruff check agent/src/main.py` exits 0
    - `uv run --project agent mypy agent/src/main.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_endpoint.py` exits 0; baseline failures are not allowed for this task
  - Stop and hand off if: endpoint fails to parse request body or serialize generated surfaces into the final response payload.

## 4. Quality Gates Verification

- [ ] **Verify final integrated quality gates**
  - Scope: no code edits; project-wide quality gates
  - Change: Confirm no typecheck, lint, or test regressions have been introduced across the entire repository.
  - Done when:
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest` exits 0, or failures match the baseline in `[.ralph/baselines/mxf-roof-surfaces-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-roof-surfaces-test.txt)` with no new failures.
    - `uv run --project agent ruff check agent/src` exits 0
    - `uv run --project agent mypy agent/src` exits 0
  - Stop and hand off if: any regression is found in files untouched by this change.
