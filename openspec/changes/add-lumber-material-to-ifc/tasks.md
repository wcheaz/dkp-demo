## 1. Pre-flight

- [ ] **1.1 Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/add-lumber-material-to-ifc-pytest.txt` exists with full output
    - `.ralph/baselines/add-lumber-material-to-ifc-mypy.txt` exists with full output
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/add-lumber-material-to-ifc-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Implementation

- [ ] **2.1 Associate "Timber - C24" material with generated IfcMember elements**
  - Scope: `agent/src/ifc_builder.py`
  - Change: Creates an `IfcMaterial` representing the lumber material and links it to all generated structural members using `IfcRelAssociatesMaterial`. Adds comments explaining future dynamic configuration.
  - Done when:
    - `agent/src/ifc_builder.py` contains creation code for `IfcMaterial("Timber - C24")`
    - `agent/src/ifc_builder.py` creates `IfcRelAssociatesMaterial` referencing the material and all `IfcMember` elements
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/` runs successfully (121 passed, 3 skipped)
    - `uv run --project agent mypy agent/src/` exits with the same pre-existing error in `dxf_builder.py` and no new errors in `ifc_builder.py`
  - Stop and hand off if: `ifcopenshell` fails with entity creation errors.

- [ ] **2.2 Add unit tests verifying material association in generated IFC output**
  - Scope: `test/test_ifc_builder.py`
  - Change: Verifies that the generated IFC model contains the `"Timber - C24"` material and that it is associated with `IfcMember` elements.
  - Done when:
    - `test/test_ifc_builder.py` contains assertions verifying `IfcMaterial` existence and association with `IfcMember`
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` exits 0 with all test cases passing (including the new ones)
    - `uv run --project agent mypy agent/src/` has no new errors
  - Stop and hand off if: parsing the generated IFC string in the test file fails.
