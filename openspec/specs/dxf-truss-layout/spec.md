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

The module SHALL draw truss cross-sections as LINE entities on a layer named `Trusses`. Each cross-section SHALL be placed at a Y-coordinate (if building is wider than deep, X-coordinate) along the longer axis, spaced evenly with edge inset of 5% of the shorter dimension from each end.

#### Scenario: Gable truss cross-sections on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"` and `roofPitch=30`
- **THEN** the `Trusses` layer contains LINE entities for each truss cross-section. Each cross-section consists of three LINEs forming an isosceles triangle: two rafters from eave points to ridge point, plus a tie-beam connecting the eave points. The first truss is inset by 500mm (5% of 10000mm) from the building edge.

#### Scenario: Flat truss cross-sections
- **WHEN** `build_dxf` is called with `roofType="Flat"`
- **THEN** each truss cross-section is a single horizontal LINE (tie-beam only) on the `Trusses` layer

### Requirement: Ridge height calculated from roofPitch

For gable and hip roof types, the ridge height SHALL be calculated as `(width_mm / 2) * tan(roofPitch * pi / 180)`. If `roofPitch` is None or 0, default values SHALL be: 30 degrees for gable/hip, 10 degrees for mono-pitch.

#### Scenario: Gable ridge height with 30-degree pitch
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, `roofPitch=30`
- **THEN** the ridge height used for each truss cross-section equals `(10000/2) * tan(30*pi/180)` = 2887mm (rounded to nearest mm)

#### Scenario: Default pitch when roofPitch is None
- **WHEN** `build_dxf` is called with `roofType="Gable"` and `roofPitch=None`
- **THEN** the ridge height is computed using a default pitch of 30 degrees

### Requirement: Mono-pitch truss cross-section

For `roofType="Mono-pitch"`, each truss cross-section SHALL be a right triangle with one rafter sloping from the low-side eave to the high-side ridge, a horizontal tie-beam, and a vertical rise on the high side.

#### Scenario: Mono-pitch cross-section
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Mono-pitch"`
- **THEN** each truss cross-section on the `Trusses` layer consists of three LINEs: a sloped rafter, a horizontal tie-beam, and a vertical line on the high side. The rise height is `(width_mm) * tan(10 * pi / 180)` using the default 10-degree pitch.
