## ADDED Requirements

### Requirement: Calculate and Generate Roof and Floor Surfaces in MXF
The system SHALL pre-calculate and export the 3D surface geometry of both the roof and floor planes in the generated Layout MXF file based on the design parameters. This allows MiTek Pamir to import the complete roof shape, pitch, and overhang without manual user intervention.

Normative requirements:
- The generated MXF root `<Mxf>` node SHALL contain a `<SurfaceList>` node.
- The `<Building>` node SHALL contain a `<RoofList>` node mapping the roof surfaces and a `<FloorList>` node mapping the floor surfaces.
- Floor surfaces (id starting with `SF`) SHALL be placed at $Z = 0$ mapping the building footprint: from $(0,0,0)$ to $(W,0,0)$ to $(W,D,0)$ to $(0,D,0)$ to $(0,0,0)$.
- Roof surfaces (id starting with `SR`) SHALL include the eaves overhang $O$ on all outer edges.
- Vertical offsets SHALL be calculated from the wall top plate height (wall height $3.0\text{ m}$ + wall plate height $0.05\text{ m} = 3.05\text{ m}$).
- The vertical position of the eaves edge is calculated as $Z_{\text{eaves}} = 3.05 - O \cdot \tan(\theta)$.
- The vertical position of the ridge is calculated as $Z_{\text{ridge}} = 3.05 + Run_{\text{ridge}} \cdot \tan(\theta)$, where $Run_{\text{ridge}}$ is the horizontal distance from the wall to the ridge.

#### Scenario: Successful Gable roof surface generation
- **GIVEN** active DesignParameters specifying width = 10.0m, depth = 15.0m, roofType = "Gable", roofPitch = 30, and overhang = 0.5m
- **WHEN** build_mxf is invoked
- **THEN** the generated XML SHALL contain:
  - A `<RoofList>` with exactly 2 `<Roof>` nodes reference surface IDs `SR0-0` and `SR0-1`
  - A `<FloorList>` with a `<Floor>` referencing `SF0-0`
  - A `<SurfaceList>` containing:
    - `SF0-0` with polygon `"0,0,0 10,0,0 10,15,0 0,15,0 0,0,0"`
    - Two `SR` surfaces with $Z_{\text{eaves}} = 3.05 - 0.5 \cdot \tan(30^\circ) \approx 2.761$ and $Z_{\text{ridge}} = 3.05 + 5.0 \cdot \tan(30^\circ) \approx 5.937$
    - A ridge running from $(5.0, -0.5, 5.937)$ to $(5.0, 15.5, 5.937)$

#### Scenario: Successful Hip roof surface generation
- **GIVEN** active DesignParameters specifying width = 8.0m, depth = 9.6m, roofType = "Hip", roofPitch = 18, and overhang = 0.25m
- **WHEN** build_mxf is invoked
- **THEN** the generated XML SHALL contain:
  - A `<RoofList>` with exactly 4 `<Roof>` nodes referencing surface IDs `SR0-0`, `SR0-1`, `SR0-2`, and `SR0-3`
  - A `<SurfaceList>` containing 4 triangular and trapezoidal surfaces with $Z_{\text{eaves}} \approx 2.969$ and $Z_{\text{ridge}} \approx 4.350$
  - A ridge running from $(4.0, 4.0, 4.350)$ to $(4.0, 5.6, 4.350)$

#### Scenario: Successful Flat roof surface generation
- **GIVEN** active DesignParameters specifying width = 10.0m, depth = 15.0m, roofType = "Flat", roofPitch = 0, and overhang = 0.5m
- **WHEN** build_mxf is invoked
- **THEN** the generated XML SHALL contain:
  - A `<RoofList>` referencing surface ID `SR0-0`
  - A `<SurfaceList>` containing `SR0-0` with polygon `"-0.5,-0.5,3.05 10.5,-0.5,3.05 10.5,15.5,3.05 -0.5,15.5,3.05 -0.5,-0.5,3.05"`
