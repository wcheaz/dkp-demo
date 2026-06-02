## MODIFIED Requirements

### Requirement: Text labels for key measurements

The module SHALL add TEXT entities on a layer named `Labels` (user-facing labels) rather than the technical specifications layer. Labels SHALL include "Width: <W>m", "Depth: <D>m", and for pitched roofs "Ridge Height: <H>m". Text height SHALL be 250mm.

#### Scenario: Text labels on 10x15m gable building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the `Labels` layer contains TEXT entities with content including "Width: 10m" and "Depth: 15m" and "Ridge Height: <H>m" (where H is the computed height in meters, rounded to 2 decimal places)

## ADDED Requirements

### Requirement: Lumber specifications on Lumber_Specs layer

The module SHALL add MTEXT or TEXT entities on the `Lumber_Specs` layer detailing lumber grade (e.g., C24) and default cross-section dimensions (e.g., Thickness: 45 mm, Width: 120 mm) as a technical spec table or legend. These specifications SHALL be placed on a separate layer from standard user-facing labels to enable independent visibility toggling.

#### Scenario: Lumber specs generated on Lumber_Specs layer
- **WHEN** `build_dxf` is called
- **THEN** the `Lumber_Specs` layer contains annotations specifying the C24 lumber grade and dimensions
