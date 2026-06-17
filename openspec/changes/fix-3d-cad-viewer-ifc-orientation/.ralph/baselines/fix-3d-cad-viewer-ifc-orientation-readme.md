# Quality Gate Baselines

This document lists the baseline status of quality gates for the `fix-3d-cad-viewer-ifc-orientation` change.

## Baseline Summary

| Gate | Command | Exit Code | Status | Exact Failing Identifiers |
|---|---|---|---|---|
| eslint | `npx eslint src/app/cad-viewer-3d/page.tsx` | 0 | PASSING | none |
| typecheck | `npx tsc --noEmit` | 0 | PASSING | none |
| test | `node scripts/test-ifc-parser.js` | 0 | PASSING | none |

## Notes

- All three required gates pass cleanly at baseline, so later tasks that require these gates to exit 0 have no pre-existing failures to tolerate.
- The `eslint` gate prints no output on success (clean lint), captured in `fix-3d-cad-viewer-ifc-orientation-eslint.txt`.
- The `typecheck` gate prints no output on success (clean compile), captured in `fix-3d-cad-viewer-ifc-orientation-typecheck.txt`.
- The `test` gate prints `SUCCESS: Parsed IFC to DXF successfully.` and `DXF line count: 13458`, captured in `fix-3d-cad-viewer-ifc-orientation-test.txt`.
- A legacy whole-repo `npm run lint` baseline (exit 1, with warnings/errors confined to `public/workers/*` minified bundles) is preserved in `fix-3d-cad-viewer-ifc-orientation-lint.txt`; it is out of scope for this change because its failures live in generated worker bundles, not in `src/app/cad-viewer-3d/`.
