## 1. Quality Gate Baselines

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `openspec/changes/dxf-pamir-material-integration/.ralph/baselines/`
  - Change: Capture current state of all test runs before modifications.
  - Done when:
    - Directory `openspec/changes/dxf-pamir-material-integration/.ralph/baselines/` exists
    - `openspec/changes/dxf-pamir-material-integration/.ralph/baselines/dxf-pamir-material-integration-pytest.txt` exists with full pytest output and ends with `EXIT=1` (reflecting pre-existing title block failures)
    - `openspec/changes/dxf-pamir-material-integration/.ralph/baselines/dxf-pamir-material-integration-readme.md` exists listing the 12 failed tests (all related to `TestTitleBlock` and `TestRoundTripAllRoofTypes` layer count asserting 5 layers while `Title_Block` is disabled)
  - Stop and hand off if: the test run returns errors outside of `TestTitleBlock` and `TestRoundTripAllRoofTypes` layer count.

## 2. Code Cleanups

- [x] **Align title block tests with disabled status**
  - Scope: `test/test_dxf_builder.py`
  - Change: Skip or update tests that assert on the disabled `Title_Block` layer so that the test suite runs green for base functionality.
  - Done when:
    - `pytest` runs and all tests pass (except for the new capabilities/layers not implemented yet)
    - `pytest` exits 0
  - Stop and hand off if: modifying `test/test_dxf_builder.py` introduces syntax errors or breaks unrelated tests.

## 3. Floor Plan and Centerlines

- [x] **Implement 3D floor plan and Wall_Centerlines layer**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: Floor plan drawn as two closed rectangles at Z=0 and Z=2700 with vertical corner lines. Centerline rectangle drawn at Z=0 on a new `Wall_Centerlines` layer.
  - Done when:
    - `build_dxf` outputs `Floor_Plan` layer with top/bottom 3D rings and vertical connectors
    - `build_dxf` outputs `Wall_Centerlines` layer with a 2D closed centerline polyline
    - `pytest -k TestFloorPlanOutline` exits 0
  - Stop and hand off if: ezdxf does not support 3D coordinates for `add_line` or `add_lwpolyline` raises errors with 3D tuples.

## 4. Roof Outline and Trusses

- [x] **Implement 3D roof outlines and 3D truss placement**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: Roof outlines (ridge, hips, slope lines) and trusses drawn in 3D coordinate space starting at Z=2700 up to Z=2700+ridge_height.
  - Done when:
    - Trusses are drawn as 3D triangles at their respective Z-level (Z=2700) and Y-spacings
    - Roof boundaries converge at 3D ridge coordinates
    - `pytest -k TestGable -k TestHip -k TestMonoPitch -k TestFlat -k TestTruss` exits 0
  - Stop and hand off if: geometry calculations for 3D hip or mono-pitch coordinates result in self-intersecting or out-of-bounds coordinate points.

## 5. Labels and Specifications

- [x] **Separate user labels and add technical Lumber_Specs layer**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: User-facing text annotations (Width, Depth, Height) moved to the `Labels` layer. Technical specs (lumber grade C24, member thickness 45 mm, widths) written as MTEXT on the new `Lumber_Specs` layer.
  - Done when:
    - DXF output has a `Labels` layer with basic labels and a `Lumber_Specs` layer with material specs text
    - `pytest -k TestDimensionEntities` exits 0
  - Stop and hand off if: MTEXT formatting values fail to render in ezdxf or cause font-loading warnings.

## 6. Quality Gates

- [ ] **Perform final integrated quality gates verification**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: Complete test suite runs and exits successfully with all 3D geometry and layer specs passing.
  - Done when:
    - `pytest` exits 0
  - Stop and hand off if: any test fails or is nondeterministic.
