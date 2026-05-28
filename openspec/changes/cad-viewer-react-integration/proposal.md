## Why

The design card currently renders completed designs as a static `<img>` tag pointing to an SVG file. DXF content is generated server-side and stored as base64 in `DesignEntry.dxfContent`, but the user never sees an interactive CAD view — they only see a flat image with no ability to pan, zoom, or toggle layers. Phase 4a installed `@mlightcad/cad-simple-viewer`, copied Web Worker assets, and configured Next.js for SSR safety. This change (Phase 4b) uses that environment to build the React wrapper component and wire it into the design card, replacing the static image with an interactive viewer and adding a DXF download button.

## What Changes

- Create a new `<CadViewer>` React wrapper component (`src/components/cad-viewer.tsx`) that dynamically imports `@mlightcad/cad-simple-viewer`, initializes `AcApDocManager` with worker URLs, mounts the WebGL canvas into a container div, and loads DXF content from a base64-encoded string prop.
- Replace the static `<img>` rendering for completed designs that have `dxfContent` with the new `<CadViewer>` component in `src/components/design-component.tsx`. Entries without `dxfContent` or in `"processing"` status continue to use the existing `<img>` rendering unchanged.
- Add a "Download DXF" button alongside the viewer for entries with `dxfContent`, using a Blob URL from the decoded base64 content.
- Add a "Generating CAD drawing..." status indicator while DXF content is being generated but not yet available.

## Capabilities

### New Capabilities
- `cad-viewer-react-component`: A `"use client"` React component that wraps `@mlightcad/cad-simple-viewer` for browser-based DXF rendering. Accepts `dxfContent` (base64 string) as a prop, initializes the viewer via `AcApDocManager.createInstance()`, loads the DXF via `openDocument()`, and handles mount/unmount lifecycle including WebGL cleanup. Wrapped with `next/dynamic({ ssr: false })`.
- `cad-viewer-design-integration`: Wires the `<CadViewer>` into the existing `DesignComponent` card layout. Completed entries with `dxfContent` render the interactive viewer instead of the static `<img>`. Includes a "Download DXF" button and a generation status indicator.

### Modified Capabilities
- `design-display`: The `DesignComponent` rendering logic for completed entries changes from always rendering `<img>` to conditionally rendering `<CadViewer>` when `entry.dxfContent` is present. Entries without `dxfContent`, in `"processing"` status, or with incomplete parameters continue to use the existing image/placeholder rendering unchanged.

## Impact

- **Frontend components**: New file `src/components/cad-viewer.tsx`; modified file `src/components/design-component.tsx`.
- **Dependencies**: No new npm dependencies — `@mlightcad/cad-simple-viewer` was installed in Phase 4a.
- **Types**: No changes to `DesignEntry` — `dxfContent` field already exists in `src/lib/types.ts`.
- **Build**: No changes to `next.config.ts` — SSR safety was configured in Phase 4a.
- **Static assets**: No new worker files — already copied to `public/workers/` in Phase 4a.
- **No backend changes**: DXF generation and the `dxfContent` field on `DesignEntry` are unchanged.
