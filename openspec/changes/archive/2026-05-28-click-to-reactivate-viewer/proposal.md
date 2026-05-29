## Why

Only one live `CadViewer` instance can exist at a time due to the `AcApDocManager` singleton. When multiple designs have DXF content, only the latest renders live — older designs show a blank placeholder because screenshot capture via WebGL has proven unreliable. Users should be able to click any past design to reactivate its live viewer, swapping the active viewer to that design.

## What Changes

- Add user-controllable `activeViewerIndex` state to `DesignComponent`, initialized to the last design with DXF content (current behavior preserved for the newest design).
- Render a clickable overlay on inactive designs that have DXF content, inviting the user to click to view that design live.
- On click, update `activeViewerIndex` to the clicked design, causing React to unmount the current `CadViewer` (destroying the singleton) and mount a new one for the selected design.
- Remove the broken `dxfPreview` / `onCapturePreview` / `captureViewToDataUrl` screenshot infrastructure since it is no longer needed.

## Capabilities

### New Capabilities

- `design-viewer-reactivate`: Click-to-reactivate viewer switching — allows the user to click any design card with DXF content to make it the active live viewer, swapping away from whichever design was previously active.

### Modified Capabilities

- `cad-viewer-react-component`: Remove `onCapturePreview` prop and `captureViewToDataUrl` function; simplify the component to only handle live rendering.
- `design-display`: Replace the static `dxfPreview` fallback image for inactive DXF designs with a clickable overlay that reactivates the viewer.

## Impact

- `src/components/design-component.tsx` — state management for active viewer index, click handler, overlay rendering
- `src/components/cad-viewer.tsx` — remove screenshot capture code and `onCapturePreview` prop
- `src/lib/types.ts` — `dxfPreview` field on `DesignEntry` becomes unused (can be removed or left deprecated)
