## MODIFIED Requirements

### Requirement: CadViewer component initializes the DXF viewer on mount

A `"use client"` React component SHALL be exported as `CadViewer` from `src/components/cad-viewer.tsx`. It SHALL accept props: `dxfContent: string` (base64-encoded DXF data) and optional `className?: string`. The component SHALL render a container `<div>` with a `ref` for DOM access. The component SHALL NOT accept an `onCapturePreview` prop.

In `useEffect` on mount, the component SHALL:
1. Dynamically `import('@mlightcad/cad-simple-viewer')`
2. Call `AcApDocManager.createInstance({ container: containerRef.current, webworkerFileUrls: { dxfParser: '/workers/libredwg-parser-worker.js', mtextRender: '/workers/mtext-renderer-worker.js' } })`
3. Decode `dxfContent` from base64 to an `ArrayBuffer` using `atob()` + `Uint8Array`
4. Call `docManager.openDocument('design.dxf', arrayBuffer, options)` to load the DXF content
5. The viewer SHALL auto-zoom to fit the content after loading

On unmount (the `useEffect` cleanup), the component SHALL call `docManager.destroy()` to release WebGL resources and remove event listeners.

The component SHALL NOT contain any screenshot capture logic (`captureViewToDataUrl`, `emitPreview`, or WebGL pixel-reading code).

#### Scenario: CadViewer renders and loads DXF content
- **WHEN** `<CadViewer dxfContent="base64encodeddxf..." />` is mounted in the browser with a valid base64 DXF string
- **THEN** the component SHALL render a container div, initialize `AcApDocManager` with the container as the mount point, decode the base64 content, and load it via `openDocument`
- **AND** the DXF drawing SHALL be visible in the container as a 2D rendering

#### Scenario: CadViewer cleans up on unmount
- **WHEN** a `<CadViewer>` component that has successfully initialized is unmounted
- **THEN** `AcApDocManager.instance.destroy()` SHALL be called exactly once
- **AND** no WebGL context or event listeners SHALL remain

#### Scenario: CadViewer handles missing container ref gracefully
- **WHEN** the container ref is `null` when `useEffect` runs
- **THEN** the component SHALL NOT call `AcApDocManager.createInstance()` and SHALL NOT throw an error

## REMOVED Requirements

### Requirement: CadViewer captures preview screenshot on unmount
**Reason**: Screenshot capture via WebGL has proven unreliable across three implementation attempts (preserveDrawingBuffer, WebGLRenderTarget, raw gl.readPixels). Replaced by click-to-reactivate approach where no preview image is needed.
**Migration**: Inactive designs now show a clickable overlay (see `design-viewer-reactivate` capability) instead of a static screenshot. Remove `onCapturePreview` prop, `captureViewToDataUrl` function, and all related screenshot infrastructure from the component.
