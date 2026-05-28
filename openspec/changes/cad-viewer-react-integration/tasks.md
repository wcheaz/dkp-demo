## 1. CadViewer React Wrapper Component

- [ ] 1.1 Create `src/components/cad-viewer.tsx` with `"use client"` directive. Export a `CadViewer` component accepting props `dxfContent: string` and optional `className?: string`. Render a container `<div ref={containerRef}>`. In `useEffect`, dynamically `import('@mlightcad/cad-simple-viewer')`, call `AcApDocManager.createInstance({ container: containerRef.current, webworkerFileUrls: { dxfParser: '/workers/libredwg-parser-worker.js', mtextRender: '/workers/mtext-renderer-worker.js' } })`. On cleanup, call `AcApDocManager.instance.destroy()`. If container ref is null, skip initialization. Component must handle the case where `createInstance` returns `undefined` (already initialized) by falling back to `AcApDocManager.instance`.
  - **Done when:** Component file exists at `src/components/cad-viewer.tsx`, `pnpm build` succeeds, and importing the component does not trigger SSR-side Three.js execution.
  - **Stop and hand off if:** `AcApDocManager.createInstance` throws or returns `undefined` even on first call — the library singleton API may have changed between versions.

- [ ] 1.2 Add DXF content loading to the `useEffect` in `cad-viewer.tsx`. After successful `createInstance`, decode `dxfContent` from base64 to `ArrayBuffer` using `atob()` + char-code loop into `Uint8Array`. Call `docManager.openDocument('design.dxf', arrayBuffer, {})`. If `openDocument` returns `false` or throws, set an error state and render "Failed to load CAD drawing" in the container area instead of the canvas.
  - **Done when:** Mounting `<CadViewer dxfContent="<valid-base64-dxf>" />` in a browser renders the DXF drawing in the container div. Mounting with invalid base64 shows "Failed to load CAD drawing". Unmounting calls `destroy()` without errors.
  - **Stop and hand off if:** `openDocument` consistently returns `false` with valid DXF content — the `AcApOpenDatabaseOptions` parameter may need a `fontLoader` callback (check `AcDbOpenDatabaseOptions` type definition in `node_modules/@mlightcad/cad-simple-viewer/lib/app/AcDbOpenDatabaseOptions.d.ts`).

## 2. Design Card Integration

- [ ] 2.1 Update `src/components/design-component.tsx` to conditionally render `<CadViewer>` for completed entries with `dxfContent`. Import `CadViewer` via `next/dynamic({ ssr: false })`. In the rendering logic for completed entries with all parameters filled, add a branch: if `entry.dxfContent` is a non-empty string, render the dynamic `CadViewer` with `dxfContent={entry.dxfContent}` and `className="w-[55%] h-[27vh]"`. Otherwise, render the existing `<img>` as before. Entries in `"processing"` status or with incomplete parameters remain unchanged.
  - **Done when:** A completed design entry with `dxfContent` renders the interactive DXF viewer. A completed entry without `dxfContent` still renders the `<img>`. `pnpm build` succeeds.
  - **Verify by:** Running `pnpm dev`, navigating to the app, and confirming a design card with `dxfContent` shows the viewer while one without shows the image.

- [ ] 2.2 Add "Download DXF" button in `src/components/design-component.tsx` for entries with `dxfContent`. Render an `<a>` element with `download={`design-${entry.id}.dxf`}` below the `<CadViewer>`. Create a Blob URL from the decoded base64 content (MIME `application/dxf`) using `URL.createObjectURL()`. Use `useMemo` to create the URL and revoke it when the entry changes or the component unmounts. Style the button consistently with existing card elements.
  - **Done when:** A design entry with `dxfContent` shows a clickable "Download DXF" button. Clicking it downloads a file named `design-1.dxf` (or appropriate ID). Entries without `dxfContent` do not show the button.
  - **Verify by:** Inspecting the DOM for the `<a download>` element, clicking it, and confirming the downloaded file opens in a text editor with valid DXF content.

- [ ] 2.3 Add "Generating CAD drawing..." status indicator in `src/components/design-component.tsx`. For completed entries with all parameters filled but `dxfContent` undefined/null/empty, render a small spinner and text below the existing `<img>`. Use the same spinner animation classes as the processing overlay. The indicator SHALL disappear when `dxfContent` becomes available.
  - **Done when:** A completed design entry without `dxfContent` shows the image plus a "Generating CAD drawing..." indicator below it. Once `dxfContent` arrives, the indicator disappears and the viewer renders.
  - **Verify by:** Creating a design entry without `dxfContent`, observing the indicator, then setting `dxfContent` and confirming the indicator is gone.

## 3. Build Verification

- [ ] 3.1 Run `pnpm build` to verify the entire application builds without errors. Confirm no Three.js, WebGL, `fs`, or `path` module errors appear in the build output. Run `pnpm dev` and verify the dev server starts without build errors. Open the browser and confirm no console errors related to Web Workers (404s on `/workers/*.js`) or WebGL initialization.
  - **Done when:** `pnpm build` exits zero, `pnpm dev` starts cleanly, and the browser console shows no errors related to the CAD viewer integration.
  - **Stop and hand off if:** Build fails with module resolution errors for `@mlightcad/cad-simple-viewer` or its transitive deps — the `turbopack.resolveAlias` in `next.config.ts` may need additional entries.
