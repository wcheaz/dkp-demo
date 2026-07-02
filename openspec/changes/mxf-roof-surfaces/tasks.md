## 1. Pre-flight and Baselines

- [ ] 1.1 **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `openspec/changes/mxf-roof-surfaces/.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `openspec/changes/mxf-roof-surfaces/.ralph/baselines/mxf-roof-surfaces-test.txt` exists with test output
    - the captured gate file ends with a literal `EXIT=0` or `EXIT=1` line
    - `openspec/changes/mxf-roof-surfaces/.ralph/baselines/mxf-roof-surfaces-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Core Geometry and XML Builder Implementation

- [ ] 2.1 **Implement overhang parsing and helper in geometry solver**
  - Scope: `agent/src/geometry_solver.py`
  - Change: Expose parsed numeric values for overhang parameter matching raw numbers, "mm", or "m" units.
  - Done when:
    - A new test verifying overhang parser functionality runs successfully
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py` exits 0 (or matches pre-flight baseline)
  - Stop and hand off if: modifying `geometry_solver.py` breaks existing imports/tests for DXF or IFC generation.

- [ ] 2.2 **Generate roof and floor surfaces in mxf builder**
  - Scope: `agent/src/mxf_builder.py`
  - Change: Add `<RoofList>`, `<FloorList>`, and `<SurfaceList>` nodes into the output XML mapping Gable, Hip, and Flat roof structures and building floors.
  - Done when:
    - The output XML contains the requested nodes when `roofType`, `roofPitch`, and `overhang` are provided
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py` exits 0
  - Stop and hand off if: XML namespace definitions cause import errors or schema validation warnings.

## 3. Test Validation and Quality Gates

- [ ] 3.1 **Implement unit test scenarios for roof and floor surfaces**
  - Scope: `test/test_mxf_builder.py`
  - Change: Add unit tests verifying exact coordinate coordinates for Gable, Hip, and Flat roof styles based on the mathematical models defined in specification.
  - Done when:
    - All tests in `test/test_mxf_builder.py` and `test/test_mxf_endpoint.py` pass cleanly
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_endpoint.py` exits 0
  - Stop and hand off if: calculated coordinates fail to match specifications due to precision discrepancies.
