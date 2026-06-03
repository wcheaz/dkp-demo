## Context

The current DXF model contains 3D coordinates, but renders flat and top-down in the browser CAD viewer because the viewer uses a 2D orthographic camera view projection. Furthermore, because colors are only defined using True Color (RGB), web viewers that default to AutoCAD Color Index (ACI) codes fall back to displaying all layers in white/black. This design document outlines how we will mathematically project the 3D coordinates into a 2D isometric representation on the backend and integrate both ACI and True Color properties for all layers.

## Goals / Non-Goals

**Goals:**
- Implement a 2D isometric projection matrix helper in `dxf_builder.py` that maps $(X, Y, Z)$ to $(X_{iso}, Y_{iso})$ coordinates.
- Ensure all 3D line drawing calls in `dxf_builder.py` pass through the projection helper.
- Configure ACI colors (integers 1–255) on all layers in `dxf_builder.py` alongside the existing True Color RGB values.

**Non-Goals:**
- Rewriting the frontend React component or modifying the `@mlightcad/cad-simple-viewer` Three.js camera directly.
- Allowing interactive 3D rotation of the canvas in the web preview in this change.

## Decisions

### D1: 2D Isometric Projection Helper on the Backend
- **Choice**: Implement a helper function `_to_iso(x, y, z) -> tuple[float, float]` in `dxf_builder.py` that projects 3D coordinates onto a 2D plane using a standard $30^\circ$ angle:
  $$X_{iso} = (X - Y) \cdot \cos(30^\circ) \approx (X - Y) \cdot 0.866025$$
  $$Y_{iso} = (X + Y) \cdot \sin(30^\circ) + Z \approx (X + Y) \cdot 0.5 + Z$$
- **Rationale**: This is highly compatible. Since the DXF geometry itself is drawn in isometric projection, it renders isometrically on any standard 2D CAD viewer or web-based renderer, bypassing the need for WebGL 3D camera controls or orbit plugins.
- **Alternatives Considered**: Modifying the React CAD viewer's camera orientation. This was rejected because the viewer uses an internal orthographic camera locked to a 2D viewport bounds calculation (`zoomToFitDrawing` based on 2D extents), and modifying it is fragile.

### D2: Unified ACI Color Index and True Color (RGB) Mapping
- **Choice**: Assign standard ACI (AutoCAD Color Index) codes on all layers in addition to RGB values:
  * `Floor_Plan`: ACI `9` (Gray) / RGB `(128, 128, 128)`
  * `Wall_Centerlines`: ACI `3` (Green) / RGB `(34, 139, 34)`
  * `Roof_Outline`: ACI `4` (Cyan/Slate Blue) / RGB `(70, 130, 180)`
  * `Trusses`: ACI `34` (Brownish Orange) / RGB `(139, 90, 43)`
  * `Dimensions`: ACI `5` (Blue) / RGB `(0, 0, 255)`
  * `Labels`: ACI `2` (Yellow) / RGB `(218, 165, 32)`
  * `Lumber_Specs`: ACI `6` (Magenta) / RGB `(128, 0, 128)`
- **Rationale**: Setting the `.color` property ensures that viewers falling back to ACI rendering will show correct colors. Setting `.rgb` preserves advanced color compatibility.

## Risks / Trade-offs

- **[Risk]**: Dimensions might look slightly distorted because ezdxf's `add_linear_dim` is designed for orthogonal drafting.
  - *Mitigation*: We will project the dimension points (`p1`, `p2`, `base`) to the 2D isometric plane, which will allow `ezdxf` to draw the dimension block correctly aligned between the projected 2D coordinates. We will verify the look in the test cases.
