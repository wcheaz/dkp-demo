## MODIFIED Requirements

### Requirement: Spatial hierarchy and unit configuration
The generated IFC file SHALL construct a standard spatial containment tree: `IfcProject` aggregates `IfcSite`, which aggregates `IfcBuilding`, which aggregates `IfcBuildingStorey`. The measurement unit system of the project SHALL be configured to millimeters (`.MILLI.`, `.METRE.`) for length, square meters for area, cubic meters for volume, and radians for plane angles. Individual `IfcMember` elements SHALL be aggregated under `IfcElementAssembly` containers, and only the assemblies and walls SHALL be directly linked to the `IfcBuildingStorey` spatial structure.

#### Scenario: Structural spatial hierarchy is correctly containment-linked
- **WHEN** the output IFC bytes are parsed or checked by a validator
- **THEN** all walls and truss assemblies SHALL be linked to the `IfcBuildingStorey` via an `IfcRelContainedInSpatialStructure` relationship.
- **AND** all timber members SHALL be aggregated under their respective `IfcElementAssembly` via an `IfcRelAggregates` relationship rather than being placed directly in the building storey.

### Requirement: Timber members have structural classifications and property sets
The system SHALL classify the functional role of each generated `IfcMember` using the `ObjectType` attribute and populate it with standard property sets detailing wood grade and pricing metadata (such as wood treatment). It SHALL also serialize the wood grade and dimensions in the format `"Grade ThicknessxWidth"` (e.g., `"C24 45x120"`) inside the member's `Description` attribute, and its index identifier (e.g. `"T21"`) in its `Name` attribute.

#### Scenario: Verify ObjectType and property sets on timber members
- **WHEN** the IFC file is generated
- **THEN** every generated `IfcMember` SHALL have its `ObjectType` attribute set to a functional role (such as `"TOP_CHORD"`, `"BOTTOM_CHORD"`, `"WEB"`, or `"PLATE"`)
- **AND** its `Description` attribute SHALL contain the grade and dimension string in the format `"Grade ThicknessxWidth"` (e.g., `"C24 45x120"`)
- **AND** its `Name` attribute SHALL contain the member serial label (e.g. `"T21"`, `"B1"`)
- **AND** it SHALL have an associated property set containing wood grade (`Grade`) and treatment properties (`IsTreated`)
