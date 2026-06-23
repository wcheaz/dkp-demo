## Context

Currently, the IFC file generation implementation in `agent/src/ifc_builder.py` outputs walls and structural members, but none of the structural members have classification attributes or property sets associated with them. To automate structural pricing and material takeoff inside estimating software like MiTek Pamir, we need to embed functional member classifications (such as rafter, web, chord) and wood properties (such as grade and treatment status) directly in the generated IFC model.

This design specifies how to add functional classifications via the `ObjectType` attribute and wood properties via standard `IfcPropertySet` entities mapped to all `IfcMember` elements using the standard IFC2x3 schema.

## Goals / Non-Goals

**Goals:**
- Categorize each `IfcMember` by its functional role (e.g. `"TOP_CHORD"`, `"BOTTOM_CHORD"`, `"WEB"`, `"PLATE"`) using the `ObjectType` attribute.
- Define a shared property set containing wood grade (`Grade` set to `"C24"`) and treatment status (`IsTreated` set to `True`) associated with all timber `IfcMember` entities.
- Add code comments describing how to extend these properties dynamically from `DesignParameters` in the future.

**Non-Goals:**
- Associating custom properties or classification attributes with walls (`IfcWallStandardCase`).
- Generating physical fastener elements or nailplates.
- Dynamically deriving material or pricing parameters from API inputs in this phase.

## Decisions

### 1. Functional Categorization via `ObjectType` vs. Custom Properties
- **Decision:** Use the standard `ObjectType` attribute of `IfcMember` to store the functional category (e.g., `"TOP_CHORD"`, `"BOTTOM_CHORD"`, `"WEB"`, `"PLATE"`).
- **Rationale:** BIM viewers and estimating tools natively query standard attributes like `ObjectType` to classify and filter structural members, which makes it highly compatible without requiring custom mapping rules.
- **Alternatives Considered:**
  - *Custom Property Set:* Rejected because standard CAD tools cannot query it as easily as the standard `ObjectType` attribute.

### 2. Associating Metadata via standard Property Sets
- **Decision:** Create a shared `IfcPropertySet` containing properties `Grade` (set to `"C24"`) and `IsTreated` (set to `True`), and map all `IfcMember` elements to it using `IfcRelDefinesByProperties`.
- **Rationale:** Standard property sets are the industry-standard way to attach non-geometric data (such as material grade, supply code, or treatment status) to IFC elements.
- **Alternatives Considered:**
  - *Overloading Name/Description:* Rejected because it violates IFC structure conventions and prevents database-level queries.

### 3. Share Property Set vs. Per-Member Property Sets
- **Decision:** Create a single project-level `IfcPropertySet` and associate all `IfcMember` elements to it in a single relationship (`IfcRelDefinesByProperties`).
- **Rationale:** Reduces file redundancy and minimizes IFC file size.
- **Alternatives Considered:**
  - *Individual Property Sets:* Rejected because creating unique property sets for every single member increases file size and calculation overhead.

## Risks / Trade-offs

- **[Risk]** IFC validation failures if the relationship entities are incorrectly formed.
  - **Mitigation:** Use `ifcopenshell.guid.new()` for `IfcRelDefinesByProperties`'s `GlobalId`, assign the appropriate `OwnerHistory`, and verify output in existing tests.
- **[Risk]** Property set duplication or bloated schema.
  - **Mitigation:** Share the property set definition across all members in a single relation rather than defining unique property sets for each member.
