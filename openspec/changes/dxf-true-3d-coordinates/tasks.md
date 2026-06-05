## 1. Setup and Pre-flight

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/dxf-true-3d-coordinates-test.txt` exists with full output from `pytest`
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/dxf-true-3d-coordinates-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Core Transition

- [ ] **Transition DXF coordinate generation and unit tests to true 3D**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: Remove `_to_iso` projection helper and replace it with direct true 3D `(x, y, z)` coordinates for floor plans, roof outlines, and trusses in `dxf_builder.py`. Place annotations on the flat Z=0 ground plane. Update all coordinate assertions in `test_dxf_builder.py` to match the true 3D coordinates.
  - Done when:
    - `_to_iso` helper function is deleted from `agent/src/dxf_builder.py`
    - `grep "_to_iso" agent/src/dxf_builder.py` returns no matches
    - `pytest test/test_dxf_builder.py` exits 0
    - `pytest test/test_dxf_endpoint.py` exits 0
  - Stop and hand off if: ezdxf entity methods fail to accept 3D coordinates, or tests fail with errors unrelated to coordinate values.
