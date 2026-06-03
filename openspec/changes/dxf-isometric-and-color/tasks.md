## 1. Quality Gate Baselines

- [ ] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `openspec/changes/dxf-isometric-and-color/.ralph/baselines/`
  - Change: Capture current state of all test runs before modifications.
  - Done when:
    - Directory `openspec/changes/dxf-isometric-and-color/.ralph/baselines/` exists
    - Running `pytest test/test_dxf_builder.py > openspec/changes/dxf-isometric-and-color/.ralph/baselines/dxf-isometric-and-color-pytest.txt; echo "EXIT=$?" >> openspec/changes/dxf-isometric-and-color/.ralph/baselines/dxf-isometric-and-color-pytest.txt` completes and writes the log
    - File `openspec/changes/dxf-isometric-and-color/.ralph/baselines/dxf-isometric-and-color-pytest.txt` ends with a literal `EXIT=0` line
    - `openspec/changes/dxf-isometric-and-color/.ralph/baselines/dxf-isometric-and-color-readme.md` exists listing all tests as passing at baseline
  - Stop and hand off if: the baseline test run returns any failures or the output file is missing `EXIT=0`.

## 2. ACI Color Configuration

- [ ] **Configure ACI colors on layers**
  - Scope: `agent/src/dxf_builder.py`
  - Change: Layer creation calls set the `.color` property on layers in addition to `.rgb` properties, matching standard color indices.
  - Done when:
    - `rg "color =" agent/src/dxf_builder.py` returns matches mapping ACI indices for `Floor_Plan` (9), `Wall_Centerlines` (3), `Roof_Outline` (4), `Trusses` (34), `Dimensions` (5), `Labels` (2), `Lumber_Specs` (6)
    - `pytest test/test_dxf_builder.py` exits 0
  - Stop and hand off if: setting `layer.color` raises an exception or does not map correctly to the index.

## 3. Floor Plan and Centerlines Projection

- [ ] **Implement isometric projection for walls and centerlines**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: Implement `_to_iso` helper in `dxf_builder.py` and apply it to `_draw_floor_plan` and `_draw_wall_centerlines`. Update floor plan unit tests to verify the new projected 2D isometric coordinates.
  - Done when:
    - `rg "def _to_iso" agent/src/dxf_builder.py` returns matches
    - `rg "test_isometric" test/test_dxf_builder.py` returns matches checking the projected floor plan coordinates
    - `pytest test/test_dxf_builder.py -k TestFloorPlanOutline` exits 0
  - Stop and hand off if: math calculations in unit tests mismatch due to floating-point rounding errors.

## 4. Roof Outline Projection

- [ ] **Implement isometric projection for roof outline**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: Apply `_to_iso` to all roof outline drawing functions. Update outline unit tests to assert the projected 2D coordinates.
  - Done when:
    - `Roof_Outline` layer contains only 2D entities at projected coordinates
    - `pytest test/test_dxf_builder.py -k "TestGableRoof or TestHipRoof or TestMonoPitchRoof or TestFlatRoof"` exits 0
  - Stop and hand off if: lines do not intersect at the projected ridge endpoints.

## 5. Trusses and Dimensions Projection

- [ ] **Implement isometric projection for trusses, dimensions, and labels**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: Apply `_to_iso` to truss cross-sections and dimension offsets.
  - Done when:
    - `Trusses`, `Dimensions`, `Labels`, and `Lumber_Specs` layers contain only projected 2D coordinates
    - `pytest test/test_dxf_builder.py -k "TestTrussCrossSection or TestDimensionEntities"` exits 0
  - Stop and hand off if: dimension blocks do not align with the projected endpoints.

## 6. Integrated Quality Gates

- [ ] **Perform final integrated quality gates verification**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: All unit tests updated and verified to pass with the new projected coordinate system.
  - Done when:
    - `pytest test/test_dxf_builder.py` exits 0 with all tests passing
  - Stop and hand off if: any test fails or is nondeterministic.
