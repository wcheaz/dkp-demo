## MODIFIED Requirements

### Requirement: Drag-and-drop or file upload parsing
The viewer page SHALL accept `.dxf` and `.ifc`/`.icf` file uploads via drag-and-drop or a file picker. When a file is received, the client SHALL read its content using the HTML5 `FileReader` API, convert it to a base64 string, and render the interactive viewer component with the loaded data.

#### Scenario: Dropping a DXF file
- **WHEN** a user drops a valid `.dxf` file onto the upload area
- **THEN** the page reads the file, base64-encodes it, and mounts the interactive canvas displaying the DXF.

#### Scenario: Dropping an IFC file on the 3D test viewer
- **WHEN** a user drops a valid `.ifc` or `.icf` file onto the 3D test viewer upload area at `/cad-viewer-3d`
- **THEN** the page reads the file, parses the geometry by applying the `IfcLocalPlacement` and `IfcAxis2Placement3D` coordinate transformations (translation and rotation) for each product, and writes it directly to a true 3D DXF representation to display the correctly oriented 3D structural shape in WebGL.
- **AND** the main viewer page `/cad-viewer` remains unchanged and continues to use its original parsing logic.
- **AND** parsing and rendering of `.dxf` files on both pages remains completely unaffected and functional.
