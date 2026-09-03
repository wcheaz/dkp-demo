## Why

When exporting designs for steep-pitched gable roofs (where the truss height exceeds the transport limit of 3.3m), our automated system generates separate half-span trusses instead of unified full-span trusses. This occurs because the roof planes are modeled as independent surfaces in the Layout MXF, causing MiTek Pamir to auto-frame each half separately. These split-span trusses have no central load-bearing support, making them structurally invalid and unable to be calculated. Additionally, the automated designs lack specialized gable-end trusses and fail to place bracing at the roof slope level.

## What Changes

- **Full-Span Truss Generation**: Modify the geometry engine to solve and generate a single wall-to-wall gable truss structure (spanning 10.8m) instead of two independent half-span trusses.
- **Transport Height Splitting**: Implement a check in the truss solver to split the truss into two sections (a lower main section and a top cap) if the total ridge height exceeds the 3.3m transport limit.
- **Gable-End Trusses**: Automatically place specialized `GableEnd` panels at the outermost positions of the roof layout.
- **Slope-Level Bracing**: Shift the generation of bracing from the horizontal ceiling level to diagonal top-chord bracing and purlins along the roof slope.

## Capabilities

### New Capabilities
- `mxf-structural-framing`: Generates full-span gable trusses, multi-part transport-split frames, gable-end panels, and slope-level bracing directly within the exported MXF file.

### Modified Capabilities
- `mxf-generation`: Extends the REST API and frontend downloader to include structural frame definitions (`<FrameList>` and `<BuildingFrameList>`) in the generated MXF payload instead of returning only the wall layout.

## Impact

- **Backend Logic**: Modifies `agent/src/mxf_builder.py` and `agent/src/geometry_solver.py` to calculate truss nodes, plates, and split heights.
- **REST API**: Updates `/api/mxf/generate` to deliver the fully framed structural MXF.
- **Unit Tests**: Modifies test assertions in `test/test_mxf_builder.py` and `test/test_mxf_endpoint.py`.
