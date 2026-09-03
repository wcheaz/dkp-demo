## 1. Quality Gate Baselines

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under [.ralph/baselines/](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/)
  - Change: Capture current state of testing, linting, and typechecking gates.
  - Done when:
    - [gable-roof-generation-fixes-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/gable-roof-generation-fixes-test.txt) exists and contains full command output of tests
    - [gable-roof-generation-fixes-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/gable-roof-generation-fixes-lint.txt) exists and contains full command output of linting
    - [gable-roof-generation-fixes-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/gable-roof-generation-fixes-typecheck.txt) exists and contains full command output of typechecking
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - [gable-roof-generation-fixes-readme.md](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/gable-roof-generation-fixes-readme.md) lists passing/failing gates, exit codes, and exact failing identifiers
    - `[ -f .ralph/baselines/gable-roof-generation-fixes-lint.txt ] && [ -f .ralph/baselines/gable-roof-generation-fixes-typecheck.txt ] && [ -f .ralph/baselines/gable-roof-generation-fixes-test.txt ] && [ -f .ralph/baselines/gable-roof-generation-fixes-readme.md ]` exits 0
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Geometry Solver Refactoring

- [x] **Consolidate structural truss geometry calculations in geometry_solver.py**
  - Scope: [geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py), [ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py)
  - Change: Consolidate truss, web, joint, and support node geometry calculations into a unified module/class.
  - Done when:
    - `rg "class GeometrySolver" agent/src/geometry_solver.py` exits 0
    - `uv run --project agent ruff check agent/src/geometry_solver.py agent/src/ifc_builder.py` exits 0
    - `uv run --project agent mypy agent/src/geometry_solver.py agent/src/ifc_builder.py` exits 0
    - Baseline classification: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - `rg "GeometrySolver" agent/src/ifc_builder.py` exits 0
  - Stop and hand off if: existing geometry calculations in [ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py) cannot be consolidated without breaking dependencies not mentioned in [design.md](file:///home/ncheaz/git/dkp-demo/openspec/changes/gable-roof-generation-fixes/design.md).

- [x] **Implement full-span truss geometry calculations for gable roofs**
  - Scope: [geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py), [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py), [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)
  - Change: Gable roof type generates standard full-span trusses (spanning from wall-to-wall) instead of split half-spans.
  - Done when:
    - `uv run --project agent ruff check agent/src/geometry_solver.py agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
    - `uv run --project agent mypy agent/src/geometry_solver.py agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
    - Baseline classification: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k "test_gable"` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - a new test `test_gable_full_span` (or matching `test_gable`) verifying full-span chord coordinates (single bottom chord and two sloping top chords meeting at the ridge) for gable roofs is added to [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py) and passes under `pytest`
    - `rg "def test_gable" test/test_mxf_builder.py` exits 0
  - Stop and hand off if: design parameters for support conditions of full-span trusses are missing or contradict building layout rules in [design.md](file:///home/ncheaz/git/dkp-demo/openspec/changes/gable-roof-generation-fixes/design.md).

## 3. Advanced Truss Features

- [x] **Implement transport height splitting for tall trusses**
  - Scope: [geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py), [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)
  - Change: Automatically split trusses exceeding 3.3m in height into two horizontal parts (base frame and cap frame).
  - Done when:
    - `uv run --project agent ruff check agent/src/geometry_solver.py test/test_mxf_builder.py` exits 0
    - `uv run --project agent mypy agent/src/geometry_solver.py test/test_mxf_builder.py` exits 0
    - Baseline classification: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k "test_truss_transport"` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - a new test `test_truss_transport_height_splitting` verifying that trusses with total height > 3.3m generate Part 1 (Base, height <= 2.8m) and Part 2 (Cap) with horizontal splice chords is added to [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py) and passes under `pytest`
    - `rg "def test_truss_transport_height_splitting" test/test_mxf_builder.py` exits 0
  - Stop and hand off if: [design.md](file:///home/ncheaz/git/dkp-demo/openspec/changes/gable-roof-generation-fixes/design.md) is ambiguous on whether/how the splitting height of 2.8m or maximum transport height of 3.3m can be configured or overridden.

- [x] **Integrate gable-end panel frames**
  - Scope: [geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py), [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py), [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)
  - Change: The first and last trusses in the layout sequence are designated as `GableEnd` family panels with vertical studs.
  - Done when:
    - `uv run --project agent ruff check agent/src/geometry_solver.py agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
    - `uv run --project agent mypy agent/src/geometry_solver.py agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
    - Baseline classification: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k "test_gable_end"` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - a new test `test_gable_end` (or matching `test_gable_end`) verifying that outer frames have family set to "GableEnd", type "PanelFrame", and vertical studs spaced at 600mm is added to [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py) and passes under `pytest`
    - `rg "def test_gable_end" test/test_mxf_builder.py` exits 0
  - Stop and hand off if: spacing requirements for gable-end vertical studs are missing or contradict configuration options in [design.md](file:///home/ncheaz/git/dkp-demo/openspec/changes/gable-roof-generation-fixes/design.md).

- [x] **Implement roof slope bracing and purlins**
  - Scope: [geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py), [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py), [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)
  - Change: Generate engineered braces (purlins and diagonal bracing) running along the roof slope.
  - Done when:
    - `uv run --project agent ruff check agent/src/geometry_solver.py agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
    - `uv run --project agent mypy agent/src/geometry_solver.py agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
    - Baseline classification: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k "test_sloped_bracing"` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - a new test `test_sloped_bracing` (or matching `test_sloped_bracing`) verifying that `<EngineeredBrace>` elements contain purlins spaced at 1m intervals along top chords and diagonal braces at 45 degrees is added to [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py) and passes under `pytest`
    - `rg "def test_sloped_bracing" test/test_mxf_builder.py` exits 0
  - Stop and hand off if: [design.md](file:///home/ncheaz/git/dkp-demo/openspec/changes/gable-roof-generation-fixes/design.md) or building specs do not specify the structural bracing pattern required for flat or extremely low-pitch roofs.

## 4. API and Integration

- [x] **Export complete structural framing in MXF payload**
  - Scope: [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py), [main.py](file:///home/ncheaz/git/dkp-demo/agent/src/main.py), [test_mxf_endpoint.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_endpoint.py)
  - Change: REST API `/api/mxf/generate` includes `<BuildingFrameList>` and `<FrameList>` with all member, plate, and brace definitions in the returned MXF.
  - Done when:
    - `uv run --project agent ruff check agent/src/mxf_builder.py agent/src/main.py test/test_mxf_endpoint.py` exits 0
    - `uv run --project agent mypy agent/src/mxf_builder.py agent/src/main.py test/test_mxf_endpoint.py` exits 0
    - Baseline classification: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_endpoint.py` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - a test in [test_mxf_endpoint.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_endpoint.py) verifying that `/api/mxf/generate` returns XML containing `<FrameList>` and `<BuildingFrameList>` tags is added/updated and passes under `pytest`
  - Stop and hand off if: the REST API contract or XML response schema for `/api/mxf/generate` is modified in a way not documented in [design.md](file:///home/ncheaz/git/dkp-demo/openspec/changes/gable-roof-generation-fixes/design.md).

- [x] **Align IFC builder with the unified geometry solver**
  - Scope: [ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py), [test_ifc_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_ifc_builder.py)
  - Change: IFC generator outputs match the newly updated geometry solver layout.
  - Done when:
    - `uv run --project agent ruff check agent/src/ifc_builder.py test/test_ifc_builder.py` exits 0
    - `uv run --project agent mypy agent/src/ifc_builder.py test/test_ifc_builder.py` exits 0
    - Baseline classification: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - the tests in [test_ifc_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_ifc_builder.py) pass under `pytest`, verifying congruent 3D model generation based on updated [geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py) calculations
  - Stop and hand off if: `ifc_builder.py` geometry changes require modifications to the IFC export schema that are not specified in [design.md](file:///home/ncheaz/git/dkp-demo/openspec/changes/gable-roof-generation-fixes/design.md).

- [x] **Align DXF builder with the unified geometry solver**
  - Scope: [dxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/dxf_builder.py), [test_dxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_dxf_builder.py)
  - Change: Update `dxf_builder.py` to use the unified `GeometrySolver` calculations so that generated DXF coordinates match the updated structural solver exactly.
  - Done when:
    - `uv run --project agent ruff check agent/src/dxf_builder.py test/test_dxf_builder.py` exits 0
    - `uv run --project agent mypy agent/src/dxf_builder.py test/test_dxf_builder.py` exits 0
    - Baseline classification: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_dxf_builder.py` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - the tests in [test_dxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_dxf_builder.py) pass under `pytest`, verifying congruent 2D CAD layout generation based on updated [geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py) calculations
  - Stop and hand off if: DXF representation of advanced truss elements (splitting, bracing) cannot be rendered using simple line elements or is not supported by `ezdxf`.

## 5. MXF Import and Transport Splitting Fixes

- [x] **Generate `<TimberSectionList>` in the MXF builder**
  - Scope: [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py), [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)
  - Change: MXF builder generates `<TimberSectionList>` containing valid C24 timber sections to resolve member ID references.
  - Done when:
    - `rg "TimberSectionList" agent/src/mxf_builder.py` exits 0
    - `uv run --project agent ruff check agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
    - `uv run --project agent mypy agent/src/mxf_builder.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_gable_timber_and_plate_lists` exits 0
  - Stop and hand off if: standard timber IDs are not defined in `design.md` or need dynamic parameterization.

- [x] **Generate `<PlateTypeList>` in the MXF builder**
  - Scope: [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py), [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)
  - Change: MXF builder generates `<PlateTypeList>` containing valid M20/M14 connector plates to resolve plate ID references, along with `<PlateTypeQuantityList>` inside the `<Job>`.
  - Done when:
    - `rg "PlateTypeList" agent/src/mxf_builder.py` exits 0
    - `uv run --project agent ruff check agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
    - `uv run --project agent mypy agent/src/mxf_builder.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_gable_timber_and_plate_lists` exits 0
  - Stop and hand off if: standard plate IDs are not defined in `design.md` or need dynamic parameterization.

- [x] **Integrate transport-height splitting into the MXF builder**
  - Scope: [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py), [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)
  - Change: The MXF builder calls `solver.mxf_truss_parts(overhang_m)` to output split frames (with Part 1 base and Part 2 cap elements) instead of `mxf_truss_frames()` when the ridge height exceeds 3.3m.
  - Done when:
    - `rg "mxf_truss_parts" agent/src/mxf_builder.py` exits 0
    - `rg "def test_mxf_builder_splits_tall_truss_in_xml" test/test_mxf_builder.py` exits 0
    - `uv run --project agent ruff check agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
    - `uv run --project agent mypy agent/src/mxf_builder.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_mxf_builder_splits_tall_truss_in_xml` exits 0
  - Stop and hand off if: the geometry solver's split parts are incompatible with the MXF frame XML generator.

## 6. Final Quality Gates

- [x] **Run final integrated quality gates**
  - Scope: [.ralph/baselines/](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/), [agent/src/](file:///home/ncheaz/git/dkp-demo/agent/src/), [test/](file:///home/ncheaz/git/dkp-demo/test/)
  - Change: All tests, linting, and typechecking run clean or match pre-flight baselines across the whole repository.
  - Done when:
    - Baseline classification: `uv run --project agent ruff check agent/src` exits 0, or failures match the baseline in `.ralph/baselines/gable-roof-generation-fixes-lint.txt`
    - Baseline classification: `uv run --project agent mypy agent/src` exits 0, or failures match the baseline in `.ralph/baselines/gable-roof-generation-fixes-typecheck.txt`
    - Baseline classification: `PYTHONPATH=agent/src:agent uv run --project agent pytest` exits 0, or failures match the baseline in `.ralph/baselines/gable-roof-generation-fixes-test.txt`
  - Stop and hand off if: any unexpected test regression is introduced in unrelated modules.


