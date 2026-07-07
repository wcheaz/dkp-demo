## Context

In our current implementation, `mxf_builder.py` generates layout-only MXF files containing walls and roof planes. When these layout files are imported into MiTek Pamir, the auto-framing engine treats the two sloped roof surfaces as independent structures, generating two separate half-span trusses meeting at the ridge instead of a single wall-to-wall gable truss. Because they have no central load-bearing support, these split trusses are structurally invalid. 

Additionally, the automated layout lacks gable-end panels at the outer boundaries, places bracing horizontally at the ceiling level (rather than along the roof slope), and does not account for the 3.3m road transport height limit for tall trusses (which requires dividing them into multi-part frames).

## Goals / Non-Goals

**Goals:**
- Extend the MXF builder to pre-generate full structural framing (`<FrameList>`, `<BuildingFrameList>`, `<PlateTypeList>`, and `<TimberSectionList>`) directly in the exported MXF file.
- Implement a unified truss solver in `geometry_solver.py` that generates a single, structurally valid, full-span truss spanning from wall-to-wall.
- Detect when a truss height exceeds the 3.3m transport limit, and dynamically split it into two horizontal sections (`Part 1` and `Part 2`) with horizontal splice chords.
- Automatically place specialized `GableEnd` panels at the two outermost roof boundaries.
- Generate diagonal wind bracing and purlins along the sloped top chords of the roof.
- Ensure the IFC builder uses the same unified solver to maintain geometric congruency across formats.

**Non-Goals:**
- Creating a complete real-time engineering calculation engine (Pamir will still perform the final plate-stress and structural verification).
- Supporting automated transport splitting for non-gable roof types in this phase.

## Decisions

### 1. Unified Structural Truss Solver in `geometry_solver.py`
- **Decision**: Move all chord, web, joint, and plate coordinate calculation logic out of `ifc_builder.py` and consolidate it into a reusable class/module in `geometry_solver.py`.
- **Rationale**: Both `ifc_builder.py` and `mxf_builder.py` must output identical structural layouts. Sharing a single geometry solver prevents divergence between the IFC and MXF models.

### 2. Transport Limit Detection and Multi-Part Splicing
- **Decision**: Calculate the total height of the truss:
  $$H_{\text{truss}} = \frac{W_{\text{building}}}{2} \cdot \tan(\theta) + H_{\text{heel}}$$
  If $H_{\text{truss}} > 3.3\text{ m}$, the solver will generate two distinct `Part` elements in the XML:
  * **Part 1 (Base)**: Extends from $Z = 0$ to $Z = 2.8\text{ m}$ with a flat, horizontal top chord.
  * **Part 2 (Cap)**: A triangular cap truss starting at $Z = 2.8\text{ m}$ up to $H_{\text{truss}}$, resting on the flat top chord of Part 1.
  * They will be linked via structural plate joints at the horizontal interface.
- **Rationale**: Matches the standard transport restrictions and the structural pattern seen in the human-designed reference `7JULY_Z.mxf`.

### 3. Outer Gable-End Panels
- **Decision**: Set the first and last frames in the layout sequence to have the family `GableEnd` and type `PanelFrame`. These frames will omit diagonal webs and instead place vertical studs at a standard $600\text{ mm}$ spacing.
- **Rationale**: Gable-end frames are structurally distinct from common trusses as they carry the wall cladding and transfer wind loads directly to the foundation.

### 4. Sloped Bracing System
- **Decision**: Define `<EngineeredBrace>` elements in the MXF referencing the top chords of the trusses. Generate purlins spaced at $1.0\text{ m}$ intervals along the roof slope, plus diagonal wind braces running at $45^{\circ}$ across the top chords.
- **Rationale**: Moving the bracing from ceiling level to the roof slope aligns with standard engineering practices and stops ceiling-level collision warnings.

## Risks / Trade-offs

- **[Risk] Increased XML File Size**
  - *Mitigation*: Adding full member, plate, and brace definitions to the MXF will increase layout file size from ~80KB to ~160KB. This is acceptable as it matches the size of human-designed files and remains within Pamir's import limits.
- **[Risk] Congruency with DXF Builder**
  - *Mitigation*: Ensure `dxf_builder.py` is also updated to reference the new unified solver coordinates so the 2D CAD layouts match the 3D models exactly.
