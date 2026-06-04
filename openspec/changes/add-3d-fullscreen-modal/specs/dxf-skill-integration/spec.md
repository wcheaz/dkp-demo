## MODIFIED Requirements

### Requirement: DXF builder API reference doc
The skill's references directory SHALL contain a file `references/dxf-builder-api.md` documenting the `build_dxf` function's signature, input parameters (mapped from `DesignParameters` fields), output format (R2000 DXF bytes), and the DXF layers with their entity types. The reference SHALL be loadable via the skill's `read_skill_resource` mechanism. It SHALL explicitly document that `DIMENSION` entities are excluded to prevent 3D WebGL renderer crashes, and standard `TEXT` or `MTEXT` entities placed on the `Labels` layer are used instead.

#### Scenario: Agent loads DXF builder reference
- **WHEN** the agent calls `read_skill_resource("run-generate-design", "references/dxf-builder-api.md")`
- **THEN** the returned content SHALL contain the `build_dxf` function signature, the mapping from `DesignParameters` fields to DXF content, and the layer schema showing that `Labels` and `Dimensions` layers use standard `TEXT` or `MTEXT` primitives instead of `DIMENSION` objects for 3D compatibility
