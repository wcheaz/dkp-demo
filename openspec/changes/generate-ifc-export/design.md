## Context

The `dkp-demo` application currently generates 2D and 3D DXF files representing wall layouts and roof trusses based on design parameters (configured in the agent's state/parameters). To support BIM coordination, users require a 3D IFC (Industry Foundation Classes) file that can be downloaded and forwarded directly to third-party engineering software—specifically MiTek Pamir.

To ensure consistency, the geometry of the generated IFC file must match the DXF file exactly.

## Goals / Non-Goals

**Goals:**
*   Implement a Python-based IFC generator (`ifc_builder.py`) using `ifcopenshell`.
*   Ensure full readability and compatibility of the output IFC in MiTek Pamir (using the IFC2x3 schema).
*   Extract geometry layout mathematics into a shared/modular interface to prevent coordination drift between DXF and IFC builders.
*   Register a Starlette endpoint `POST /api/ifc/generate` to serve the generated IFC files.
*   Add a user-friendly "Export IFC" download button in the Next.js frontend UI.

**Non-Goals:**
*   Reconstructing building models by parsing/interpreting the generated DXF file (we will build the IFC directly from parameters).
*   Generating metal truss plates, screws, brackets, or fine hardware detailing in the IFC output.
*   Rendering the IFC model visually within the web browser (only the DXF is rendered; the IFC is strictly a download asset).
*   Supporting IFC4 schema features or structures.

## Decisions

### Decision 1: Use Direct Parametric Generation (IfcOpenShell) over DXF Parsing
*   **Alternatives considered:** Parsing the generated 3D DXF lines and recreating structural entities from coordinate groupings.
*   **Rationale:** Parsing DXF files is error-prone because DXF lacks semantic and structural data (a line is just a line; it does not know if it is a top chord or a wall plate). Direct parametric generation via `ifcopenshell` allows us to create structured `IfcWallStandardCase` and `IfcMember` objects with metadata directly.

### Decision 2: Target IFC2x3 Schema
*   **Alternatives considered:** IFC4, IFC4.3.
*   **Rationale:** MiTek Pamir has robust, industry-standard compatibility with IFC2x3. Using IFC2x3 minimizes importing failures, schema validation warnings, and profile parsing issues in Pamir.

### Decision 3: Decouple Layout Math from Builders (Shared Geometry Interface)
*   **Alternatives considered:** Keep layout math inline within `dxf_builder.py` and duplicate the coordinate solving inside `ifc_builder.py`.
*   **Rationale:** Duplicating drawing math leads to synchronization errors and coordinate drift when design parameters change. We will refactor the core geometry calculations (e.g. wall coordinates, truss chord intersection points, web spacing) into a shared utility layer. Both `dxf_builder.py` and `ifc_builder.py` will call this utility layer to get coordinate data.

### Decision 4: Use Swept Solids for Structural Member Geometry
*   **Alternatives considered:** Boundary Representation (B-Rep / Tessellated Shells).
*   **Rationale:** B-Rep geometries are imported into Pamir as uneditable visual graphics. Extruded rectangular profiles (`IfcExtrudedAreaSolid` sweeping `IfcRectangleProfileDef`) enable Pamir to detect the centerline, span length, and section dimensions of studs and timber members, allowing them to be imported as editable structural elements.

## Risks / Trade-offs

*   **[Risk]** `ifcopenshell` dependency installation fails on target production/container environments due to platform-specific C++ binary bindings.
    *   *Mitigation:* Declare `ifcopenshell` clearly in `requirements.txt` and run pre-flight check tasks in our pipeline to verify binary library loading on the targeted Linux runtimes.
*   **[Risk]** Misalignment of local placements (`IfcLocalPlacement`) leading to rotated or misplaced framing members in Pamir.
    *   *Mitigation:* Align local placement X-axis along the longitudinal centerline of each timber member, and define profiles centered around the local origin. Validate the generated IFCs using standard open-source IFC viewers.
*   **[Risk]** Inconsistent profile mapping inside Pamir.
    *   *Mitigation:* Standardize naming of rectangular profiles to nominal timber dimensions (e.g. `45x120`, `45x220`) that match standard software catalogs.
