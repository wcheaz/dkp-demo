## Purpose

Dimensions and annotations module for adding measurement dimensions and text labels to DXF drawings.

## Requirements

### Requirement: Linear dimension for building width

The module SHALL configure the `Dimensions` layer but SHALL NOT add any `DIMENSION` entities (to prevent 3D WebGL parser crashes). All measurement annotations SHALL instead be drawn as standard `TEXT` primitives on the `Labels` layer.

#### Scenario: Width dimension on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** no `DIMENSION` style entities are generated on the `Dimensions` layer, and the building width is annotated using a standard `TEXT` entity on the `Labels` layer

### Requirement: Linear dimension for building depth

The module SHALL configure the `Dimensions` layer but SHALL NOT add any `DIMENSION` entities (to prevent 3D WebGL parser crashes). All measurement annotations SHALL instead be drawn as standard `TEXT` primitives on the `Labels` layer.

#### Scenario: Depth dimension on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** no `DIMENSION` style entities are generated on the `Dimensions` layer, and the building depth is annotated using a standard `TEXT` entity on the `Labels` layer

### Requirement: Ridge height dimension for gable and hip roofs

For gable and hip roof types, the module SHALL configure the `Dimensions` layer but SHALL NOT add any `DIMENSION` entities. All measurement annotations SHALL instead be drawn as standard `TEXT` primitives on the `Labels` layer.

#### Scenario: Ridge height dimension for gable roof
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, `roofPitch=30`
- **THEN** the ridge height is annotated using a standard `TEXT` entity on the `Labels` layer

#### Scenario: No ridge height dimension for flat roof
- **WHEN** `build_dxf` is called with `roofType="Flat"`
- **THEN** no ridge height dimension is added to the `Dimensions` layer

### Requirement: Text labels for key measurements

The module SHALL add `TEXT` entities on a layer named `Labels` (user-facing labels). All label placement coordinates SHALL be placed at their true coordinates (e.g. Z=0). Labels SHALL include "Width: <W>m", "Depth: <D>m", and for pitched roofs "Ridge Height: <H>m".

#### Scenario: Text labels on 10x15m gable building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the `Labels` layer contains `TEXT` entities positioned at true 3D coordinates, including content for width, depth, and ridge height

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
