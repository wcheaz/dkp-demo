## Context

The backend generates a DXF CAD drawing representing roof truss designs. In previous iterations, coordinates in the DXF file were projected into a 2D isometric representation on the backend using `_to_iso(x, y, z)`. While this allowed a simple 2D viewer to display an isometric view, it prevents the 3D orbit viewer (`CadViewer3D`) from rendering a true 3D model. Orbiting the model in the 3D viewer reveals a flat sheet of paper rather than a volumetric building frame. We will transition the DXF generation to use true 3D (X, Y, Z) coordinates.

## Goals / Non-Goals

**Goals:**
- Eliminate the `_to_iso` isometric projection helper from `dxf_builder.py`.
- Draw all building structural lines (floor plan wall box, roof framing outline, trusses) in actual 3D space.
- Position text labels (e.g. measurements, lumber specifications) at actual 3D locations (using Z=0 ground plane as the default baseline).
- Update the unit test suite in `test_dxf_builder.py` to match the new 3D coordinate assertions.
- Verify that both the frontend 2D viewer (which will render the 3D model as a standard top-down orthographic plan view) and the 3D viewer (which will render a true 3D rotatable wireframe) work correctly.

**Non-Goals:**
- Customizing or configuring `@mlightcad/cad-simple-viewer` (2D viewer) to render isometric projections on the frontend. The default top-down plan view is acceptable and standard for a 2D card list.
- Changing the agent's LLM prompt, since the prompt only dictates the layers, labels, and lack of `DIMENSION` objects, not the math coordinates themselves.

## Decisions

### D1: Use true 3D (X, Y, Z) coordinates in model space
- **Choice**: Modify the drawing functions in `dxf_builder.py` to pass three-dimensional tuple coordinates `(x, y, z)` directly to `msp.add_line(...)` and `msp.add_text(...)` / `msp.add_mtext(...)` instead of projecting them via `_to_iso`.
- **Rationale**: `three-dxf-loader` (underneath the 3D viewer) parses 3D coordinates from the DXF format correctly. By drawing real 3D lines, the OrbitControls in Three.js will naturally rotate around a true 3D bounding box rather than a 2D projection on a flat sheet of paper.
- **Alternatives considered**: Passing a camera configuration to the 3D viewer to skew 2D projected coordinates. This was rejected as it would be mathematically complex, highly error-prone, and wouldn't solve the fact that the underlying geometry was fundamentally flat.

### D2: Place annotations and metadata on the Z=0 plane
- **Choice**: Set the insertion point `dxf.insert` of all `TEXT` and `MTEXT` labels to `(x, y, 0)` on the ground plane rather than using isometric projections.
- **Rationale**: Keeps annotations organized at the baseline floor plan level, making them legible in both the 2D top-down plan view and the 3D orbit view.
- **Alternatives considered**: Floating text at their respective heights (e.g. placing "Ridge Height: 2.89m" at the ridge height). This was rejected because text in `three-dxf-loader` does not auto-face the camera, so floating text would rotate away from the user and look cluttered. Keeping it flat on Z=0 is standard.

## Risks / Trade-offs

- **[Risk]**: The 2D card preview viewer will no longer show an isometric drawing, but rather a top-down plan view.
  - *Mitigation*: This is actually a standard CAD preview convention. In a card feed, showing a clean top-down 2D engineering drawing is highly legible, and clicking into it unlocks the interactive 3D modal.
- **[Risk]**: The existing test suite heavily asserts the projected 2D coordinates.
  - *Mitigation*: We will rewrite `test_dxf_builder.py` to assert the true 3D coordinates. The test assertions will check `l.dxf.start` and `l.dxf.end` as 3D vectors `(x, y, z)`.
