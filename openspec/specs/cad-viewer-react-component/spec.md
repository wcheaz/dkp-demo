## Purpose

The CAD Viewer React Component provides a client-side React component that renders DXF drawings using the `@mlightcad/cad-simple-viewer` library within a Next.js application.

## Requirements

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

### Requirement: CadViewer accepts className prop for styling

The `CadViewer` component SHALL accept an optional `className?: string` prop and apply it to the outermost container `<div>`. When not provided, the container SHALL have a default class that sets a minimum height and width.

#### Scenario: Custom className applied to container
- **WHEN** `<CadViewer dxfContent="..." className="my-custom-class" />` is rendered
- **THEN** the container div SHALL have `className="my-custom-class"`

#### Scenario: Default styling when no className provided
- **WHEN** `<CadViewer dxfContent="..." />` is rendered without className
- **THEN** the container div SHALL have a default class providing a visible rendering area

### Requirement: CadViewer shows error state on load failure

If `openDocument` returns `false` or throws an error, the component SHALL display an error message ("Failed to load CAD drawing") in place of the viewer. The component SHALL NOT crash or leave a blank area.

#### Scenario: Invalid DXF content shows error
- **WHEN** `<CadViewer dxfContent="aW52YWxpZCBkYXRh" />` is mounted with base64 content that is not valid DXF
- **THEN** the component SHALL render an error message "Failed to load CAD drawing" in the container area
- **AND** `AcApDocManager.destroy()` SHALL still be callable on unmount

#### Scenario: Network error during worker loading shows error
- **WHEN** the Web Worker files fail to load (e.g., 404 on `/workers/*.js`)
- **THEN** the component SHALL catch the error and display "Failed to load CAD drawing"
- **AND** the component SHALL NOT throw an unhandled error

### Requirement: CadViewer is never server-side rendered

The component file SHALL use `"use client"` directive. The component SHALL only execute dynamic import of `@mlightcad/cad-simple-viewer` inside `useEffect`, which never runs on the server. The parent component (`DesignComponent`) SHALL wrap `<CadViewer>` in a client-side-only boundary so that no Three.js or WebGL code runs during SSR.

#### Scenario: CadViewer does not execute during SSR
- **WHEN** the page is server-side rendered
- **THEN** `import('@mlightcad/cad-simple-viewer')` SHALL NOT be called
- **AND** no WebGL or Three.js code SHALL execute on the server

### Requirement: CadViewer auto-zooms to fit content on load

After successfully loading DXF content via `openDocument`, the viewer SHALL automatically zoom to fit the entire drawing within the container. The user SHALL NOT need to manually zoom out to see the full design.

#### Scenario: Drawing is fully visible after load
- **WHEN** a valid DXF with entities at coordinates (0,0) to (15000,10000) is loaded
- **THEN** the viewer SHALL auto-zoom so that the entire drawing from (0,0) to (15000,10000) is visible within the container
