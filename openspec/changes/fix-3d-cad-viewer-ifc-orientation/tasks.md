## 1. Quality Gate Baseline

- [ ] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-eslint.txt` exists with full output from `npx eslint src/app/cad-viewer-3d/page.tsx`
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-typecheck.txt` exists with full output from `npx tsc --noEmit`
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-test.txt` exists with full output from `node scripts/test-ifc-parser.js`
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: any gate command is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Geometry Mapping and Coordinate Transformation

- [ ] **Parse relative placements and retrieve Cartesian points**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: The parser traces solid geometry references to parent products and extracts product local placements (location, axis, and ref direction).
  - Done when:
    - `findProductLocalPlacementId` and `resolvePlacement3D` helper functions are defined in the module scope of `src/app/cad-viewer-3d/page.tsx` (between the `MAX_FILE_SIZE_BYTES` and `CadViewer3DPage` markers).
    - `node scripts/test-ifc-parser.js` exits 0 and prints `SUCCESS: resolvePlacement3D basic tests passed.`
    - `npx eslint src/app/cad-viewer-3d/page.tsx` exits 0.
  - Stop and hand off if: `IFCAXIS2PLACEMENT3D` entity structures in the test IFC files deviate from standard coordinate/direction mappings.

- [ ] **Calculate 3D orthonormal bases and transform vertices**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: The parser calculates the 3D orthonormal basis for both the solid and the product local placements, and maps profile vertices to global 3D space.
  - Done when:
    - `getOrthonormalBasis` helper function is defined in the module scope of `src/app/cad-viewer-3d/page.tsx` (between the `MAX_FILE_SIZE_BYTES` and `CadViewer3DPage` markers).
    - `node scripts/test-ifc-parser.js` exits 0 and prints `SUCCESS: getOrthonormalBasis math tests passed.`
    - `npx eslint src/app/cad-viewer-3d/page.tsx` exits 0.
  - Stop and hand off if: any vector math results in division by zero or NaN values during projection.

## 3. Final Quality Gates and Integration

- [ ] **Verify integration build and lint gates**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: Ensure the updated 3D CAD viewer parses correctly, compiles cleanly, and satisfies type checking.
  - Done when:
    - `node scripts/test-ifc-parser.js` exits 0 and prints `SUCCESS: Parsed IFC to DXF successfully.`
    - `npx eslint src/app/cad-viewer-3d/page.tsx` exits 0.
    - `npx tsc --noEmit` exits 0.
  - Stop and hand off if: TypeScript compilation yields new errors in `src/app/cad-viewer-3d/` code.

---

### Manual Verification Instructions (Non-Checkbox)
To be performed after the automated task list successfully completes:
1. Navigate to `/cad-viewer-3d` in the local development environment.
2. Upload `gable.ifc` or `mono-pitch.ifc` and confirm that rafters are rendered at their correct angles (sloped) and walls are positioned correctly.
3. Upload `gable.dxf` and confirm that the DXF model displays correctly without regressions.
