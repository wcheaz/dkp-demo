## ADDED Requirements

### Requirement: CAD test viewer route
The system SHALL expose an isolated client-side page at the route `/cad-viewer`. This page MUST NOT execute server-side rendering logic and must be imported dynamically with SSR disabled.

#### Scenario: Navigating to CAD viewer
- **WHEN** a user visits `/cad-viewer`
- **THEN** the browser renders a clean, dark-themed page layout containing a drag-and-drop file upload zone and no compilation/SSR errors are raised.

### Requirement: Drag-and-drop or file upload parsing
The viewer page SHALL accept `.dxf` file uploads via drag-and-drop or a file picker. When a file is received, the client SHALL read its content using the HTML5 `FileReader` API, convert it to a base64 string, and render the interactive `<CadViewer>` component with the loaded data.

#### Scenario: Dropping a DXF file
- **WHEN** a user drops a valid `.dxf` file onto the upload area
- **THEN** the page reads the file, base64-encodes it, and mounts the interactive `<CadViewer>` canvas displaying the DXF.

### Requirement: Viewer reset control
The page SHALL display a prominent reset or "Clear" button when a DXF file is active, which resets the client state and returns the user to the upload/drop zone.

#### Scenario: Resetting the viewer
- **WHEN** a user clicks the "Clear" button while viewing a DXF
- **THEN** the canvas is destroyed, state is cleared, and the page displays the drag-and-drop upload zone.
