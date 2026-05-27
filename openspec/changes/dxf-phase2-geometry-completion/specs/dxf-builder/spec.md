## MODIFIED Requirements

### Requirement: DXF output is valid and re-readable

The `build_dxf` function SHALL produce DXF content that can be re-read by `ezdxf.read()` without errors. The DXF version SHALL be AC1015 (R2000). The output SHALL include five layers: `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, and `Title_Block`.

#### Scenario: Valid DXF from basic parameters
- **WHEN** `build_dxf` is called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, and `roofPitch=30`
- **THEN** the returned bytes can be passed to `ezdxf.read(BytesIO(result))` without raising an exception, the document's DXF version is AC1015, and the document contains exactly the layers `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, and `Title_Block`

#### Scenario: Valid DXF from flat roof with minimal parameters
- **WHEN** `build_dxf` is called with `floorPlanDimensions="8x12m"`, `roofType="Flat"`, `roofPitch=None`
- **THEN** the returned bytes are valid DXF with all five layers present, and the `Trusses` layer contains horizontal LINE entities (flat trusses), the `Dimensions` layer contains width and depth dimensions, and the `Title_Block` layer contains the border rectangle and metadata text
