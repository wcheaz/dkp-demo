## Why

The current main page displays roof truss drawings in 2D using a flat CAD viewer. To allow users to verify the detailed 3D structure, spacing, and annotations of the generated roof trusses, we need to integrate an interactive 3D WebGL-based viewer with orbit/pan/zoom camera controls, projection toggles, and view presets.

## What Changes

- Replace the 2D `CadViewer` with the 3D-only `CadViewer3D` viewer inside the main page's fullscreen workspace container (`src/components/design-component.tsx`).
- Dynamically import the `CadViewer3D` component to prevent server-side rendering (SSR) hydration errors.
- Support interactive camera controls (left-click to orbit, right-click to pan, mouse wheel to zoom) in fullscreen.
- Support switching camera projection modes (Perspective vs. Orthographic) and viewport presets (Top, Front, Side, Isometric).
- Maintain translations for Slovak and English across the fullscreen modal controls and headers.

### Non-Goals
- Adding a 2D/3D toggle inside the inline card previews on the design list (keeping cards 2D-only for speed).
- Supporting direct IFC/ICF file uploads or conversions on the main page flow (maintaining existing DXF backend integration).
- Modifying the core Three.js parser or three-dxf-loader engine.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `cad-viewer-fullscreen`: Maximized fullscreen workspace renders the design drawing in 3D using `CadViewer3D` instead of a 2D viewer, providing interactive orbiting, panning, zooming, projection toggling, and viewport presets, while retaining existing multi-language header and exit triggers.

## Impact

- `src/components/design-component.tsx`: Fullscreen modal container rendering logic.
- `src/i18n/language-provider.tsx`: Added Slovak/English translations for 3D viewer control buttons and labels if not already present.
- `src/components/cad-viewer-3d.tsx`: Reused as the core 3D rendering component.
