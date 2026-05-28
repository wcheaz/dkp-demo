## Context

The project is a roof truss design demo where an AI agent collects building parameters, generates DXF files via `agent/src/dxf_builder.py`, and stores the result as base64 in `DesignEntry.dxfContent`. The frontend (`src/components/design-component.tsx`) currently renders completed designs as static `<img>` tags.

Phase 4a (completed) installed `@mlightcad/cad-simple-viewer@1.4.13`, copied Web Worker files to `public/workers/`, and configured `next.config.ts` with `turbopack.resolveAlias` for SSR safety. The viewer library is a framework-agnostic TypeScript package that renders DXF via Three.js/WebGL in the browser.

The viewer is a singleton — `AcApDocManager.createInstance()` must be called once with an HTML container element, worker URLs, and optional dimensions. DXF content is loaded via `docManager.openDocument(fileName, content, options)` where content is an `ArrayBuffer`. Cleanup is via `docManager.destroy()`.

Key constraint: `@mlightcad/cad-simple-viewer` has no React-specific integration. The package exports core classes (`AcApDocManager`, `AcApContext`, `AcApOpenCmd`) that must be orchestrated manually. There is no official React example — only a vanilla JS example repo that no longer exists at the documented URL.

## Goals / Non-Goals

**Goals:**
- Provide an interactive DXF viewer (pan, zoom, layer toggling) embedded in the design card
- Gracefully handle mount/unmount lifecycle without WebGL context leaks
- Fall back to the existing static `<img>` for entries without DXF content
- Provide a DXF download button for entries with DXF content
- Show a generation status indicator while DXF is being prepared

**Non-Goals:**
- Editing DXF entities in the viewer (read-only display only)
- Layer control UI panel (the viewer supports it internally but we don't need to expose a custom panel)
- Offline HTML export button (evaluated later in Phase 5)
- Multiple simultaneous viewer instances (one viewer per design card, mounted when visible)
- Changing the DXF generation pipeline or `dxfContent` data format

## Decisions

### D1: Dynamic import with `useEffect` instead of `next/dynamic`

**Decision:** Use `useEffect`-based dynamic `import('@mlightcad/cad-simple-viewer')` inside the component rather than wrapping the entire component with `next/dynamic({ ssr: false })`.

**Rationale:** The `AcApDocManager` singleton pattern means we need fine-grained control over when initialization happens relative to the container div being in the DOM. A `next/dynamic` wrapper handles code splitting but does not guarantee the container ref is available when the module loads. Using `useEffect` ensures: (1) the container div exists, (2) the import is client-only, (3) we can sequence init → mount → load DXF.

**Alternative considered:** `next/dynamic({ ssr: false })` wrapping the component. Simpler but less control over the initialization sequence, and the parent (`DesignComponent`) already needs conditional rendering logic for DXF vs non-DXF entries.

### D2: Singleton viewer — create on first mount, reuse across re-renders

**Decision:** Call `AcApDocManager.createInstance()` once on the first mount. On subsequent prop changes (e.g., different `dxfContent`), call `openDocument()` again with the new content. On unmount, call `destroy()`.

**Rationale:** The library enforces a singleton pattern. Creating a new instance every time would conflict with the internal singleton check. The `openDocument` API is designed to replace the current document, so re-loading is the correct approach.

**Failure mode:** If `createInstance` is called when an instance already exists, it may return `undefined`. The component must check for this and fall back to `AcApDocManager.instance` if needed.

### D3: Base64 decode to ArrayBuffer for `openDocument`

**Decision:** Decode the base64 `dxfContent` string to a `Uint8Array` using `atob()` + `Uint8Array`, then pass the underlying `ArrayBuffer` to `docManager.openDocument('design.dxf', arrayBuffer, options)`.

**Rationale:** The `openDocument` API requires an `ArrayBuffer`. The `dxfContent` field is a plain base64 string (no data URI prefix, as specified in the `design-entry-model` spec). The file extension in the `fileName` parameter determines the parser used — `.dxf` triggers the DXF parser.

### D4: DXF download via Blob URL

**Decision:** Create a Blob from the decoded `Uint8Array` with MIME type `application/dxf`, generate a URL via `URL.createObjectURL()`, and set it as the `href` of an `<a>` element with the `download` attribute. Revoke the URL on cleanup.

**Rationale:** Standard browser download pattern. No server round-trip needed — the content is already in memory as base64. The `download` attribute triggers a file save dialog.

### D5: Generation status indicator shares existing processing pattern

**Decision:** Show a "Generating CAD drawing..." overlay identical to the existing processing spinner (same CSS classes, same animation) for entries with `status: "complete"` but no `dxfContent`. This is a brief visual state between design completion and DXF generation completing.

**Rationale:** Reuses existing UI patterns. No new visual components needed. The state is transient — once `dxfContent` arrives, the viewer renders.

### D6: Conditional rendering — DXF viewer only when `dxfContent` is present

**Decision:** In `DesignComponent`, the rendering priority for a completed entry with all parameters filled is:
1. If `entry.dxfContent` is a non-empty string → render `<CadViewer>`
2. Otherwise → render existing `<img>` (unchanged behavior)

**Rationale:** Not all completed designs will have DXF content immediately. The conditional ensures backward compatibility — the existing flow works unchanged until DXF content arrives. This also handles the case where DXF generation fails silently.

## Risks / Trade-offs

- **[WebGL context limits]** Browsers limit simultaneous WebGL contexts (typically 8-16). If many design cards have DXF content, mounting viewers for all of them could exceed this limit. → Mitigation: Only mount the viewer for the most recently completed design entry. For older entries, show a static image or a "Click to view" button that mounts the viewer on demand. For the demo (typically 1-3 designs), this is unlikely to be an issue.

- **[Viewer initialization latency]** The first `AcApDocManager.createInstance()` loads Three.js and initializes WebGL, which can take 500ms-2s on slower devices. → Mitigation: Show the generation status indicator during this window. The viewer auto-zooms to fit after loading.

- **[Memory on unmount]** If `destroy()` is not called, WebGL contexts leak. → Mitigation: The `useEffect` cleanup function MUST call `destroy()`. Add a console warning in development if cleanup is skipped.

- **[Large DXF base64 in state]** Base64-encoded DXF content stored inline in React state increases memory usage. → Mitigation: Acceptable for a demo. A production app would use URL-based loading instead. Our DXF files are small (generated from simple geometry).

- **[No official React example]** The cad-simple-viewer library has no React wrapper documentation. → Mitigation: The API surface is well-typed (TypeScript declarations available). The initialization sequence is: `createInstance({ container, webworkerFileUrls })` → `openDocument(name, buffer, opts)`. Unmount: `destroy()`. This is straightforward to wrap in `useEffect`.
