## Purpose

Title block module for drawing a title block rectangle and project metadata on the `Title_Block` layer of DXF drawings.

## Requirements

### Requirement: Title block rectangle on Title_Block layer

The module SHALL draw a rectangle (40000 x 15000 mm) in the lower-right area of the drawing as four LINE entities on a layer named `Title_Block`. The rectangle SHALL be positioned so its right edge aligns with the building's right edge plus 20% margin, and its bottom edge aligns with the building's bottom edge minus the dimension offset minus a gap of 5000mm.

#### Scenario: Title block position on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Title_Block` layer contains exactly 4 LINE entities forming a 40000 x 15000 mm rectangle positioned to the lower-right of the building geometry

### Requirement: Project metadata text in title block

The module SHALL place MTEXT entities inside the title block rectangle on the `Title_Block` layer with the following content, each on a separate line or as separate MTEXT entities:
- `buildingType` (if not None, else "Building")
- `location` (if not None, else "Location not specified")
- Current UTC date formatted as YYYY-MM-DD
- Floor plan dimensions as "Plan: <W>x<D>m"
- Roof type as "Roof: <type>"

Text height SHALL be 800mm.

#### Scenario: Full metadata with all fields
- **WHEN** `build_dxf` is called with `buildingType="Residential"`, `location="Bratislava"`, `floorPlanDimensions="10x15m"`, `roofType="Gable"`
- **THEN** the `Title_Block` layer contains MTEXT entities including "Residential", "Bratislava", a date string matching pattern `\d{4}-\d{2}-\d{2}`, "Plan: 10x15m", and "Roof: Gable"

#### Scenario: Metadata with None fields
- **WHEN** `build_dxf` is called with `buildingType=None` and `location=None`
- **THEN** the `Title_Block` layer MTEXT includes "Building" (fallback for buildingType) and "Location not specified" (fallback for location), while still showing the date, plan, and roof type

### Requirement: Title block does not crash on missing optional fields

If `buildingType`, `location`, `overhang`, or `atticUsage` is None, the title block SHALL still render with fallback text values. No ValueError or exception SHALL be raised due to missing optional fields.

#### Scenario: All optional fields are None
- **WHEN** `build_dxf` is called with a `DesignParameters` where all optional fields except `floorPlanDimensions` and `roofType` are None
- **THEN** the title block renders with fallback values and `build_dxf` returns valid DXF bytes
