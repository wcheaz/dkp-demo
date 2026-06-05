## MODIFIED Requirements

### Requirement: Truss cross-sections on Trusses layer

The module SHALL draw truss cross-sections as 3D LINE entities on a layer named `Trusses`. Each truss SHALL represent a 3D structural shape (at Z=2700 for the bottom chord and meeting at Z=2700+ridge_height for the ridge peak) placed at its respective Y-coordinate (or X-coordinate if the building is wider than deep) using true 3D coordinates.

#### Scenario: Gable truss cross-sections on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"` and `roofPitch=30`
- **THEN** the `Trusses` layer contains 3D LINE entities representing the top and bottom chords of each truss at their actual physical coordinates

#### Scenario: Flat truss cross-sections
- **WHEN** `build_dxf` is called with `roofType="Flat"`
- **THEN** each truss cross-section is a single horizontal 3D LINE on the `Trusses` layer, representing the tie-beam at Z=2700

### Requirement: Mono-pitch truss cross-section

For `roofType="Mono-pitch"`, each truss cross-section SHALL be a right triangle sloping from eave `(0, y, 2700)` to ridge `(w, y, 2700+ridge_height)` using true 3D coordinates.

#### Scenario: Mono-pitch cross-section
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Mono-pitch"`
- **THEN** each truss cross-section on the `Trusses` layer consists of three 3D LINEs representing the sloped rafter, bottom chord, and vertical rise member
