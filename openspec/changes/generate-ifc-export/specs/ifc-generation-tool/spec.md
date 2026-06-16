## ADDED Requirements

### Requirement: ifc_builder module builds valid IFC2x3 models
The Python module `agent.src.ifc_builder` SHALL provide a function `build_ifc(params: DesignParameters) -> bytes` that parses design parameters and builds a valid 3D IFC model in the IFC2x3 schema format. The output bytes SHALL be valid ISO-10303-21 text formatting containing a complete BIM spatial hierarchy.

#### Scenario: Valid inputs generate complete IFC2x3 model
- **WHEN** `build_ifc` is invoked with valid parameters (`{"floorPlanDimensions": "10x15m", "roofType": "Gable", "roofPitch": 30}`)
- **THEN** it SHALL return a non-empty `bytes` object
- **AND** the bytes content SHALL contain the schema identifier `FILE_SCHEMA(('IFC2X3'));`
- **AND** it SHALL contain `IfcProject`, `IfcSite`, `IfcBuilding`, `IfcBuildingStorey`, `IfcWallStandardCase`, and `IfcMember` entities.

### Requirement: Spatial hierarchy and unit configuration
The generated IFC file SHALL construct a standard spatial containment tree: `IfcProject` aggregates `IfcSite`, which aggregates `IfcBuilding`, which aggregates `IfcBuildingStorey`. The measurement unit system of the project SHALL be configured to millimeters (`.MILLI.`, `.METRE.`) for length, square meters for area, cubic meters for volume, and radians for plane angles.

#### Scenario: Structural spatial hierarchy is correctly containment-linked
- **WHEN** the output IFC bytes are parsed or checked by a validator
- **THEN** all walls and timber members SHALL be linked to the `IfcBuildingStorey` via an `IfcRelContainedInSpatialStructure` relationship.

### Requirement: Swept solid member geometry
All structural timber members (chords, webs) in the IFC file SHALL be represented geometrically using extruded rectangular profiles (`IfcRectangleProfileDef`) swept along their longitudinal local placement axis (`IfcExtrudedAreaSolid`). The profile name attribute SHALL represent nominal timber sizing in the format `"ThicknessxWidth"` (e.g. `"45x120"`).

#### Scenario: Members are rendered as parametric swept solids
- **WHEN** the output IFC contains `IfcMember` or `IfcBeam` objects
- **THEN** their representation geometry SHALL point to an `IfcExtrudedAreaSolid` sweeping a centered `IfcRectangleProfileDef`.

### Requirement: Shared geometry coordinates layout
The layout coordinates, spans, height calculations, and pitch intersections SHALL be computed by a shared geometry utility module (e.g. `agent.src.geometry_solver`). Both the DXF drawing builder (`agent.src.dxf_builder`) and the IFC builder (`agent.src.ifc_builder`) SHALL consume the exact same coordinate calculations from this shared module to guarantee that the generated DXF and IFC files are geometrically congruent.

#### Scenario: DXF and IFC builders consume same shared coordinates
- **WHEN** a truss design is exported to both DXF and IFC formats
- **THEN** the coordinates of the chord joints and member lengths in both files SHALL be calculated by the same shared helper function.
