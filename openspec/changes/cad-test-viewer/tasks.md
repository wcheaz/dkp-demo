## 1. Quality Gate baselines

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/cad-test-viewer-test.txt` exists with test suite output
    - `.ralph/baselines/cad-test-viewer-lint.txt` exists with eslint output
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/cad-test-viewer-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if:
    - any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line.
    - any command attempts to read or write to `/tmp` (always use the local `./tmp` folder in the project workspace).

## 2. Backend Material Colors

- [x] **Configure layer RGB colors in DXF builder and update tests**
  - Scope: `agent/src/dxf_builder.py`, `test/test_dxf_builder.py`
  - Change: Layer RGB attributes are assigned on layer creation in the DXF builder, and backend unit tests verify these RGB values are correctly embedded in generated files.
  - Done when:
    - `pytest test/test_dxf_builder.py` exits 0 (or failures match the pre-flight baseline with no new failures)
    - `test/test_dxf_builder.py` contains assertions verifying `layer.rgb` equals `(128, 128, 128)` for `Floor_Plan`, `(70, 130, 180)` for `Roof_Outline`, `(139, 90, 43)` for `Trusses`, and `(0, 0, 255)` for `Dimensions`
  - Stop and hand off if: `ezdxf` layer creation fails or does not support the `.rgb` attribute.

## 3. Frontend Test Viewer

- [ ] **Implement `/cad-viewer` page for client-side CAD rendering**
  - Scope: `src/app/cad-viewer/page.tsx`
  - Change: A new isolated route at `/cad-viewer` displays a premium drag-and-drop file upload UI and renders dropped/selected DXF files in the CAD canvas.
  - Done when:
    - `src/app/cad-viewer/page.tsx` exists and uses `next/dynamic` with `ssr: false` to import `CadViewer`
    - `npm run build` exits 0
    - `rg "use client"` returns a match in `src/app/cad-viewer/page.tsx`
  - Stop and hand off if: the dynamically imported `CadViewer` causes webpack build errors or is not resolvable.
