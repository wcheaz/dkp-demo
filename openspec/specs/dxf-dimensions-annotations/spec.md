## Purpose

Dimensions and annotations module for adding measurement dimensions and text labels to DXF drawings.

## Requirements

### Requirement: Linear dimension for building width

The module SHALL add a linear dimension showing the building width. The dimension points (p1, p2, and base) SHALL be projected onto the 2D isometric plane using the isometric formula before adding the dimension to the `Dimensions` layer.

#### Scenario: Width dimension on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Dimensions` layer contains a linear dimension entity measuring 10000mm whose point properties are mapped using the isometric projection helper

### Requirement: Linear dimension for building depth

The module SHALL add a linear dimension showing the building depth. The dimension points (p1, p2, and base) SHALL be projected onto the 2D isometric plane using the isometric formula before adding the dimension to the `Dimensions` layer.

#### Scenario: Depth dimension on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Dimensions` layer contains a linear dimension entity measuring 15000mm whose point properties are mapped using the isometric projection helper

### Requirement: Ridge height dimension for gable and hip roofs

For gable and hip roof types, the module SHALL add a vertical linear dimension to the right of the first truss cross-section showing the ridge height. The dimension SHALL be on the `Dimensions` layer.

#### Scenario: Ridge height dimension for gable roof
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, `roofPitch=30`
- **THEN** the `Dimensions` layer contains a vertical linear dimension entity measuring the computed ridge height (approximately 2887mm) placed near the first truss cross-section

#### Scenario: No ridge height dimension for flat roof
- **WHEN** `build_dxf` is called with `roofType="Flat"`
- **THEN** no ridge height dimension is added to the `Dimensions` layer

### Requirement: Text labels for key measurements

The module SHALL add TEXT entities on a layer named `Labels` (user-facing labels). All label placement coordinates SHALL be projected onto the 2D isometric plane using the isometric formula. Labels SHALL include "Width: <W>m", "Depth: <D>m", and for pitched roofs "Ridge Height: <H>m".

#### Scenario: Text labels on 10x15m gable building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the `Labels` layer contains TEXT entities positioned at projected 2D isometric coordinates, including content for width, depth, and ridge height

### Requirement: Overhang dimension when parseable

If `overhang` is provided and parseable as a numeric value (format: `"<number>m"` or `"<number>"`), the module SHALL add a horizontal dimension showing the overhang on one eave side, on the `Dimensions` layer. If unparseable or None, overhang dimension SHALL be omitted (no error raised).

#### Scenario: Overhang dimension with valid value
- **WHEN** `build_dxf` is called with `overhang="0.5m"`
- **THEN** the `Dimensions` layer contains a horizontal dimension entity measuring 500mm for the overhang

#### Scenario: No overhang dimension when None
- **WHEN** `build_dxf` is called with `overhang=None`
- **THEN** no overhang dimension is added and no error is raised

### Requirement: Lumber specifications on Lumber_Specs layer

The module SHALL add MTEXT or TEXT entities on the `Lumber_Specs` layer detailing lumber grade (e.g., C24) and default cross-section dimensions (e.g., Thickness: 45 mm, Width: 120 mm) as a technical spec table or legend. These specifications SHALL be placed on a separate layer from standard user-facing labels to enable independent visibility toggling.

#### Scenario: Lumber specs generated on Lumber_Specs layer
- **WHEN** `build_dxf` is called
- **THEN** the `Lumber_Specs` layer contains annotations specifying the C24 lumber grade and dimensions
