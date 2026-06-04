## Why

The currently generated DXF files represent a true 3D model, but they load by default in flat, top-down orthogonal views in web-based CAD viewers, which lacks an immediate sense of scale and visual depth. Additionally, layer colors are defined only in True Color (RGB), which many simple web viewers do not render, causing drawings to appear in flat black/white. Incorporating a mathematical 2D isometric projection in the drawing pipeline and assigning classic AutoCAD Color Index (ACI) colors to layers will ensure all users see colored, 3D-like isometric designs out-of-the-box.

## What Changes

- **2D Isometric Coordinate Projection**: Project all 3D coordinates $(X, Y, Z)$ mathematically into 2D isometric coordinates $(X_{iso}, Y_{iso})$ using standard $30^\circ$ projection formulas during DXF generation.
- **ACI Color Index Integration**: Configure classic AutoCAD Color Index (ACI) codes (e.g., green, blue, brown, gray, yellow) on all layers in the DXF builder, ensuring color rendering works across simple and legacy CAD viewers.

## Non-Goals

- Implementing actual 3D rotation controls in the frontend React CAD viewer component.
- Generating alternative 3D file formats (e.g., IFC) in this change.
- Changing the raw engineering logic or truss counting algorithms.

## Capabilities

### Modified Capabilities

- `dxf-builder`: Update the coordinate generation system to project 3D coordinate endpoints to a 2D isometric plane, and configure ACI colors on each layer.
- `dxf-truss-layout`: Update the truss layout lines to be projected onto the 2D isometric coordinates.
- `dxf-dimensions-annotations`: Update dimension rendering and label positions to match the isometric coordinate space.

## Impact

- **Backend (`agent/src/dxf_builder.py`)**: Update all drawing methods to use a 2D isometric coordinate mapping helper.
- **Tests (`test/test_dxf_builder.py`)**: Update unit tests to verify the mathematically projected 2D coordinates and ACI color properties on layers.
