## 1. Pre-flight and Backups

- [ ] 1.1 **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates that later tasks require.
  - Done when:
    - `.ralph/baselines/test.txt` and `.ralph/baselines/typecheck.txt` exist with full command outputs
    - Every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: Any gate command is nondeterministic, or capturing fails after retrying.

- [ ] 1.2 **Create backups of files to be modified**
  - Scope: `.backup/` directory
  - Change: Back up `src/app/cad-viewer-3d/page.tsx`, `agent/src/ifc_builder.py`, and `agent/src/agent.py` to `.backup/`.
  - Done when:
    - Directory `.backup/` exists and contains copies of the three files
    - `diff src/app/cad-viewer-3d/page.tsx .backup/page.tsx` exits 0 (representing backup identity check)
  - Stop and hand off if: Any copy command fails with permission or disk space issues.

## 2. Client-side Parser Upgrades

- [ ] 2.1 **Implement B-Rep parsing in parseIfcToDxf**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: Add parsing support for `IFCFACETEDBREP` and `IFCCLOSEDSHELL` entities in `parseIfcToDxf`.
  - Done when:
    - Parser correctly processes `IFCFACETEDBREP` referencing `IFCCLOSEDSHELL` and lists of `IFCPOLYLOOP` entities.
    - `npx tsc --noEmit` exits 0 (representing successful compilation)
  - Stop and hand off if: B-Rep parsing algorithm is ambiguous or conflicts with existing swept solid parsing structures.

- [ ] 2.2 **Implement arbitrary closed profile parsing**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: Add support for `IFCARBITRARYCLOSEDPROFILEDEF` linked to `IFCCOMPOSITECURVE` segments to construct the polygon loops.
  - Done when:
    - Parser processes arbitrary profiles, projections, and extrusions correctly.
    - `npx tsc --noEmit` exits 0
  - Stop and hand off if: The curve segment parsing logic does not close or fails to find referenced polyline vertices.

- [ ] 2.3 **Implement recursive placement transformation**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: Recursively traverse nested `IFCLOCALPLACEMENT` parent lines (`PlacementRelTo`) and compile absolute translation and rotation matrices for transforming vertices.
  - Done when:
    - Coordinates of members inside assemblies are correctly transformed into global coordinates rather than discarding parent coordinates.
    - `npx tsc --noEmit` exits 0
  - Stop and hand off if: Infinite placement recursion is detected or matrix multiplication logic is mathematically undefined.

## 3. Backend spatial structure and formatting upgrades

- [ ] 3.1 **Aggregate members inside IfcElementAssembly**
  - Scope: `agent/src/ifc_builder.py`
  - Change: Group `IfcMember` elements inside `IfcElementAssembly` containers (typed as `.TRUSS.` and assembly place `.FACTORY.`) and link them using `IfcRelAggregates`.
  - Done when:
    - `pytest test/test_ifc_builder.py` exits 0
    - Visual inspection of generated IFC content shows `IFCELEMENTASSEMBLY` containing members.
  - Stop and hand off if: Assembly structure breaks existing standard container specifications.

- [ ] 3.2 **Format member Name and Description metadata**
  - Scope: `agent/src/ifc_builder.py`
  - Change: Format member Name as `"T<index>"` and Description as `"Grade ThicknessxWidth"` (e.g. `"C24 45x120"`) in generated `IfcMember` instances.
  - Done when:
    - Generated member elements carry correct name and description attributes.
    - `pytest test/test_ifc_builder.py` exits 0
  - Stop and hand off if: String formatting rules are ambiguous or fail to match Pamir import specs.

- [ ] 3.3 **Output support proxies and attach custom pricing property sets**
  - Scope: `agent/src/ifc_builder.py`
  - Change: Generate `IfcBuildingElementProxy` support points at wall bearings and attach the custom pricing property sets (`Pamir Frame`, `Pamir Support`, `Pamir Member`) containing weight, connector type, and site-fixed status.
  - Done when:
    - Generated files contain proxies and custom property set associations.
    - `pytest test/test_ifc_builder.py` exits 0
  - Stop and hand off if: Property set creation parameters do not match standard types.

## 4. Pricing formula calibration

- [ ] 4.1 **Calibrate backend pricing formula coefficients**
  - Scope: `agent/src/agent.py`
  - Change: Update `generate_quote` to use updated timber volumetric pricing, Gusset plate pricing, assembly margins, and custom `metalworkCost` calculations (based on support bracket counts).
  - Done when:
    - `generate_quote` outputs correct deterministic pricing matching the new formula.
    - `pytest test/` exits 0
  - Stop and hand off if: Formula outputs disagree with known base cases.

## 5. Verification and Quality Gates

- [ ] 5.1 **Write unit tests for Pamir IFC pricing and assembly structures**
  - Scope: `test/test_pamir_ifc_pricing.py` (Must be placed in root `test/` folder)
  - Change: Create a test file verifying the correct nesting of assembly components, metadata descriptions, custom property sets, and pricing output calculations.
  - Done when:
    - `pytest test/test_pamir_ifc_pricing.py` exits 0
  - Stop and hand off if: Tests fail or conflict with main generator logic.

- [ ] 5.2 **Verify full project quality gates**
  - Scope: whole project
  - Change: Run the full test suites and linter.
  - Done when:
    - `pytest` exits 0
    - `npx tsc --noEmit` exits 0
  - Stop and hand off if: Any regression failures occur.

- [ ] 5.3 **Create bridging summary documentation**
  - Scope: `ralph-docs/PAMIR_IFC_BRIDGING_SUMMARY.md` (Must be placed in root `ralph-docs/` folder)
  - Change: Write a markdown summary outlining the implemented B-Rep parsing, coordinate transform, assembly nesting, custom property sets, and calibrated pricing rules.
  - Done when:
    - `ralph-docs/PAMIR_IFC_BRIDGING_SUMMARY.md` exists and contains detailed change logs and validation steps.
  - Stop and hand off if: Documentation placement rules are violated.
