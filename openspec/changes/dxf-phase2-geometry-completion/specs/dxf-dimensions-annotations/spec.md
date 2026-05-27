## ADDED Requirements

### Requirement: Linear dimension for building width

The module SHALL add a horizontal linear dimension below the floor plan showing the building width. The dimension SHALL be placed on the `Dimensions` layer using `msp.add_linear_dim()` with an offset of 10% of the building depth below the floor-plan bottom edge.

#### Scenario: Width dimension on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Dimensions` layer contains a linear dimension entity measuring 10000mm (building width) placed below the floor plan at Y offset of approximately -1500mm (10% of 15000mm depth)

### Requirement: Linear dimension for building depth

The module SHALL add a vertical linear dimension to the left of the floor plan showing the building depth. The dimension SHALL be placed on the `Dimensions` layer with an offset of 10% of the building width to the left of the floor-plan left edge.

#### Scenario: Depth dimension on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Dimensions` layer contains a linear dimension entity measuring 15000mm (building depth) placed to the left of the floor plan at X offset of approximately -1000mm (10% of 10000mm width)

### Requirement: Ridge height dimension for gable and hip roofs

For gable and hip roof types, the module SHALL add a vertical linear dimension to the right of the first truss cross-section showing the ridge height. The dimension SHALL be on the `Dimensions` layer.

#### Scenario: Ridge height dimension for gable roof
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, `roofPitch=30`
- **THEN** the `Dimensions` layer contains a vertical linear dimension entity measuring the computed ridge height (approximately 2887mm) placed near the first truss cross-section

#### Scenario: No ridge height dimension for flat roof
- **WHEN** `build_dxf` is called with `roofType="Flat"`
- **THEN** no ridge height dimension is added to the `Dimensions` layer

### Requirement: Text labels for key measurements

The module SHALL add TEXT entities on the `Dimensions` layer labeling the building with "Width: <W>m", "Depth: <D>m", and for pitched roofs "Ridge Height: <H>m". Text height SHALL be 250mm.

#### Scenario: Text labels on 10x15m gable building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the `Dimensions` layer contains TEXT entities with content including "Width: 10m" and "Depth: 15m" and "Ridge Height: <H>m" (where H is the computed height in meters, rounded to 2 decimal places)

### Requirement: Overhang dimension when parseable

If `overhang` is provided and parseable as a numeric value (format: `"<number>m"` or `"<number>"`), the module SHALL add a horizontal dimension showing the overhang on one eave side, on the `Dimensions` layer. If unparseable or None, overhang dimension SHALL be omitted (no error raised).

#### Scenario: Overhang dimension with valid value
- **WHEN** `build_dxf` is called with `overhang="0.5m"`
- **THEN** the `Dimensions` layer contains a horizontal dimension entity measuring 500mm for the overhang

#### Scenario: No overhang dimension when None
- **WHEN** `build_dxf` is called with `overhang=None`
- **THEN** no overhang dimension is added and no error is raised
