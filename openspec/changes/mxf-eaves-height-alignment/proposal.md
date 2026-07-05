## Why

After importing our auto-generated layout MXF files into MiTek Pamir and performing auto-framing, users encounter minor warnings/errors stating that the generated frames/trusses are "too short on the right/left hand side". This happens because the vertical position of the sloped roof surfaces is calculated directly from the wall top plate height ($3.05\text{ m}$) down to the eaves without incorporating a vertical truss heel height offset. As a result, the eaves Z-coordinate is set too low (sometimes below $3.05\text{ m}$), forcing a conflict where the physical truss top chords protrude vertically above the roof surface at the eaves, causing Pamir to flag the frames as too short.

## What Changes

- **Dynamic Eaves Height Calculation**: Dynamically calculate the vertical eaves height ($Z_{\text{eaves}}$) as $z\_base + 0.07\text{ m}$ (representing wall height + plate height + standard eaves vertical offset $0.07\text{ m}$) for all roof types, instead of hardcoding a fixed value.
- **Slope Height Adjustment**: Calculate sloped roof surface points by starting at the dynamic $Z_{\text{eaves}}$ baseline at the eaves edge and sloping upward towards the ridge, ensuring the top of the rafter matches the roof surface.
- **Flat Roof Height Adjustment**: Set flat roof surfaces at a constant height of $z\_base + 0.07\text{ m}$ to provide consistent vertical clearance matching the rafter/joist depth.

## Capabilities

### New Capabilities

### Modified Capabilities
- `mxf-roof-surfaces`: Update the vertical calculation of roof surfaces to dynamically anchor eaves at $Z_{\text{eaves}} = z\_base + 0.07\text{ m}$ and slope upwards, preventing auto-framed trusses from protruding above the roof surfaces.

## Impact
- `agent/src/geometry_solver.py`: Update flat, mono-pitch, gable, and hip roof surface polygon builders to use the dynamic eaves height anchoring ($z\_base + 0.07\text{ m}$) and slope calculations.
- `test/test_mxf_builder.py`: Update unit tests to reflect the corrected vertical coordinate values for all roof types.
