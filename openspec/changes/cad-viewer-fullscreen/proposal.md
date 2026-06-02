## Why

The CAD viewer in the design component card layout is currently very small (limited to a height of `27vh` and `55%` width), which makes it difficult to read and inspect detailed truss layouts and annotations. This change introduces a "fullscreen" option to expand the active drawing to fill the entire main content area, improving visibility and analysis.

## What Changes

- **Maximize Button**: Add a magnifying glass button in the top-right corner of the active CAD viewer component card.
- **Main-Content Fullscreen**: Clicking the magnifying glass button expands the CAD viewer to occupy the entire main content area (excluding the Copilot sidebar).
- **Back Button**: Provide a highly visible "Back" button inside the expanded view to return to the standard design flow.
- **No Uploads**: Unlike the standalone `/cad-viewer` route, this maximized view only displays the currently loaded/generated DXF content from the active design and does not permit user file uploads.
- **Internationalization (i18n)**: All new UI strings (such as the back button label) will support both Slovak and English languages via `useTranslations`.

## Non-goals

- Overlaying the Copilot sidebar (the sidebar must remain visible and functional).
- Permitting manual upload or dragging/dropping of other DXF files in this full-screen mode.
- Preserving the maximized fullscreen state across page reloads.

## Capabilities

### New Capabilities
- `cad-viewer-fullscreen`: Renders the active design's DXF content in a maximized view occupying the main content area next to the Copilot sidebar. Includes toggle buttons to enter and exit this mode.

### Modified Capabilities
None.

## Impact

- **`src/components/design-component.tsx`**: Will manage the fullscreen toggle state and render the fullscreen view when active.
- **`src/components/cad-viewer.tsx`**: Will need to handle resizing dynamically when container dimensions change during state transition.
- **Translations (`src/i18n/`)**: Add translation keys for the back button and tooltips.
