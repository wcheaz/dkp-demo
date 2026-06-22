## Context

Currently, the IFC file generation implementation in [ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py) outputs walls and structural members, but none of the structural members have material definitions associated with them. For integration with structural software such as MiTek Pamir, adding material information (such as wood/lumber grade `"Timber - C24"`) is highly beneficial. 

This design specifies how to add a static material definition to all `IfcMember` instances in the generated IFC model, using standard IFC2x3 semantics.

## Goals / Non-Goals

**Goals:**
- Associate a static material named `"Timber - C24"` with all generated `IfcMember` entities.
- Ensure the material definition is correctly linked using standard `IfcMaterial` and `IfcRelAssociatesMaterial` entities.
- Add code comments describing how this could be extended to support variable materials via `DesignParameters` in the future.

**Non-Goals:**
- Dynamically changing the material from the API payload (e.g., via a query parameter) in this phase.
- Adding material layers, styles, textures, or structural properties (like density, strength classes, elastic modulus) to the material definition.
- Associating materials with `IfcWallStandardCase` or non-lumber elements in this change.

## Decisions

### 1. Standard IFC Material Semantics vs. Property Sets
- **Decision:** Use standard `IfcMaterial` and `IfcRelAssociatesMaterial` entities instead of custom property sets.
- **Rationale:** Standard BIM viewers and structural analysis tools (like MiTek Pamir) rely on standard IFC material relations to recognize object materials rather than parsing custom property sets.
- **Alternatives Considered:** 
  - *Custom Property Set (`IfcPropertySet`):* Rejected because it is less standard for material properties and typically ignored by automated material calculators in external CAD systems.

### 2. Single Global Material Association vs. Per-Member Associations
- **Decision:** Create a single `IfcMaterial` entity at the project level, and map all generated `IfcMember` elements to it in a single relationship (`IfcRelAssociatesMaterial`) or as a shared reference.
- **Rationale:** Creating a single relationship mapping all members to the single material definition reduces step-file size and redundancy in the IFC output.
- **Alternatives Considered:**
  - *Individual associations:* Create a unique `IfcRelAssociatesMaterial` for every single member. Rejected because it unnecessarily inflates the file size.

### 3. Commenting Future Extensibility
- **Decision:** Add code comments in [ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py) near the material creation point, detailing how `DesignParameters` could be updated with a new field (e.g., `lumberMaterial: str`) to drive the material dynamically.
- **Rationale:** Keeps the codebase maintainable and guides future developers without adding complexity to the current interface.

## Risks / Trade-offs

- **[Risk]** IFC validation failures in strict checkers if the relationship entities are incorrectly formed.
  - **Mitigation** Use `ifcopenshell.guid.new()` for `IfcRelAssociatesMaterial`'s `GlobalId`, assign the appropriate `OwnerHistory`, and verify output in existing tests.
