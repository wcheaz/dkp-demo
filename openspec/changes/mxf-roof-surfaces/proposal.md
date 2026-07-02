## Why

Currently, layout MXF files generated for MiTek Pamir only contain wall boundaries and omit roof and floor surfaces. Consequently, when Pamir imports these files, it does not receive the desired roof pitch or type (e.g., a hip roof with an 18-degree pitch) and defaults to its own local templates (e.g., a 25-degree Gable roof). Pre-calculating and exporting the roof and floor surfaces in the MXF file will automate this layout definition, matching the user's specific roof design.

## What Changes

- **Roof Surface Calculation**: Calculate 3D polygon coordinates for the roof planes (Gable, Hip, Mono-pitch, Flat) using `roofType`, `roofPitch`, and `overhang` from the design parameters.
- **Eaves and Ridge Height Mapping**: Correctly calculate the vertical position ($Z$ coordinates) of the eaves and ridge based on wall height, plate heights, and slope run.
- **MXF Surface Lists**: Generate `<RoofList>`, `<FloorList>`, and `<SurfaceList>` nodes in the output MXF file with exact 3D polygon definitions.

### Non-Goals
- Supporting non-rectangular buildings or complex multi-level roofs.
- Generating structural framing (truss layouts, member sizes, connector plates) within the MXF file.
- Direct rendering of MXF surfaces in the frontend CAD viewer.

### First-Rollout Boundaries
- Scope is limited to the backend MXF generator engine and its corresponding test suites.
- Supports rectangular shapes with standard Gable, Hip, Mono-pitch, and Flat roof styles.

## Capabilities

### New Capabilities
- `mxf-roof-surfaces`: Generation of 3D roof and floor surfaces inside the Layout MXF export based on design parameters (roof type, pitch, overhang, and dimensions).

### Modified Capabilities

## Impact

- `agent/src/mxf_builder.py`: Will be updated to perform geometry calculations and generate the new XML nodes.
- `test/test_mxf_builder.py`: New unit tests to verify the calculated 3D coordinates of surfaces for different roof types.
