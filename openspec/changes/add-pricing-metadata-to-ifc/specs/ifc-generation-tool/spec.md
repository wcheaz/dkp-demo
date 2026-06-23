## ADDED Requirements

### Requirement: Timber members have structural classifications and property sets
The system SHALL classify the functional role of each generated `IfcMember` using the `ObjectType` attribute and populate it with standard property sets detailing wood grade and pricing metadata (such as wood treatment).

#### Scenario: Verify ObjectType and property sets on timber members
- **WHEN** the IFC file is generated
- **THEN** every generated `IfcMember` SHALL have its `ObjectType` attribute set to a functional role (such as `"TOP_CHORD"`, `"BOTTOM_CHORD"`, `"WEB"`, or `"PLATE"`)
- **AND** it SHALL have an associated property set containing wood grade (`Grade`) and treatment properties (`IsTreated`)
