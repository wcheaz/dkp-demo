## MODIFIED Requirements

### Requirement: DXF output is valid and re-readable

The `build_dxf` function SHALL produce DXF content that can be re-read by `ezdxf.read()` without errors. The DXF version SHALL be AC1018 (R2004). The output SHALL include seven layers: `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, `Title_Block`, `Wall_Centerlines`, and `Lumber_Specs`.

#### Scenario: Valid DXF from basic parameters
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, and `roofPitch=30`
- **THEN** the returned bytes can be passed to `ezdxf.read(BytesIO(result))` without raising an exception, the document's DXF version is AC1018, and the document contains the layers `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, `Title_Block`, `Wall_Centerlines`, and `Lumber_Specs`

#### Scenario: Valid DXF from flat roof with minimal parameters
- **WHEN** `build_dxf` is called with `floorPlanDimensions="8x12m"`, `roofType="Flat"`, `roofPitch=None`
- **THEN** the returned bytes are valid DXF with all seven layers present, and the `Trusses` layer contains horizontal LINE entities at 3D elevation, the `Dimensions` layer contains width and depth dimensions, and the `Title_Block` layer contains the border rectangle and metadata text

### Requirement: Floor-plan outline drawn on Floor_Plan layer

The module SHALL parse `floorPlanDimensions` (format: `"<width>x<depth>m"`), convert to millimeters, and draw a 3D wall outline on a layer named `Floor_Plan`. The outline SHALL consist of a bottom closed rectangle at Z=0, a top closed rectangle at Z=2700 (default wall height), and four vertical LINE entities at the corners connecting Z=0 and Z=2700.

#### Scenario: 10x15m floor plan
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Floor_Plan` layer contains a bottom rectangle with vertices at Z=0, a top rectangle with vertices at Z=2700, and four vertical corner lines from Z=0 to Z=2700

#### Scenario: Dimensions with decimals
- **WHEN** `build_dxf` is called with `floorPlanDimensions="8.5x12.3m"`
- **THEN** the `Floor_Plan` layer contains a bottom rectangle at Z=0 and a top rectangle at Z=2700 with X bounds from 0 to 8500 and Y bounds from 0 to 12300

### Requirement: Gable roof outline on Roof_Outline layer

For `roofType="Gable"`, the module SHALL draw the roof framing in 3D on the `Roof_Outline` layer. The ridge line SHALL run parallel to the longer axis at Z=2700+ridge_height, centered on the building. Four hip/ridge rafter lines SHALL connect the top corners of the walls at Z=2700 to the endpoints of the ridge line.

#### Scenario: Gable roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the `Roof_Outline` layer contains 3D LINE entities: a ridge line at X=5000 and Z=2700+ridge_height, and rafter lines connecting the wall corners at Z=2700 to the ridge endpoints

### Requirement: Hip roof outline on Roof_Outline layer

For `roofType="Hip"`, the module SHALL draw the hip roof framing in 3D on the `Roof_Outline` layer. The ridge line SHALL be at Z=2700+ridge_height (length equals building length minus building width, centered). Four hip lines SHALL connect the ridge endpoints to the four top wall corners at Z=2700.

#### Scenario: Hip roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Hip"`
- **THEN** the `Roof_Outline` layer contains 3D LINE entities: a ridge line at Z=2700+ridge_height, and four hip lines connecting ridge endpoints to the top wall corners at Z=2700

### Requirement: Mono-pitch roof outline on Roof_Outline layer

For `roofType="Mono-pitch"`, the module SHALL draw the roof outline in 3D on the `Roof_Outline` layer, sloping from Z=2700 on the low side to Z=2700+ridge_height on the high side.

#### Scenario: Mono-pitch roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Mono-pitch"`
- **THEN** the `Roof_Outline` layer contains 3D LINE entities forming a sloped rectangular plane from Z=2700 to Z=2700+ridge_height

### Requirement: Flat roof outline on Roof_Outline layer

For `roofType="Flat"`, the module SHALL draw the roof outline in 3D on the `Roof_Outline` layer as a closed rectangle at Z=2700.

#### Scenario: Flat roof on 10x15m building
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"` and `roofType="Flat"`
- **THEN** the `Roof_Outline` layer contains exactly one closed rectangle at Z=2700

## ADDED Requirements

### Requirement: Wall centerlines drawn on Wall_Centerlines layer

The module SHALL draw the centerline vectors of all structural walls on a dedicated `Wall_Centerlines` layer. The centerline rectangle SHALL be placed at Z=0 representing the wall midpoints (with no thickness offset).

#### Scenario: Centerline rectangle generated
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`
- **THEN** the `Wall_Centerlines` layer contains a closed rectangle of dimensions 10000x15000 at Z=0
