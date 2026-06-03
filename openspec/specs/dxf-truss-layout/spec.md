## Purpose

Truss layout module for computing and drawing truss cross-sections on the `Trusses` layer of DXF drawings.

## Requirements

### Requirement: Truss count derived from floor area

The module SHALL compute `total_trusses` as `round(width_m * depth_m * 0.147)` where `width_m` and `depth_m` are the parsed floor-plan dimensions in meters. `total_trusses` SHALL be at least 2.

#### Scenario: Truss count for 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the computed `total_trusses` equals `round(10 * 15 * 0.147)` = `round(22.05)` = 22

#### Scenario: Minimum truss count
- **WHEN** `build_dxf` is called with `floorPlanDimensions="2x3m"`
- **THEN** the computed `total_trusses` is at least 2 (even though `round(2*3*0.147)` = 1)

### Requirement: Truss cross-sections on Trusses layer

The module SHALL draw truss cross-sections as 3D LINE entities on a layer named `Trusses`. Each truss SHALL be placed at its actual Y-coordinate (or X-coordinate if the building is wider than deep) at Z=2700 (wall height level) and span in 3D up to the ridge height at Z=2700+ridge_height, spaced evenly with edge inset of 5% of the shorter dimension from each end.

#### Scenario: Gable truss cross-sections on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"` and `roofPitch=30`
- **THEN** the `Trusses` layer contains 3D LINE entities for each truss. Each truss consists of three 3D LINEs: two rafters connecting eave points at `(0, y, 2700)` and `(10000, y, 2700)` to the ridge point at `(5000, y, 2700+ridge_height)`, and a bottom chord connecting `(0, y, 2700)` to `(10000, y, 2700)`

#### Scenario: Flat truss cross-sections
- **WHEN** `build_dxf` is called with `roofType="Flat"`
- **THEN** each truss cross-section is a single horizontal 3D LINE connecting `(0, y, 2700)` to `(w, y, 2700)` on the `Trusses` layer

### Requirement: Ridge height calculated from roofPitch

For gable and hip roof types, the ridge height SHALL be calculated as `(width_mm / 2) * tan(roofPitch * pi / 180)`. If `roofPitch` is None or 0, default values SHALL be: 30 degrees for gable/hip, 10 degrees for mono-pitch.

#### Scenario: Gable ridge height with 30-degree pitch
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, `roofPitch=30`
- **THEN** the ridge height used for each truss cross-section equals `(10000/2) * tan(30*pi/180)` = 2887mm (rounded to nearest mm)

#### Scenario: Default pitch when roofPitch is None
- **WHEN** `build_dxf` is called with `roofType="Gable"` and `roofPitch=None`
- **THEN** the ridge height is computed using a default pitch of 30 degrees

### Requirement: Mono-pitch truss cross-section

For `roofType="Mono-pitch"`, each truss cross-section SHALL be a 3D right triangle with one rafter sloping from the low-side eave `(0, y, 2700)` to the high-side ridge `(w, y, 2700+ridge_height)`, a horizontal bottom chord at Z=2700, and a vertical rise line on the high side from Z=2700 to Z=2700+ridge_height.

#### Scenario: Mono-pitch cross-section
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Mono-pitch"`
- **THEN** each truss cross-section on the `Trusses` layer consists of three 3D LINEs representing the sloped rafter, bottom chord, and vertical rise member at Z=2700
