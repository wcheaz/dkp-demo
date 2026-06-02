## Context

The current DXF output in `dxf_builder.py` generates flat 2.5D wireframe geometry. While the `Trusses` layer color (brown) visually hints at timber, the file contains no explicit material specs or thickness attributes. When imported into MiTek Pamir, designers must manually scale the geometry and trace walls and truss locations manually. By upgrading to 3D coordinate geometry, adding a dedicated `Wall_Centerlines` layer, and separating user labels from technical specifications on a `Lumber_Specs` layer, we can automate the Pamir designer's workflow.

## Goals / Non-Goals

**Goals:**
- Transition all layout geometry (walls, roof outlines, trusses) to use true 3D coordinates `(X, Y, Z)` in `ezdxf` with a default wall height of 2700 mm.
- Add a dedicated `Wall_Centerlines` layer containing the 2D footprint of the walls at Z=0 for rapid tracing.
- Separate user-facing annotations (`Labels` layer) from engineering specifications (`Lumber_Specs` layer).
- Ensure all measurements in the DXF file use a strict 1:1 scale where 1 unit = 1 millimeter.

**Non-Goals:**
- Supporting 3D solid rendering (e.g., drawing thick solid 3D box meshes instead of 3D lines) in the DXF builder. Wireframe is preferred for clean CAD snapping.
- Allowing user-customizable wall heights in this phase (hardcoded default of 2700 mm is sufficient).
- Exporting to other formats (e.g., IFC) in this change proposal.

## Decisions

### D1: True 3D Wireframe Geometry via ezdxf 3D Coordinates
- **Choice**: Use 3-tuple `(X, Y, Z)` coordinates for all `LINE` and `POLYLINE` additions instead of 2-tuple `(X, Y)` coordinates.
  - *Floor Plan*: Bottom rectangle at `Z = 0`, top rectangle at `Z = 2700`, and four vertical lines connecting them at coordinates `(0, 0)`, `(w, 0)`, `(w, d)`, and `(0, d)`.
  - *Roof outline*: Drawn at eave height `Z = 2700` and ridge height `Z = 2700 + ridge_height`.
  - *Trusses*: Spaced along the Y-axis, drawn as triangles with a bottom chord at `Z = 2700` and top chords meeting at the ridge `Z = 2700 + ridge_height`.
- **Rationale**: Standard CAD programs and Pamir natively support 3D snapping and rotation. Wireframe 3D coordinates allow the viewer to render the design in 3D space, which aligns with the user's requirement.
- **Alternatives Considered**: Creating 3D solid meshes (`3DSOLID` or `MESH`). This was rejected because mesh generation is highly complex, increases file size significantly, and makes simple snapping harder for structural tracing.

### D2: Dedicated Wall Centerlines Layer
- **Choice**: Draw a closed 2D rectangle at `Z = 0` representing the wall centerline on a new `Wall_Centerlines` layer.
- **Rationale**: In Pamir, walls are drawn along their centerlines. Having a clean centerline layer means the designer can click "Trace Walls" and snap to the centerline layout instantly, rather than manually calculating the offset between exterior and interior wall faces.
- **Alternatives Considered**: Drawing double-line wall centerlines. Rejected since single centerline vectors are the standard snapping target in CAD-to-wall conversion tools.

### D3: Layer Isolation and Material Color Coding
- **Choice**: Assign distinct layers with dedicated RGB colors representing materials and annotations:
  * `Floor_Plan`: Concrete Gray `(128, 128, 128)`
  * `Wall_Centerlines`: Green `(34, 139, 34)`
  * `Roof_Outline`: Steel Blue `(70, 130, 180)`
  * `Trusses`: Timber Brown `(139, 90, 43)`
  * `Dimensions`: Annotation Blue `(0, 0, 255)`
  * `Labels`: Yellow/Amber `(218, 165, 32)`
  * `Lumber_Specs`: Purple `(128, 0, 128)`
- **Rationale**: Isolating dimensions, user labels, and technical specs onto separate layers allows the Pamir operator to hide/show layers to clear clutter and prevent incorrect snapping.

### D4: Separating General Labels from Lumber Specifications
- **Choice**: Place end-user labels (Width, Depth, Ridge Height in meters) on the `Labels` layer, and place engineering specs (e.g. lumber grade "C24", member thickness "45 mm", and widths) on a new `Lumber_Specs` layer.
- **Rationale**: End users only need basic dimension labels for previewing, while Pamir designers need to see material specifications.

## Risks / Trade-offs

- **[Risk]**: The simple WebGL CAD viewer in the frontend might not support 3D rotation, rendering the 3D model only from a top-down orthogonal view.
  - *Mitigation*: Even in orthogonal 2D top-down view, 3D DXF files render correctly (as a 2D projection on the screen). Standard `@mlightcad/cad-simple-viewer` can render 3D coordinates. We will verify the visual output in the frontend viewer and confirm it looks correct.
