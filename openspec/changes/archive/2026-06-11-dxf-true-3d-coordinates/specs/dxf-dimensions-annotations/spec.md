## MODIFIED Requirements

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
- **THEN** no ridge height text is added to the `Labels` layer

### Requirement: Text labels for key measurements

The module SHALL add `TEXT` entities on a layer named `Labels` (user-facing labels). All label placement coordinates SHALL be placed at their true coordinates (e.g. Z=0). Labels SHALL include "Width: <W>m", "Depth: <D>m", and for pitched roofs "Ridge Height: <H>m".

#### Scenario: Text labels on 10x15m gable building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the `Labels` layer contains `TEXT` entities positioned at true 3D coordinates, including content for width, depth, and ridge height
