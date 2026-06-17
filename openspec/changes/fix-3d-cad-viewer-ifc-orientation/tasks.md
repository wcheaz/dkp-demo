## 1. Quality Gate Baseline

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-eslint.txt` exists with full output from `npx eslint src/app/cad-viewer-3d/page.tsx`
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-typecheck.txt` exists with full output from `npx tsc --noEmit`
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-test.txt` exists with full output from `node scripts/test-ifc-parser.js`
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if:
    - any gate command is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Geometry Mapping and Coordinate Transformation

- [x] **Parse relative placements and retrieve Cartesian points**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: The parser traces solid geometry references to parent products and extracts product local placements (location, axis, and ref direction).
  - Done when:
    - `findProductLocalPlacementId` and `resolvePlacement3D` helper functions are defined at the module scope of `src/app/cad-viewer-3d/page.tsx` (outside the `parseIfcToDxf` function, between the `MAX_FILE_SIZE_BYTES` and `CadViewer3DPage` markers).
    - `node scripts/test-ifc-parser.js` exits 0 and prints `SUCCESS: resolvePlacement3D basic tests passed.`
    - `npx eslint src/app/cad-viewer-3d/page.tsx` exits 0; baseline failures are not allowed for this task
  - Stop and hand off if:
    - `IFCAXIS2PLACEMENT3D` entity structures in the test IFC files deviate from standard coordinate/direction mappings.

- [x] **Transform profile vertices to global 3D space**
  - Scope: `src/app/cad-viewer-3d/page.tsx`, `scripts/test-ifc-parser.js`
  - Change: The parser calculates the 3D orthonormal basis for both the solid and the product local placements, maps profile vertices to global 3D space (writing actual 3D coordinates to the DXF output instead of performing a 2D projection), and the test script verifies that the output DXF contains non-zero Z components.
  - Done when:
    - `getOrthonormalBasis` helper function is defined at the module scope of `src/app/cad-viewer-3d/page.tsx` (outside the `parseIfcToDxf` function, between the `MAX_FILE_SIZE_BYTES` and `CadViewer3DPage` markers).
    - `scripts/test-ifc-parser.js` contains assertions to parse the DXF output and validate that at least one coordinate has a non-zero Z component.
    - `node scripts/test-ifc-parser.js` exits 0 and prints both `SUCCESS: getOrthonormalBasis math tests passed.` and `SUCCESS: Output DXF contains true 3D coordinates.`
    - `npx eslint src/app/cad-viewer-3d/page.tsx` exits 0; baseline failures are not allowed for this task
  - Stop and hand off if:
    - standard default axes or mathematical formulas for orthonormal basis reconstruction are ambiguous or conflict with the IFC/STEP specification.

## 3. Final Quality Gates and Integration

- [ ] **Verify repository integration build and quality gates**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: Ensure the updated 3D CAD viewer code compiles and lints cleanly at the repository integration level.
  - Done when:
    - `node scripts/test-ifc-parser.js` exits 0; baseline failures are not allowed for this task
    - `npx eslint src/app/cad-viewer-3d/page.tsx` exits 0; baseline failures are not allowed for this task
    - `npx tsc --noEmit` exits 0; baseline failures are not allowed for this task
  - Stop and hand off if:
    - TypeScript or ESLint compilation errors occur in unrelated files outside `src/app/cad-viewer-3d/` that prevent project compilation.

---

### Manual Verification Instructions (Non-Checkbox)
To be performed after the automated task list successfully completes:
1. Navigate to `/cad-viewer-3d` in the local development environment.
2. Upload `gable.ifc` or `mono-pitch.ifc` and confirm that rafters are rendered at their correct angles (sloped) and walls are positioned correctly.
3. Upload `gable.dxf` and confirm that the DXF model displays correctly without regressions.
