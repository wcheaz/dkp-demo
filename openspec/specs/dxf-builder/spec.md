## Purpose

DXF builder module for generating 2D CAD drawings from building parameters.

## Requirements

### Requirement: DXF output is valid and re-readable

The `build_dxf` function SHALL produce DXF content that can be re-read by `ezdxf.read()` without errors. The DXF version SHALL be AC1018 (R2004). The output SHALL include seven layers: `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, `Title_Block`, `Wall_Centerlines`, and `Lumber_Specs`. All layers SHALL have a specified AutoCAD Color Index (ACI) integer color code configured.

#### Scenario: Valid DXF from basic parameters
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, and `roofPitch=30`
- **THEN** the returned bytes can be passed to `ezdxf.read(BytesIO(result))` without raising an exception, the document's DXF version is AC1018, the document contains all seven layers, and each layer has a non-zero ACI color code (e.g. `color` property) set

#### Scenario: Valid DXF from flat roof with minimal parameters
- **WHEN** `build_dxf` is called with `floorPlanDimensions="8x12m"`, `roofType="Flat"`, `roofPitch=None`
- **THEN** the returned bytes are valid DXF with all seven layers present, and the `Trusses` layer contains horizontal LINE entities at projected 2D isometric coordinates, the `Dimensions` layer contains dimensions, and the `Title_Block` layer contains the border rectangle and metadata text

### Requirement: Floor-plan outline drawn on Floor_Plan layer

The module SHALL parse `floorPlanDimensions` (format: `"<width>x<depth>m"`), convert to millimeters, and draw a 2D isometric projection of the 3D wall box on a layer named `Floor_Plan`. The wall box SHALL consist of a bottom rectangle at Z=0, a top rectangle at Z=2700 (default wall height), and four vertical corner lines connecting Z=0 and Z=2700. All coordinates SHALL be projected to the 2D plane using the isometric formula: $X_{iso} = (X - Y) \cdot \cos(30^\circ)$ and $Y_{iso} = (X + Y) \cdot \sin(30^\circ) + Z$.

#### Scenario: 10x15m floor plan
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Floor_Plan` layer contains projected LINE entities representing the bottom ring, top ring, and vertical corner connections of a 10000x15000x2700 wall box

#### Scenario: Dimensions with decimals
- **WHEN** `build_dxf` is called with `floorPlanDimensions="8.5x12.3m"`
- **THEN** the `Floor_Plan` layer contains projected LINE entities with coordinates derived from width 8500, depth 12300, and height 2700

### Requirement: Invalid floorPlanDimensions raises ValueError

If `floorPlanDimensions` is `None` or cannot be parsed by the regex `r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?"`, the function SHALL raise `ValueError`.

#### Scenario: None dimensions
- **WHEN** `build_dxf` is called with `floorPlanDimensions=None`
- **THEN** `ValueError` is raised

#### Scenario: Malformed dimensions string
- **WHEN** `build_dxf` is called with `floorPlanDimensions="about twenty meters"`
- **THEN** `ValueError` is raised

### Requirement: Gable roof outline on Roof_Outline layer

For `roofType="Gable"`, the module SHALL draw the roof framing projected to the 2D isometric plane on the `Roof_Outline` layer. The ridge line SHALL run parallel to the longer axis at Z=2700+ridge_height, centered on the building. Rafter lines SHALL connect the top corners of the walls at Z=2700 to the endpoints of the ridge line. All coordinates SHALL be projected to 2D using the isometric formula.

#### Scenario: Gable roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the `Roof_Outline` layer contains 2D LINE entities representing the ridge line (at Z=2700+ridge_height) and rafter lines projected isometrically

### Requirement: Hip roof outline on Roof_Outline layer

For `roofType="Hip"`, the module SHALL draw the hip roof framing projected to the 2D isometric plane on the `Roof_Outline` layer. The ridge line SHALL be at Z=2700+ridge_height (length equals building length minus building width, centered). Four hip lines SHALL connect the ridge endpoints to the four top wall corners at Z=2700. All coordinates SHALL be projected to 2D using the isometric formula.

#### Scenario: Hip roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Hip"`
- **THEN** the `Roof_Outline` layer contains 2D LINE entities representing the ridge line and hip lines projected isometrically

### Requirement: Mono-pitch roof outline on Roof_Outline layer

For `roofType="Mono-pitch"`, the module SHALL draw the roof outline projected to the 2D isometric plane on the `Roof_Outline` layer, sloping from Z=2700 on the low side to Z=2700+ridge_height on the high side. All coordinates SHALL be projected to 2D using the isometric formula.

#### Scenario: Mono-pitch roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Mono-pitch"`
- **THEN** the `Roof_Outline` layer contains 2D LINE entities representing the sloped roof frame projected isometrically

### Requirement: Flat roof outline on Roof_Outline layer

For `roofType="Flat"`, the module SHALL draw the roof outline projected to the 2D isometric plane on the `Roof_Outline` layer as a rectangle at Z=2700. All coordinates SHALL be projected to 2D using the isometric formula.

#### Scenario: Flat roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Flat"`
- **THEN** the `Roof_Outline` layer contains 2D LINE entities representing the flat roof perimeter at Z=2700 projected isometrically

### Requirement: Unknown roof type raises ValueError

If `roofType` is `None` or not one of `Gable`, `Hip`, `Mono-pitch`, `Flat` (case-insensitive), the function SHALL raise `ValueError`.

#### Scenario: None roof type
- **WHEN** `build_dxf` is called with `roofType=None`
- **THEN** `ValueError` is raised

#### Scenario: Unsupported roof type
- **WHEN** `build_dxf` is called with `roofType="Gambrel"`
- **THEN** `ValueError` is raised

### Requirement: Wall centerlines drawn on Wall_Centerlines layer

The module SHALL draw the centerline vectors of all structural walls on a dedicated `Wall_Centerlines` layer. The centerline rectangle SHALL be placed at Z=0 representing the wall midpoints (with no thickness offset).

#### Scenario: Centerline rectangle generated
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Wall_Centerlines` layer contains a closed rectangle of dimensions 10000x15000 at Z=0
