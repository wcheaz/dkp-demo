## Why

The isolated `/cad-viewer-3d` test page parses uploaded or dropped IFC models into a 2D isometric DXF representation on the fly. However, the parser currently discards the local placements (`IfcLocalPlacement`) and rotation vectors (`Axis` and `RefDirection`) of the members, causing all structural elements (including sloped rafters and horizontal joists) to be swept vertically at the origin. This results in a completely incorrect and distorted 3D shape preview.

## What Changes

- Update `parseIfcToDxf` in `src/app/cad-viewer-3d/page.tsx` to resolve local placements and rotation matrices for each structural element:
  - Map `IfcExtrudedAreaSolid` entities back to their parent products (`IfcMember`, `IfcWallStandardCase`) using the IFC spatial representation references.
  - Parse the product's `IfcLocalPlacement` and retrieve the Cartesian point locations and directional vectors (`Axis` and `RefDirection`).
  - Calculate the 3D orthonormal basis for both the solid and the product local placements using vector projections and cross products.
  - Apply the coordinate transformations (translation and rotation) to the profile vertices before performing the 2D isometric projection.
- Ensure that parsing and rendering of `.dxf` files remains completely unaffected and functional.

### Non-Goals
- Updating the main page viewer at `src/app/cad-viewer/page.tsx`. This page is explicitly out of scope and will be updated in a future change after the isolated viewer is verified.
- Modifying the backend IFC generation code (`ifc_builder.py`). The generated IFC files are already geometrically correct and valid.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `cad-test-viewer`: Extend the isolated viewer to correctly orient and render 3D IFC/BIM structural geometry (including walls and truss members) using their defined local placement transformations.

## Impact

- **Frontend**: Only affects `src/app/cad-viewer-3d/page.tsx`.
- **Dependencies**: None. No new packages or dependencies are introduced.
- **APIs**: No changes to backend APIs or contracts.
