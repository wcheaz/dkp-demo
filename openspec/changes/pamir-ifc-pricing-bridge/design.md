## Context

Currently, the client-side viewer has a simplified parser that ignores B-Rep geometry, arbitrary extrusion profiles, and nested local coordinate systems. Furthermore, the backend IFC generator outputs a flat containment structure without the assembly hierarchies or property sets needed for professional imports (like MiTek Pamir). To resolve this, we will upgrade the client-side parser to support full B-Rep rendering and recursive coordinate frame transforms, and upgrade the backend generator to produce Pamir-compatible IFC assembly structures, pricing properties, and support points.

## Goals / Non-Goals

**Goals:**
- Enable the React 3D viewer to render Pamir IFC exports containing B-Rep geometry and composite curves.
- Reconstruct the local coordinate transformations correctly by recursively traversing placement parent matrices.
- Modify the backend IFC generator to aggregate members under `IfcElementAssembly` truss structures.
- Embed Pamir-compatible metadata and attach pricing-specific property sets (`Pamir Frame`, `Pamir Support`, `Pamir Member`).
- Calibrate the pricing engine to reflect sheathing factors, metalwork hangers, and setup margins.

**Non-Goals:**
- Building a full solid-geometry modeler or boundary representation kernel in JavaScript.
- Supporting general boolean CSG subtraction/union operations in the client-side parser.
- Adding physical geometric details for metalwork fasteners like nails or plates in generated files.

## Decisions

### 1. B-Rep Geometry Parsing in Front-End
- **Approach**: The parser will scan for `IFCFACETEDBREP` and `IFCSHELLBASEDSURFACEMODEL` entities.
- **Algorithm**:
  1. Retrieve `ClosedShell` from the B-Rep record.
  2. Traverse `IfcClosedShell` to extract all `IfcFace` elements.
  3. Traverse `IfcFace` to extract `IfcFaceOuterBound` containing `IfcPolyLoop` entities.
  4. Resolve coordinates of `IfcCartesianPoint` references for the polyloops.
  5. Generate DXF `3DFACE` or a sequence of `LINE` segments for each polyloop edge.
- **Rationale**: This is a lightweight, dependency-free approach to display wireframe or shaded B-Rep meshes in WebGL without loading heavy client-side parsing libraries.

### 2. Recursive Coordinate Frame Assembly
- **Approach**: Modify `resolvePlacement3D` to calculate absolute transformations.
- **Algorithm**:
  - Represent local placements as $4 \times 4$ transformation matrices combining the placement location and orthonormal basis (X, Y, Z directions).
  - Recursively fetch `PlacementRelTo` fields up to the storey root.
  - Multiplied from right to left: $M_{\text{global}} = M_{\text{parent}} \times M_{\text{local}}$.
- **Rationale**: Ensures nested members within assemblies preserve their global coordinates.

### 3. Hierarchical Spatial Containment in Backend
- **Approach**: Create `IfcElementAssembly` objects in `ifc_builder.py` representing each truss (e.g., `S1`, `B1`).
- **Rationale**: Gruoping elements under assemblies ensures Pamir maps the structure as coherent structural truss components rather than floating beams.

### 4. Custom Property Sets and Support Proxies
- **Approach**: 
  - Add virtual support points as `IfcBuildingElementProxy` placed at wall plate intersections.
  - Attach property sets: `Pamir Frame` (weight, design status), `Pamir Support` (type, face), and `Pamir Member` (SiteFixed).
- **Rationale**: Matches the properties expected by the Pamir quoting module, ensuring automatic price generation from imported files.

### 5. Calibrating the Pricing formula in Backend
- **Approach**: Update the backend pricing logic in `agent/src/agent.py` to use calibrated cost coefficients:
  - Increase raw timber cost coefficient to 6200 CZK/m³ to reflect C24 grade wood.
  - Add `metalworkCost` computing the price of ABR90 angle brackets based on support nodes (support nodes = totalTrusses × 2, bracket count = support nodes × 1.6, bracket cost = 370 CZK per bracket).
  - Adjust assembly cost and hanger cost to include labor and overhead.

## Risks / Trade-offs

- **[Risk] Performance in Javascript Parser** → Parsing large IFC files with thousands of B-Rep coordinates on the client thread can freeze the UI.
  - *Mitigation*: Limit parsing to files under 10MB (already checked) and process geometry loops sequentially.
- **[Risk] Compatibility with other viewers** → Using custom `IfcElementAssembly` property sets might cause warnings in simple BIM viewers.
  - *Mitigation*: Standard property definitions are placed alongside custom sets, ensuring compatibility with standard tools.
