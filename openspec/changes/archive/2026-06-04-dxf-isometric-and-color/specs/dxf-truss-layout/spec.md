## MODIFIED Requirements

### Requirement: Truss cross-sections on Trusses layer

The module SHALL draw truss cross-sections as 2D LINE entities on a layer named `Trusses`. Each truss SHALL represent a 3D structural shape (at Z=2700 for the bottom chord and meeting at Z=2700+ridge_height for the ridge peak) placed at its respective Y-coordinate (or X-coordinate if the building is wider than deep) and mathematically projected to 2D using the isometric formula: $X_{iso} = (X - Y) \cdot \cos(30^\circ)$ and $Y_{iso} = (X + Y) \cdot \sin(30^\circ) + Z$.

#### Scenario: Gable truss cross-sections on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"` and `roofPitch=30`
- **THEN** the `Trusses` layer contains 2D LINE entities representing the top and bottom chords of each truss, with coordinates mapped using the isometric projection helper

#### Scenario: Flat truss cross-sections
- **WHEN** `build_dxf` is called with `roofType="Flat"`
- **THEN** each truss cross-section is a single horizontal 2D LINE on the `Trusses` layer, representing the tie-beam at Z=2700 projected isometrically

### Requirement: Mono-pitch truss cross-section

For `roofType="Mono-pitch"`, each truss cross-section SHALL be a right triangle sloping from eave `(0, y, 2700)` to ridge `(w, y, 2700+ridge_height)` with all endpoints projected to 2D using the isometric formula.

#### Scenario: Mono-pitch cross-section
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Mono-pitch"`
- **THEN** each truss cross-section on the `Trusses` layer consists of three LINEs representing the sloped rafter, bottom chord, and vertical rise member projected isometrically
