## Why

The current system has two major limitations regarding IFC files:
1. The 3D CAD viewer fails to render Pamir-generated IFC files, displaying only a single fallback line. This occurs because the client-side parser does not support Boundary Representation (B-Rep) geometry, arbitrary closed profiles, or multi-level coordinate placements.
2. The backend-generated IFC files do not align with the hierarchical structure and inline metadata conventions used by MiTek Pamir, making them incompatible for import and automatic pricing.

By bridging this gap, users will be able to visualize industry-standard Pamir files in the web UI, and our generated IFCs can be imported directly into Pamir for automated pricing and engineering workflows.

## What Changes

- **Upgraded Client-Side Parser**: The client-side IFC parser (`parseIfcToDxf`) will be upgraded to support B-Rep geometry (`IFCFACETEDBREP`), arbitrary profile definitions (`IFCARBITRARYCLOSEDPROFILEDEF`), and recursive placement transformation (`IFCLOCALPLACEMENT` parent chains).
- **Hierarchical IFC Generation**: The backend IFC generator will group generated timber members under `IfcElementAssembly` entities typed as `.TRUSS.` instead of outputting a flat container structure.
- **Enhanced Pricing and Lumber Metadata**: The generated IFCs will embed lumber grades and cross-sections directly in member names/descriptions and attach the custom pricing property sets (`Pamir Frame`, `Pamir Support`, `Pamir Member`) that Pamir uses for automated quoting imports.
- **Calibrated Pricing Model**: The backend pricing engine coefficients will be adjusted to align with the Pamir quote metrics (factoring in sheathing weights, press setup margins, and structural metalwork connectors based on support zones).

## Non-goals

- Implementing full B-Rep solid-modeling operations or boolean CSG tree parsing in the client-side viewer. The viewer will only extract polygon loops and convert them to wireframe DXF lines/faces.
- Generating physical, 3D meshes of metal nailplates or connector brackets in the IFC output. Connectors will remain virtual support points with attached property sets.
- Replacing the existing pricing engine completely; we will only update the pricing formula coefficients to match the calibrated Pamir quote metrics.

## Capabilities

### New Capabilities
- `pamir-ifc-viewer-support`: Enables the client-side CAD viewer to parse and display B-Rep mesh geometries, composite profiles, and deeply nested placements found in Pamir IFC exports.
- `pamir-pricing-integration`: Outlines the mapping of structural properties (weights, connector counts, lumber grade formats) into custom Pamir property sets in the generated IFC files.

### Modified Capabilities
- `ifc-generation-tool`: Upgrade the IFC builder module to organize members into hierarchical assemblies and format member descriptions for Pamir importer compatibility.
- `pricing-calculation`: Calibrate the backend pricing engine formula coefficients to align with Pamir quote metrics (including sheathing sheathing and connector margin overheads).

## Impact

- **Frontend**: `src/app/cad-viewer-3d/page.tsx` (the `parseIfcToDxf` function and coordinate resolution helpers).
- **Backend**: `agent/src/ifc_builder.py` (hierarchical spatial structure, property sets, formatting) and `agent/src/agent.py` (pricing engine formula coefficients in `generate_quote`).
- **Dependencies**: No new npm or Python dependencies will be introduced. `ifcopenshell` and existing React CAD libraries remain unchanged.
