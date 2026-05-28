## 1. Pre-flight baseline

- [ ] **Pre-flight: record `pnpm build` baseline**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current `pnpm build` output so later tasks can classify build failures against a known baseline.
  - Done when:
    - `.ralph/baselines/cad-viewer-react-integration-build.txt` exists with full build output
    - captured file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/cad-viewer-react-integration-readme.md` lists exit code and any errors
  - Stop and hand off if: `pnpm build` is nondeterministic across two runs, or the captured file is missing the `EXIT=` final line after retry.

## 2. CadViewer React wrapper component

- [ ] **Create CadViewer component shell with dynamic import and lifecycle cleanup**
  - Scope: `src/components/cad-viewer.tsx`
  - Change: New `"use client"` component file exports `CadViewer` accepting props `dxfContent: string` and optional `className?: string`. Renders a container `<div ref={containerRef}>`. In `useEffect`, dynamically imports `@mlightcad/cad-simple-viewer`, calls `AcApDocManager.createInstance({ container: containerRef.current, webworkerFileUrls: { dxfParser: '/workers/libredwg-parser-worker.js', mtextRender: '/workers/mtext-renderer-worker.js' } })`. Falls back to `AcApDocManager.instance` if `createInstance` returns `undefined` (already initialized). Cleanup calls `AcApDocManager.instance.destroy()`. Skips initialization if container ref is null.
  - Done when:
    - `src/components/cad-viewer.tsx` exists and exports a named `CadViewer` component
    - `rg "use client" src/components/cad-viewer.tsx` returns a match
    - `pnpm build` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - build output contains no Three.js, WebGL, `fs`, or `path` module errors
  - Stop and hand off if: `AcApDocManager.createInstance` throws or returns `undefined` even on first call — the library singleton API may have changed between versions.

- [ ] **Add DXF content loading and error handling to CadViewer**
  - Scope: `src/components/cad-viewer.tsx`
  - Change: After successful `createInstance`, the `useEffect` decodes `dxfContent` from base64 to `ArrayBuffer` using `atob()` + char-code loop into `Uint8Array`. Calls `docManager.openDocument('design.dxf', arrayBuffer, {})`. If `openDocument` returns `false` or throws, sets an error state rendering "Failed to load CAD drawing" in the container. Re-calls `openDocument` when `dxfContent` prop changes without re-creating the instance.
  - Done when:
    - `rg "openDocument" src/components/cad-viewer.tsx` returns a match
    - mounting `<CadViewer dxfContent="<valid-base64-dxf>" />` in a browser renders the DXF drawing in the container div with the full drawing visible (auto-zoom-to-fit)
    - mounting with invalid base64 shows "Failed to load CAD drawing" text
    - unmounting calls `destroy()` without console errors
    - `pnpm build` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: `openDocument` consistently returns `false` with valid DXF content — the options parameter may need a `fontLoader` callback (check `AcDbOpenDatabaseOptions` type definition in `node_modules/@mlightcad/cad-simple-viewer`).

## 3. Design card integration

- [ ] **Wire CadViewer into DesignComponent for entries with dxfContent**
  - Scope: `src/components/design-component.tsx`
  - Change: Import `CadViewer` via `next/dynamic({ ssr: false })`. In rendering logic for completed entries with all parameters filled, add a branch: if `entry.dxfContent` is a non-empty string, render the dynamic `CadViewer` with `dxfContent={entry.dxfContent}` and `className="w-[55%] h-[27vh]"`. Otherwise, render the existing `<img>` unchanged. Entries in `"processing"` status or with incomplete parameters remain unchanged.
  - Done when:
    - `rg "CadViewer" src/components/design-component.tsx` returns matches
    - `rg "ssr: false" src/components/design-component.tsx` returns a match
    - a completed design entry with `dxfContent` renders `<CadViewer>` instead of `<img>`
    - a completed entry without `dxfContent` still renders `<img>`
    - `pnpm build` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: `next/dynamic` import of `CadViewer` causes build failures not present in baseline — may need to use `useEffect`-based `import()` directly in the component instead.

- [ ] **Add DXF download button for entries with dxfContent**
  - Scope: `src/components/design-component.tsx`
  - Change: Render an `<a>` element with `download={`design-${entry.id}.dxf`}` below the `<CadViewer>`. Create a Blob URL from the decoded base64 content (MIME `application/dxf`) using `URL.createObjectURL()`. Use `useMemo` to create the URL and revoke it on entry change or unmount. Style consistently with existing card elements.
  - Done when:
    - `rg "application/dxf" src/components/design-component.tsx` returns a match
    - a design entry with `dxfContent` shows a clickable "Download DXF" button
    - entries without `dxfContent` do not show the button
    - clicking the button downloads a file named `design-<id>.dxf` containing valid DXF content
    - `pnpm build` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: Blob URL creation fails in the target browser — may need a data-URI fallback.

- [ ] **Add "Generating CAD drawing..." status indicator**
  - Scope: `src/components/design-component.tsx`
  - Change: For completed entries with all parameters filled but `dxfContent` undefined/null/empty, render a spinner and "Generating CAD drawing..." text below the existing `<img>`. Use the same spinner animation classes as the processing overlay. Indicator disappears when `dxfContent` becomes available.
  - Done when:
    - `rg "Generating CAD drawing" src/components/design-component.tsx` returns a match
    - a completed entry without `dxfContent` shows the indicator below the image
    - once `dxfContent` arrives, the indicator is no longer visible
    - `pnpm build` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: the indicator interferes with existing processing spinner styling — may need to differentiate the CSS classes.

## 4. Integrated build verification

- [ ] **Verify full application builds and dev server starts cleanly**
  - Scope: no code edits; verification only
  - Change: No code changes. Confirms the integrated application builds and runs without errors introduced by this change.
  - Done when:
    - `pnpm build` exits 0
    - `pnpm dev` starts without build errors
    - browser console shows no errors related to Web Workers (404s on `/workers/*.js`) or WebGL initialization
  - Stop and hand off if: build fails with module resolution errors for `@mlightcad/cad-simple-viewer` or its transitive deps — the `turbopack.resolveAlias` in `next.config.ts` may need additional entries.
