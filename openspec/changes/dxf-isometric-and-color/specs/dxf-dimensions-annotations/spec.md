## MODIFIED Requirements

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

### Requirement: Text labels for key measurements

The module SHALL add TEXT entities on a layer named `Labels` (user-facing labels). All label placement coordinates SHALL be projected onto the 2D isometric plane using the isometric formula. Labels SHALL include "Width: <W>m", "Depth: <D>m", and for pitched roofs "Ridge Height: <H>m".

#### Scenario: Text labels on 10x15m gable building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the `Labels` layer contains TEXT entities positioned at projected 2D isometric coordinates, including content for width, depth, and ridge height
