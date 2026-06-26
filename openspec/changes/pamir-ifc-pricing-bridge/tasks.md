## 1. Pre-flight and Baselines

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `[.ralph/baselines/](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/)`
  - Change: Capture current state of all gates that later tasks require.
  - Done when:
    - `[.ralph/baselines/pamir-ifc-pricing-bridge-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-test.txt)`, `[.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt)`, and `[.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt)` exist with full command outputs
    - Every captured gate file ends with a literal `EXIT=<integer>` line
    - `[.ralph/baselines/pamir-ifc-pricing-bridge-readme.md](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-readme.md)` lists passing/failing gates, exit codes, and exact failing identifiers
    - `[ -f .ralph/baselines/pamir-ifc-pricing-bridge-test.txt ] && [ -f .ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt ] && [ -f .ralph/baselines/pamir-ifc-pricing-bridge-lint.txt ] && [ -f .ralph/baselines/pamir-ifc-pricing-bridge-readme.md ]` exits 0
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Client-side Parser Upgrades

- [x] **Implement B-Rep parsing in parseIfcToDxf**
  - Scope: `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/cad-viewer-3d/page.tsx)`, `[test-ifc-parser.js](file:///home/ncheaz/git/dkp-demo/scripts/test-ifc-parser.js)`
  - Change: Add parsing support for `IFCFACETEDBREP` and `IFCCLOSEDSHELL` entities in `parseIfcToDxf` and add test cases to `test-ifc-parser.js`.
  - Done when:
    - `node scripts/test-ifc-parser.js` exits 0
    - `npx tsc --noEmit` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt)` with no new type-checking errors in `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/cad-viewer-3d/page.tsx)`
    - `npm run lint` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt)` with no new errors in `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/cad-viewer-3d/page.tsx)`
  - Stop and hand off if: B-Rep parsing algorithm is ambiguous or conflicts with existing swept solid parsing structures.

- [ ] **Implement arbitrary closed profile parsing**
  - Scope: `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/cad-viewer-3d/page.tsx)`, `[test-ifc-parser.js](file:///home/ncheaz/git/dkp-demo/scripts/test-ifc-parser.js)`
  - Change: Add support for `IFCARBITRARYCLOSEDPROFILEDEF` linked to `IFCCOMPOSITECURVE` segments to construct polygon loops and add test cases to `test-ifc-parser.js`.
  - Done when:
    - `node scripts/test-ifc-parser.js` exits 0
    - `npx tsc --noEmit` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt)` with no new type-checking errors in `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/cad-viewer-3d/page.tsx)`
    - `npm run lint` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt)` with no new errors in `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/cad-viewer-3d/page.tsx)`
  - Stop and hand off if: The curve segment parsing logic does not close or fails to find referenced polyline vertices.

- [ ] **Implement recursive placement transformation**
  - Scope: `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/cad-viewer-3d/page.tsx)`, `[test-ifc-parser.js](file:///home/ncheaz/git/dkp-demo/scripts/test-ifc-parser.js)`
  - Change: Recursively traverse nested `IFCLOCALPLACEMENT` parent lines (`PlacementRelTo`) to compute absolute translation and rotation matrices for transforming vertices, and add test cases to `test-ifc-parser.js`.
  - Done when:
    - `node scripts/test-ifc-parser.js` exits 0
    - `npx tsc --noEmit` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt)` with no new type-checking errors in `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/cad-viewer-3d/page.tsx)`
    - `npm run lint` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt)` with no new errors in `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/cad-viewer-3d/page.tsx)`
  - Stop and hand off if: Infinite placement recursion is detected or matrix multiplication logic is mathematically undefined.

## 3. Backend spatial structure and formatting upgrades

- [ ] **Aggregate members inside IfcElementAssembly**
  - Scope: `[ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py)`, `[test_ifc_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_ifc_builder.py)`
  - Change: Group `IfcMember` elements inside `IfcElementAssembly` containers (typed as `.TRUSS.` and assembly place `.FACTORY.`), link them using `IfcRelAggregates`, and add unit tests to `test_ifc_builder.py`.
  - Done when:
    - `pytest test/test_ifc_builder.py -k test_ifc_element_assembly_aggregation` exits 0
    - `pytest test/test_ifc_builder.py -k test_write_example_ifc` exits 0
    - `python -c "import ifcopenshell; f=ifcopenshell.open('generated/gable.ifc'); assert len(f.by_type('IfcElementAssembly')) > 0"` exits 0
    - `pytest test/test_ifc_builder.py` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-test.txt)` with no new test failures in `[ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py)`
  - Stop and hand off if: Assembly structure breaks existing standard container specifications.

- [ ] **Format member Name and Description metadata**
  - Scope: `[ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py)`, `[test_ifc_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_ifc_builder.py)`
  - Change: Format member Name as `"T<index>"` and Description as `"Grade ThicknessxWidth"` (e.g. `"C24 45x120"`) in generated `IfcMember` instances, and add unit tests to `test_ifc_builder.py`.
  - Done when:
    - `pytest test/test_ifc_builder.py -k test_member_name_and_description_formatting` exits 0
    - `pytest test/test_ifc_builder.py -k test_write_example_ifc` exits 0
    - `python -c "import ifcopenshell; f=ifcopenshell.open('generated/gable.ifc'); assert any(m.Name.startswith('T') and 'C24' in m.Description for m in f.by_type('IfcMember'))"` exits 0
    - `pytest test/test_ifc_builder.py` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-test.txt)` with no new test failures in `[ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py)`
  - Stop and hand off if: String formatting rules are ambiguous or fail to match Pamir import specs.

