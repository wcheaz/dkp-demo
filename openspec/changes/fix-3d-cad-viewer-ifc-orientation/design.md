## Context

The isolated `/cad-viewer-3d` page renders IFC files by converting them to DXF format on the fly via the `parseIfcToDxf` function. Because the parser currently ignores the local coordinate placements (`IfcLocalPlacement`) and direction vectors (`Axis`, `RefDirection`) of each product (such as `IFCMEMBER` or `IFCWALLSTANDARDCASE`), it extrudes all geometry vertically at unrotated coordinates, resulting in distorted shape displays.

## Goals / Non-Goals

**Goals:**
- Parse the coordinate axes (`Axis` and `RefDirection`) and location of `IfcAxis2Placement3D` associated with both the solid's placement and the product's local placement.
- Derive a correct 3D orthonormal basis ($x_{axis}, y_{axis}, z_{axis}$) for each placement.
- Apply the 3D coordinate transformations to the profile vertices to compute correct global coordinates.
- Perform the 2D isometric projection on the transformed global vertices for rendering.
- Keep DXF file uploading, parsing, and rendering functionality fully intact.

**Non-Goals:**
- Modifying the main viewer page `src/app/cad-viewer/page.tsx` (this will be done after a human verification step).
- Modifying backend IFC export generation (`agent/src/ifc_builder.py`).

## Decisions

### Decision 1: Lightweight regex-based relation parsing vs. Web Assembly parser
- **Alternative**: Integrate a full-featured JavaScript IFC parsing library such as `web-ifc`.
- **Choice**: Extend the existing regex-based parser in `parseIfcToDxf` to trace entity ID references.
- **Rationale**: The generated IFC files use a fixed, predictable structure. Adding a full library like `web-ifc` would introduce significant package overhead (multiple megabytes of WebAssembly files), require complex worker setups, and increase bundle size. Modifying the existing JS parser is lightweight, zero-overhead, and sufficient for the task.

### Decision 2: Product Placement Association
- **Alternative**: Apply only the solid's placement vector.
- **Choice**: Trace the solid ID through `IFCSHAPEREPRESENTATION` and `IFCPRODUCTDEFINITIONSHAPE` to its parent `IFCMEMBER` or `IFCWALLSTANDARDCASE`, and apply the product's `IFCLOCALPLACEMENT`.
- **Rationale**: In the IFC standard, the coordinate translations and rotations (such as sloped rafter angles) are attached to the product itself via its local placement, while the solid represents the raw geometric extrusion shape. Correct positioning requires combining both transformations.

### Decision 3: Mathematical Orthonormal Basis Reconstruction
- **Choice**: Implement standard vector projection to project `RefDirection` (approximate local X) onto the plane perpendicular to the normalized `Axis` (local Z) vector to get the exact local X axis. Cross product of local Z and local X gives the local Y axis.
- **Rationale**: This is the exact algorithm defined by buildingSMART and the STEP/IFC standard for `IfcAxis2Placement3D`, guaranteeing congruence with standard BIM viewers.

## Risks / Trade-offs

- **Risk**: Regression in DXF rendering.
  - **Mitigation**: The code path for DXF files bypasses `parseIfcToDxf` entirely. We will run regression checks with existing DXF files.
- **Risk**: Missing vectors (optional arguments in `IfcAxis2Placement3D`).
  - **Mitigation**: If `Axis` or `RefDirection` are omitted (as indicated by `$` in the STEP file), they will default to `(0, 0, 1)` and `(1, 0, 0)` respectively.
