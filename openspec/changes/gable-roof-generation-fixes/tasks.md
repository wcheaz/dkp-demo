## 1. Quality Gate Baselines

- [ ] 1.1 **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `openspec/changes/gable-roof-generation-fixes/.ralph/baselines/`
  - Change: Capture current state of testing, linting, and typechecking gates.
  - Done when:
    - `openspec/changes/gable-roof-generation-fixes/.ralph/baselines/test.txt` exists and contains exit code of tests
    - `openspec/changes/gable-roof-generation-fixes/.ralph/baselines/lint.txt` exists and contains exit code of linting
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `openspec/changes/gable-roof-generation-fixes/.ralph/baselines/gable-roof-generation-fixes-readme.md` lists all gates
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Geometry Solver Refactoring

- [ ] 2.1 **Consolidate structural truss geometry calculations in `geometry_solver.py`**
  - Scope: `agent/src/geometry_solver.py`, `test/test_mxf_builder.py`
  - Change: Consolidate truss, web, joint, and support node geometry calculations into a unified module/class.
  - Done when:
    - Unit tests in `test/test_mxf_builder.py` pass or fail with baseline match
    - `PYTHONPATH=agent/src:agent uv run pytest test/test_mxf_builder.py` exits 0 or matches baseline
  - Stop and hand off if: `geometry_solver.py` has syntax errors or compilation failures.

- [ ] 2.2 **Implement full-span truss generation for gable roofs**
  - Scope: `agent/src/geometry_solver.py`, `agent/src/mxf_builder.py`
  - Change: Gable roof type generates standard full-span trusses (spanning from wall-to-wall) instead of split half-spans.
  - Done when:
    - Invoking geometry solver with gable parameters produces a single bottom chord spanning 10.0m (plus overhangs) and two sloping top chords meeting at the ridge.
    - target tests in `test/test_mxf_builder.py` verify full-span coords
  - Stop and hand off if: solver cannot resolve support conditions.

## 3. Advanced Truss Features

- [ ] 3.1 **Implement transport height checking and caps splitting**
  - Scope: `agent/src/geometry_solver.py`
  - Change: Automatically split trusses exceeding 3.3m in height into two horizontal parts (base frame and cap frame).
  - Done when:
    - Trusses with total height > 3.3m generate Part 1 (Base, height <= 2.8m) and Part 2 (Cap).
    - Unit test proving splitting logic passes
  - Stop and hand off if: maximum height is not configurable.

- [ ] 3.2 **Integrate gable-end panel frames**
  - Scope: `agent/src/geometry_solver.py`, `agent/src/mxf_builder.py`
  - Change: The first and last trusses in the layout sequence are designated as `GableEnd` family panels with vertical studs.
  - Done when:
    - The outer frames at Y = first and last coordinates have family set to "GableEnd" and type "PanelFrame" in generated MXF.
  - Stop and hand off if: spacing is not 600mm.

- [ ] 3.3 **Implement top-chord sloped bracing and purlins**
  - Scope: `agent/src/geometry_solver.py`, `agent/src/mxf_builder.py`
  - Change: Generate engineered braces (purlins and diagonal bracing) running along the roof slope.
  - Done when:
    - `<EngineeredBrace>` elements in generated MXF contain purlins spaced at 1m intervals along top chords and diagonal braces at 45 degrees.
  - Stop and hand off if: roof pitch is $0^{\circ}$ (flat).

## 4. API and IFC Integration

- [ ] 4.1 **Export complete structural framing in MXF payload**
  - Scope: `agent/src/mxf_builder.py`, `agent/src/main.py`, `test/test_mxf_endpoint.py`
  - Change: REST API `/api/mxf/generate` includes `<BuildingFrameList>` and `<FrameList>` with all member, plate, and brace definitions in the returned MXF.
  - Done when:
    - Testing route `/api/mxf/generate` returns XML containing `<FrameList>` and `<BuildingFrameList>` tags.
    - `PYTHONPATH=agent/src:agent uv run pytest test/test_mxf_endpoint.py` exits 0
  - Stop and hand off if: endpoint returns malformed XML.

- [ ] 4.2 **Align IFC builder with the unified geometry solver**
  - Scope: `agent/src/ifc_builder.py`, `test/test_ifc_builder.py`
  - Change: IFC generator outputs match the newly updated geometry solver layout.
  - Done when:
    - `PYTHONPATH=agent/src:agent uv run pytest test/test_ifc_builder.py` exits 0
  - Stop and hand off if: `ifc_builder.py` fails to compile due to missing solver imports.
