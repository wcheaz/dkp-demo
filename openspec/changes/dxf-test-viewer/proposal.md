## Why

Developers and users need a way to preview arbitrary local DXF files interactively using the existing CAD viewer. In addition, the generated DXF files currently use default white/black lines, which do not represent different materials (wood, concrete, steel) realistically. Setting up a dedicated test viewer page and styling DXF layers with material-appropriate colors solves these needs.

## What Changes

- **DXF Test Route**: A new isolated client-side route `/dxf-viewer` with a drag-and-drop or file selector to load and display any local DXF file using the existing `<CadViewer>` component.
- **Material-based Layer Colors**: Update the DXF builder to assign specific colors representing materials to each DXF layer using `ezdxf` layer RGB values (e.g., timber brown for trusses, concrete gray for the floor plan, sky blue for dimensions).

## Non-goals

- Adding links or buttons to the `/dxf-viewer` page from the main user-facing gallery.
- Persisting uploaded DXF files in the database or server filesystem.
- Generating 3D DXF coordinates or loading alternative 3D model files (OBJ, GLTF, IFC) in this change.

## Capabilities

### New Capabilities
- `dxf-test-viewer`: Isolated client-side route at `/dxf-viewer` for drag-and-drop local DXF rendering.

### Modified Capabilities
- `dxf-builder`: Standardize layer colors in the DXF generation code to represent timber, concrete, and annotations.

## Impact

- **Frontend Pages**: New route page `src/app/dxf-viewer/page.tsx`.
- **Backend Code**: `agent/src/dxf_builder.py` (updates layer color configurations).
- **Backend Tests**: `test/test_dxf_builder.py` (verify layer colors are set correctly).
