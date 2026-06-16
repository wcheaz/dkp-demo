## Why

Customers need to export their truss and wall designs as 3D BIM models to send to architects and engineers for structural calculations, planning permission, and clash detection in software like MiTek Pamir. Currently, the system only generates flat 2D/3D DXF files. By generating structured 3D IFC (IFC2x3) files directly from design parameters, we enable seamless integration with professional engineering software.

### Scope
- Implement a parametric 3D IFC generator (`ifc_builder.py`) using `ifcopenshell` to output wall and truss geometries.
- Align geometries (walls, members, beams) to use standard extruded swept solids, ensuring compatibility with MiTek Pamir.
- Create a Starlette HTTP endpoint `/api/ifc/generate` to serve the generated `.ifc` files.
- Expose an "Export IFC" download button next to the existing "Export DXF" button in the Next.js web application UI.

### Non-goals
- Reconstructing IFC files by parsing existing DXF files (DXF-to-IFC semantic reconstruction).
- Generating visual connection plates, bolts, or metal connectors in the IFC file.
- Supporting IFC4 or other experimental schemas (only IFC2x3 is targeted for maximum Pamir compatibility).
- Creating interactive 3D rendering of IFC models in the client browser (the IFC is strictly a download-and-forward asset).

### Rollout Boundaries
- **Phase 1 (Backend & CLI):** Build the `ifc_builder.py` geometry module and verify output IFC files can be read by standard BIM tools.
- **Phase 2 (API Endpoint):** Implement and register the HTTP endpoint.
- **Phase 3 (Frontend Integration):** Integrate the download button in the Next.js UI next to the DXF download link.

## What Changes

- **Add** `ifcopenshell` to Python dependencies in `requirements.txt`.
- **Add** a new module `agent/src/ifc_builder.py` containing the logic to build the IFC spatial tree (`IfcProject` -> `IfcSite` -> `IfcBuilding` -> `IfcBuildingStorey`) and add walls/trusses as extruded swept solids.
- **Modify** `agent/src/dxf_builder.py` and `agent/src/ifc_builder.py` (or introduce a shared module) to share structural layout math and coordinate calculations, preventing model drift between DXF and IFC outputs.
- **Add** a new endpoint `/api/ifc/generate` in the backend API routing.
- **Modify** the web client's design panel component to show an IFC export download button.

## Capabilities

### New Capabilities
- `ifc-generation-tool`: Generate a valid IFC2x3 file from a `DesignParameters` instance using `ifcopenshell`.
- `ifc-serve-endpoint`: Serve the generated IFC file via an HTTP POST endpoint `/api/ifc/generate`.

### Modified Capabilities
- `design-display`: Update the user interface to show the IFC download button alongside the DXF download option.

## Impact

- **Dependencies:** Adds `ifcopenshell` package to Python environment.
- **Backend Services:** Adds `/api/ifc/generate` endpoint.
- **Frontend UI:** Updates the download controls on the design visualization and parameter entry pages.
- **Engineering Workflow:** Enhances model consistency and enables downstream structural analysis in MiTek Pamir.
