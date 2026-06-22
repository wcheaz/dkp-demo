## 1. Pre-flight

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/add-lumber-material-to-ifc-pytest.txt` exists with full output
    - `.ralph/baselines/add-lumber-material-to-ifc-mypy.txt` exists with full output
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/add-lumber-material-to-ifc-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Implementation

- [x] **Associate "Timber - C24" material with generated IfcMember elements**
  - Scope: `agent/src/ifc_builder.py`
  - Change: Creates an `IfcMaterial` representing the lumber material and links it to all generated structural members using `IfcRelAssociatesMaterial`. Adds comments explaining future dynamic configuration.
  - Done when:
    - `agent/src/ifc_builder.py` contains creation code for `IfcMaterial("Timber - C24")`
    - `agent/src/ifc_builder.py` creates `IfcRelAssociatesMaterial` referencing the material and all `IfcMember` elements
    - `PYTHONPATH=agent/src:agent uv run --project agent python -c "import ifcopenshell, ifc_builder, types; p = types.SimpleNamespace(floorPlanDimensions='10x15m', roofType='Flat'); m = ifcopenshell.file.from_string(ifc_builder.build_ifc(p).decode('utf-8')); assert len(m.by_type('IfcMaterial')) >= 1; assert any(mat.Name == 'Timber - C24' for mat in m.by_type('IfcMaterial')); assert len(m.by_type('IfcRelAssociatesMaterial')) >= 1"` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` exits 0 with all 26 tests passing
    - `uv run --project agent mypy agent/src/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if:
    - `ifcopenshell` fails with entity creation errors, or there is ambiguity in how material associations should be structured.

- [x] **Add unit tests verifying material association in generated IFC output**
  - Scope: `test/test_ifc_builder.py`
  - Change: Verifies that the generated IFC model contains the `"Timber - C24"` material and that it is associated with `IfcMember` elements.
  - Done when:
    - `test/test_ifc_builder.py` contains assertions verifying `IfcMaterial` existence and association with `IfcMember`
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py -k test_timber_material_association` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` exits 0 with all 27 tests passing
    - `uv run --project agent mypy agent/src/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if:
    - parsing the generated IFC string in the test file fails, or test utility functions lack necessary support for checking material references.
