## Purpose

DXF builder module for generating 2D CAD drawings from building parameters.

## Requirements

### Requirement: DXF output is valid and re-readable

The `build_dxf` function SHALL produce DXF content that can be re-read by `ezdxf.read()` without errors. The DXF version SHALL be AC1015 (R2000). The output SHALL include five layers: `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, and `Title_Block`.

#### Scenario: Valid DXF from basic parameters
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, and `roofPitch=30`
- **THEN** the returned bytes can be passed to `ezdxf.read(BytesIO(result))` without raising an exception, the document's DXF version is AC1015, and the document contains exactly the layers `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, and `Title_Block`

#### Scenario: Valid DXF from flat roof with minimal parameters
- **WHEN** `build_dxf` is called with `floorPlanDimensions="8x12m"`, `roofType="Flat"`, `roofPitch=None`
- **THEN** the returned bytes are valid DXF with all five layers present, and the `Trusses` layer contains horizontal LINE entities (flat trusses), the `Dimensions` layer contains width and depth dimensions, and the `Title_Block` layer contains the border rectangle and metadata text

### Requirement: Floor-plan outline drawn on Floor_Plan layer

The module SHALL parse `floorPlanDimensions` (format: `"<width>x<depth>m"`), convert to millimeters, and draw a closed LWPOLYLINE rectangle on a layer named `Floor_Plan`. The rectangle SHALL start at origin (0, 0) with width along X and depth along Y.

#### Scenario: 10x15m floor plan
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Floor_Plan` layer contains exactly one LWPOLYLINE with 4 vertices at (0,0), (10000,0), (10000,15000), (0,15000) (closed)

#### Scenario: Dimensions with decimals
- **WHEN** `build_dxf` is called with `floorPlanDimensions="8.5x12.3m"`
- **THEN** the `Floor_Plan` layer LWPOLYLINE has vertices at (0,0), (8500,0), (8500,12300), (0,12300)

### Requirement: Invalid floorPlanDimensions raises ValueError

If `floorPlanDimensions` is `None` or cannot be parsed by the regex `r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?"`, the function SHALL raise `ValueError`.

#### Scenario: None dimensions
- **WHEN** `build_dxf` is called with `floorPlanDimensions=None`
- **THEN** `ValueError` is raised

#### Scenario: Malformed dimensions string
- **WHEN** `build_dxf` is called with `floorPlanDimensions="about twenty meters"`
- **THEN** `ValueError` is raised

### Requirement: Gable roof outline on Roof_Outline layer

For `roofType="Gable"`, the module SHALL draw a ridge line on the `Roof_Outline` layer. The ridge SHALL run parallel to the longer axis, centered on the building. Ridge endpoints SHALL be at the midpoint of each long side.

#### Scenario: Gable roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the `Roof_Outline` layer contains LINE entities forming a gable: two rafter lines from eave corners converging at the ridge midpoint, and the ridge line itself along the Y-axis center at x=5000

### Requirement: Hip roof outline on Roof_Outline layer

For `roofType="Hip"`, the module SHALL draw a ridge line (shorter than the building length) and hip lines connecting ridge endpoints to the building corners. Ridge length SHALL equal building length minus building width.

#### Scenario: Hip roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Hip"`
- **THEN** the `Roof_Outline` layer contains LINE entities for the ridge (length = 15000 - 10000 = 5000mm, centered) and four hip lines from ridge endpoints to the four building corners

### Requirement: Mono-pitch roof outline on Roof_Outline layer

For `roofType="Mono-pitch"`, the module SHALL draw the roof outline as the same rectangle as the floor plan on the `Roof_Outline` layer, with a marker line indicating the high side.

#### Scenario: Mono-pitch roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Mono-pitch"`
- **THEN** the `Roof_Outline` layer contains an LWPOLYLINE matching the floor plan rectangle and a LINE on the high side (one of the long edges)

### Requirement: Flat roof outline on Roof_Outline layer

For `roofType="Flat"`, the module SHALL draw the roof outline as a closed LWPOLYLINE matching the floor plan rectangle on the `Roof_Outline` layer.

#### Scenario: Flat roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Flat"`
- **THEN** the `Roof_Outline` layer contains exactly one closed LWPOLYLINE with the same 4 vertices as the floor plan

### Requirement: Unknown roof type raises ValueError

If `roofType` is `None` or not one of `Gable`, `Hip`, `Mono-pitch`, `Flat` (case-insensitive), the function SHALL raise `ValueError`.

#### Scenario: None roof type
- **WHEN** `build_dxf` is called with `roofType=None`
- **THEN** `ValueError` is raised

#### Scenario: Unsupported roof type
- **WHEN** `build_dxf` is called with `roofType="Gambrel"`
- **THEN** `ValueError` is raised