- [ ] **Output support proxies and attach custom pricing property sets**
  - Scope: `[ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py)`, `[test_ifc_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_ifc_builder.py)`
  - Change: Generate `IfcBuildingElementProxy` support points at wall bearings, attach custom pricing property sets (`Pamir Frame`, `Pamir Support`, `Pamir Member`), and add unit tests to `test_ifc_builder.py`.
  - Done when:
    - `pytest test/test_ifc_builder.py -k test_support_proxies_and_property_sets` exits 0
    - `pytest test/test_ifc_builder.py -k test_write_example_ifc` exits 0
    - `python -c "import ifcopenshell; f=ifcopenshell.open('generated/gable.ifc'); assert len(f.by_type('IfcBuildingElementProxy')) > 0; psets = {p.Name for p in f.by_type('IfcPropertySet')}; assert {'Pamir Frame', 'Pamir Support', 'Pamir Member'} <= psets"` exits 0
    - `pytest test/test_ifc_builder.py` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-test.txt)` with no new test failures in `[ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py)`
  - Stop and hand off if: Property set creation parameters do not match standard types.

## 4. Pricing formula calibration

- [ ] **Calibrate pricing formula coefficients across backend and frontend**
  - Scope: `[agent.py](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py)`, `[pricing-breakdown-modal.tsx](file:///home/ncheaz/git/dkp-demo/src/components/pricing-breakdown-modal.tsx)`, `[pricing-formula.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/references/pricing-formula.md)`, `[tool-execution-simulation-spec.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/references/tool-execution-simulation-spec.md)`, `[test_pricing.py](file:///home/ncheaz/git/dkp-demo/test/test_pricing.py)`
  - Change: Update `generate_quote` in the backend, the frontend `computePricingBreakdown`, and the agent skill references to use the calibrated Pamir coefficients (timber @ 6200 CZK, brackets @ 370 CZK, updated joints/assembly/hanger costs), and create unit tests in `test_pricing.py`.
  - Done when:
    - `pytest test/test_pricing.py` exits 0
    - `pytest test/` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-test.txt)` with no new test failures in `[agent.py](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py)`
    - `npx tsc --noEmit` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt)` with no new type-checking errors in `[pricing-breakdown-modal.tsx](file:///home/ncheaz/git/dkp-demo/src/components/pricing-breakdown-modal.tsx)`
    - `npm run lint` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt)` with no new errors in `[pricing-breakdown-modal.tsx](file:///home/ncheaz/git/dkp-demo/src/components/pricing-breakdown-modal.tsx)`
  - Stop and hand off if: Calibrated coefficients or bracket count formulas are mathematically contradictory or undefined.

## 5. Verification and Quality Gates

- [ ] **Verify full project quality gates**
  - Scope: whole project
  - Change: Run the full test suites, TypeScript compilation, and linter.
  - Done when:
    - `pytest` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-test.txt)` with no new failures.
    - `npx tsc --noEmit` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-typecheck.txt)` with no new failures.
    - `npm run lint` exits 0, or failures match the baseline in `[.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/pamir-ifc-pricing-bridge-lint.txt)` with no new failures.
  - Stop and hand off if: Any regression failures occur.

- [ ] **Create bridging summary documentation**
  - Scope: `[PAMIR_IFC_BRIDGING_SUMMARY.md](file:///home/ncheaz/git/dkp-demo/docs/PAMIR_IFC_BRIDGING_SUMMARY.md)`
  - Change: Write a markdown summary outlining the implemented B-Rep parsing, coordinate transform, assembly nesting, custom property sets, and calibrated pricing rules.
  - Done when:
    - `[ -f docs/PAMIR_IFC_BRIDGING_SUMMARY.md ]` exits 0
  - Stop and hand off if: The documentation folder is deleted or unwritable.
