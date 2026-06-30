## Purpose

Defines the client-side IFC parsing capabilities of the CAD viewer (in `src/app/cad-viewer-3d/page.tsx`), including boundary representation geometry parsing, arbitrary closed profile extrusion handling, and recursive coordinate transformation resolution for correctly positioning nested members.

## Requirements

### Requirement: Client-side parsing of B-Rep geometry
The client-side IFC parser (`parseIfcToDxf` in `src/app/cad-viewer-3d/page.tsx`) SHALL parse boundary representation (`IFCFACETEDBREP` and `IFCCLOSEDSHELL`) entities. It SHALL extract the absolute 3D vertex coordinates from the linked `IFCPOLYLOOP` entities and output them as lines or faces in the parsed DXF output.

#### Scenario: IFC file with member using B-Rep geometry is successfully parsed
- **WHEN** an IFC file containing an `IFCMEMBER` with a representation shape pointing to an `IFCFACETEDBREP` shell is uploaded
- **THEN** the parser SHALL extract all polyloop vertex coordinate points
- **AND** output corresponding 3D segments to the final DXF entities string

### Requirement: Client-side parsing of arbitrary closed profile extrusions
The client-side IFC parser (`parseIfcToDxf` in `src/app/cad-viewer-3d/page.tsx`) SHALL parse arbitrary closed profiles (`IFCARBITRARYCLOSEDPROFILEDEF`). It SHALL resolve the polyline path defined by the composite curves (`IFCCOMPOSITECURVE`) and project the 2D vertices along the extrusion axis by the specified depth to generate the 3D geometry.

#### Scenario: Wall with arbitrary profile is successfully parsed
- **WHEN** an IFC file containing an `IFCEXTRUDEDAREASOLID` pointing to an `IFCARBITRARYCLOSEDPROFILEDEF` is parsed
- **THEN** the parser SHALL reconstruct the closed polyline shape from the composite curve segments
- **AND** sweep it along the local extrusion direction to generate the 3D vertex coordinates in the DXF

### Requirement: Recursive coordinate transformation resolution
The client-side placement resolver SHALL recursively traverse nested local placements (`IFCLOCALPLACEMENT` linking to parent placements via `PlacementRelTo` arguments). It SHALL accumulate these nested coordinate frames using matrix multiplication to compute the correct absolute global 3D position of each member.

#### Scenario: Nested member placement inside assembly is correctly positioned
- **WHEN** an `IFCMEMBER` placement is nested inside an `IFCELEMENTASSEMBLY` placement which has its own offset relative to the storey
- **THEN** the parser SHALL accumulate the local coordinate transformations recursively from the storey down to the member
- **AND** transform all member vertices using the final combined transformation matrix in the DXF
