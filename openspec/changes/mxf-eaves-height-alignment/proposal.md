## Why

After importing our auto-generated layout MXF files into MiTek Pamir and performing auto-framing, users encounter minor warnings/errors stating that the generated frames/trusses are "too short on the right/left hand side". This happens because the vertical position of the sloped roof surfaces is calculated directly from the wall top plate height ($3.05\text{ m}$) down to the eaves without incorporating a vertical truss heel height offset. As a result, the eaves Z-coordinate is set too low (sometimes below $3.05\text{ m}$), forcing a conflict where the physical truss top chords protrude vertically above the roof surface at the eaves, causing Pamir to flag the frames as too short.

## What Changes

- **Eaves Height Anchoring**: Anchor the base vertical eaves coordinate ($Z_{\text{eaves}}$) at exactly $3.12\text{ m}$ (wall height $3.0\text{ m}$ + wall plate $0.05\text{ m}$ + standard eaves vertical offset $0.07\text{ m}$) for all roof types.
- **Slope Height Adjustment**: Calculate sloped roof surface points by starting at $Z_{\text{eaves}} = 3.12\text{ m}$ at the eaves edge and sloping upward towards the ridge, ensuring the top of the rafter matches the roof surface.
- **Flat Roof Height Adjustment**: Set flat roof surfaces at a constant height of $3.12\text{ m}$ to provide consistent vertical clearance matching the rafter/joist depth.

## Capabilities

### New Capabilities

### Modified Capabilities
- `mxf-roof-surfaces`: Update the vertical calculation of roof surfaces to anchor eaves at $Z_{\text{eaves}} = 3.12\text{ m}$ and slope upwards, preventing auto-framed trusses from protruding above the roof surfaces.

## Impact
- `agent/src/geometry_solver.py`: Update flat, mono-pitch, gable, and hip roof surface polygon builders to use the correct eaves height anchoring ($3.12\text{ m}$) and slope calculations.
- `test/test_mxf_builder.py`: Update unit tests to reflect the new, correct vertical coordinate values for all roof types.
