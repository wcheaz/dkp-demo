## Purpose

Defines the backend IFC generator integration with Pamir pricing and structural metadata, including the grouping of timber members into `IfcElementAssembly` truss containers, attachment of custom Pamir property sets (Frame, Member), and generation of virtual support point proxies for connection hardware cost estimation.

## Requirements

### Requirement: Organize generated timber members in IfcElementAssembly containers
The backend IFC generator SHALL group individual `IfcMember` elements (top chords, bottom chords, webs) into distinct `IfcElementAssembly` structural containers representing roof truss frames. The assembly's `PredefinedType` SHALL be set to `.TRUSS.` and its `AssemblyPlace` set to `.FACTORY.`.

#### Scenario: Verify IfcElementAssembly containment in generated IFC
- **WHEN** the backend generates the IFC file for a truss design
- **THEN** it SHALL output `IfcElementAssembly` entities with the PredefinedType `.TRUSS.`
- **AND** it SHALL link the relevant `IfcMember` entities to the assembly using `IfcRelAggregates` relationships
- **AND** only the assembly itself SHALL be placed directly in the building storey spatial container

### Requirement: Include custom Pamir Frame pricing property set on assemblies
The backend IFC generator SHALL attach a custom `IfcPropertySet` named `"Pamir Frame"` to each generated `IfcElementAssembly`. This property set SHALL define the physical `Weight` (in kg), structural engineering validation status `DesignResultType` (string), and `ProductionSet` (string batch code).

#### Scenario: Verify Pamir Frame property set on assembly
- **WHEN** the generated IFC contains an `IfcElementAssembly`
- **THEN** it SHALL associate the assembly with an `IfcPropertySet` named `"Pamir Frame"`
- **AND** the property set SHALL define a `Weight` property containing the computed mass in kilograms
- **AND** a `DesignResultType` property set to `"Success"`
- **AND** a `ProductionSet` property set to `"1"`

### Requirement: Generate virtual support points for connectors cost estimation
The backend IFC generator SHALL place `IfcBuildingElementProxy` entities at wall bearing zones where trusses rest. These proxies SHALL be associated with a `"Pamir Support"` property set containing `SupportType` (e.g. `"WoodWall"`, `"Concrete"`, or `"BeamHanger"`) and `SupportFace` (e.g. `"Bottom"`) to allow cost estimation of connection hardware.

#### Scenario: Verify support points and support property set
- **WHEN** the IFC is generated for a design with bearing walls
- **THEN** it SHALL output `IfcBuildingElementProxy` entities representing support connection points at the intersection of bottom chords and wall plates
- **AND** these proxies SHALL be associated with a `"Pamir Support"` property set specifying the support type and face attributes

### Requirement: Include custom Pamir Member fixed states property set
The backend IFC generator SHALL associate each `IfcMember` with an `IfcPropertySet` named `"Pamir Member"` containing the `SiteFixed` boolean property to denote whether the member is prefabricated or cut on-site.

#### Scenario: Verify SiteFixed property on members
- **WHEN** the generated IFC contains `IfcMember` elements
- **THEN** they SHALL have an associated `"Pamir Member"` property set defining `SiteFixed` as a boolean property
