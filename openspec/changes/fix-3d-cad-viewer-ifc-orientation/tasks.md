## 1. Quality Gate Baseline

- [x] 1.1 **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-lint.txt` exists with full output from `npm run lint`
    - the captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/fix-3d-cad-viewer-ifc-orientation-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: the lint command is nondeterministic across two runs, or the captured baseline file is missing the `EXIT=<integer>` final line after retrying.

## 2. Geometry Mapping and Coordinate Transformation

- [x] 2.1 **Parse relative placements and retrieve Cartesian points**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: The parser links each `IfcExtrudedAreaSolid` to its parent product and retrieves the `IfcLocalPlacement` (Axis2Placement3D) location and direction vectors.
  - Done when:
    - `findProductLocalPlacementId` successfully resolves parent product placements.
    - `resolvePlacement3D` successfully parses `location`, `axis`, and `refDir` values from `IFCAXIS2PLACEMENT3D` entities.
    - `npm run lint` output for `src/app/cad-viewer-3d/page.tsx` matches the pre-flight baseline with no new errors.
  - Stop and hand off if: `IFCAXIS2PLACEMENT3D` entity structures in the test IFC files deviate from standard coordinate/direction mappings.

- [x] 2.2 **Calculate 3D orthonormal bases and transform vertices**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: Vertices for both the start and end of the extruded solid are mapped using the calculated orthonormal basis and translation offsets before projection.
  - Done when:
    - `getOrthonormalBasis` implements orthogonal projection of `RefDirection` onto `Axis` and normalizes all vectors correctly.
    - `parseIfcToDxf` applies the orthonormal basis to transform profile corner points to global 3D space.
    - `npm run lint` output for `src/app/cad-viewer-3d/page.tsx` matches the pre-flight baseline with no new errors.
  - Stop and hand off if: any vector math results in division by zero or NaN values during projection.

## 3. Verification and Handoff

- [x] 3.1 **Verify correctly oriented IFC previews and check DXF regression**
  - Scope: `src/app/cad-viewer-3d/page.tsx`
  - Change: The isolated `/cad-viewer-3d` page renders the sloped rafters and walls of uploaded IFC files correctly, and DXF previews remain functional.
  - Done when:
    - Uploading `gable.ifc` or `mono-pitch.ifc` to `/cad-viewer-3d` renders sloped rafters and correctly positioned walls.
    - Uploading `gable.dxf` or `mono-pitch.dxf` to `/cad-viewer-3d` renders correctly (no regressions).
    - `npm run lint` exits with no new failures in `src/app/cad-viewer-3d/page.tsx` compared to the baseline.
  - Stop and hand off if: DXF file uploads fail to render or throw parsing errors.
