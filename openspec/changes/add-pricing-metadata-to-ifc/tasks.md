## 1. Pre-flight

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/add-pricing-metadata-to-ifc-pytest.txt` exists with full output
    - `.ralph/baselines/add-pricing-metadata-to-ifc-mypy.txt` exists with full output
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/add-pricing-metadata-to-ifc-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Implementation

- [ ] **Classify timber members and associate pricing property sets in generated IFC output**
  - Scope: `agent/src/ifc_builder.py`
  - Change: Sets the `ObjectType` attribute of all generated `IfcMember` elements according to their structural role (`"TOP_CHORD"`, `"BOTTOM_CHORD"`, `"WEB"`, `"PLATE"`), creates an `IfcPropertySet` containing `Grade="C24"` and `IsTreated=True`, and associates it with the members using `IfcRelDefinesByProperties`.
  - Done when:
    - `agent/src/ifc_builder.py` contains assignments setting the `ObjectType` attribute on created `IfcMember` elements
    - `agent/src/ifc_builder.py` contains code creating `IfcPropertySet` and `IfcRelDefinesByProperties`
    - `PYTHONPATH=agent/src:agent uv run --project agent python -c "import ifcopenshell, ifc_builder, types; p = types.SimpleNamespace(floorPlanDimensions='10x15m', roofType='Flat'); m = ifcopenshell.file.from_string(ifc_builder.build_ifc(p).decode('utf-8')); assert any(mb.ObjectType in ['TOP_CHORD', 'BOTTOM_CHORD', 'WEB', 'PLATE'] for mb in m.by_type('IfcMember')); assert len(m.by_type('IfcPropertySet')) >= 1; assert len(m.by_type('IfcRelDefinesByProperties')) >= 1"` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` exits 0 with all 26 tests passing
    - `uv run --project agent mypy agent/src/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if:
    - `ifcopenshell` fails with entity creation errors, or there is ambiguity in how property sets are defined or structured in IFC2x3.

- [ ] **Add unit tests verifying member role ObjectType and property sets in generated IFC output**
  - Scope: `test/test_ifc_builder.py`
  - Change: Adds test assertions to verify that all generated `IfcMember` elements have their `ObjectType` set to structural role strings, and that they are correctly linked to a property set defining `Grade` and `IsTreated` properties.
  - Done when:
    - `test/test_ifc_builder.py` contains assertions verifying `ObjectType` values and `IfcPropertySet` relationships on `IfcMember` elements
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py -k test_timber_member_pricing_metadata` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` exits 0 with all 27 tests passing
    - `uv run --project agent mypy agent/src/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if:
    - parsing the generated IFC string in the test file fails, or test utility functions lack necessary support for checking property relationships.
