## MODIFIED Requirements

### Requirement: Fullscreen CAD Rendering
The maximized CAD view SHALL occupy the main content area next to the Copilot sidebar. It SHALL render the active design's CAD drawing in 3D using the client-side `CadViewer3D` component based on the DXF content associated with the active design. It SHALL support interactive camera controls (left-click dragging to orbit, right-click dragging to pan, and scrolling to zoom), camera projection switching (Perspective vs. Orthographic), and camera viewport presets (Top (2D), Front, Side, Isometric) with a Reset View recenter capability.

#### Scenario: Fullscreen viewer displays active CAD drawing in 3D
- **WHEN** the user enters fullscreen mode for a design entry
- **THEN** the system SHALL load the design's DXF content, initialize the WebGL scene, adjust the camera position to fit the geometry, and display the interactive viewport control panel with preset buttons

### Requirement: Fullscreen Translation
The fullscreen header title, back button, and 3D viewport control panel labels (including Perspective, Orthographic, Reset View, Top, Front, Side, Isometric, and loading states) SHALL support both English and Slovak languages based on the active locale.

#### Scenario: User switches language in fullscreen mode
- **WHEN** the user toggles the active language to Slovak
- **THEN** the fullscreen header title, back button, and all 3D viewport control panel labels and tooltips SHALL be rendered in Slovak translation
