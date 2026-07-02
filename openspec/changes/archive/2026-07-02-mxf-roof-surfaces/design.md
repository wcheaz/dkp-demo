## Context

The current Layout MXF generation handles building outer walls (`W0` to `W3`) but omits roof and floor surfaces. Pamir imports the layout successfully, but defaults to a 25-degree Gable roof because there is no `<RoofList>` or `<SurfaceList>` in the MXF. We need to implement a 3D geometry engine in `agent/src/mxf_builder.py` that maps `roofType`, `roofPitch`, and `overhang` to 3D surface coordinates, so Pamir loads the correct design pitch and shape automatically.

## Goals / Non-Goals

**Goals:**
- Parse `roofType`, `roofPitch`, and `overhang` parameters during MXF generation.
- Implement geometry solver routines for `Gable`, `Hip`, `Mono-pitch`, and `Flat` roofs.
- Calculate and output `<RoofList>`, `<FloorList>`, and `<SurfaceList>` nodes in the generated XML.
- Add comprehensive test coverage in `test/test_mxf_builder.py` verifying coordinates for each roof style.

**Non-Goals:**
- Fabricating structural framing elements (such as rafters, webbing, or plate connectors).
- Supporting L-shaped or multi-level roofs (limited to rectangular floor plans).

## Decisions

### 1. XML Node Generation and Schema
- **Decision**: Append `<RoofList>` and `<FloorList>` to the `<Building>` node, and `<SurfaceList>` to the root `<Mxf>` node in `build_mxf`.
- **Rationale**: Keeps the XML aligned with standard MiTek MXF format schemas (matching imported/exported examples like `Test Project 2.mxf`).

### 2. Geometry Calculation Formulas
- **Wall Height Reference**: Wall height is fixed at $3.0\text{ m}$. Wall plate is $0.05\text{ m}$. Thus, base roof Z is at $3.05\text{ m}$.
- **Overhang parsing**: If `overhang` is specified, it is parsed (supporting raw numbers or formats like `"250mm"`, `"0.5m"`).
- **Pitch and Rise math**:
  - $Z_{\text{eaves}} = 3.05 - overhang \cdot \tan(\theta)$
  - $Z_{\text{ridge}} = 3.05 + run_{\text{ridge}} \cdot \tan(\theta)$
  - For `Gable` and `Hip`, $run_{\text{ridge}} = \min(W, D)/2$.
  - For `Mono-pitch`, $run_{\text{ridge}} = W$.
  - For `Flat`, pitch $\theta = 0$, so $Z_{\text{eaves}} = Z_{\text{ridge}} = 3.05$.
- **Polygon Orientation**: Points will be written in a closed loop matching clockwise ordering (e.g. `p1 p2 p3 p1` for triangles, `p1 p2 p3 p4 p1` for quadrilaterals).

### 3. Shared Overhang Helper
- **Decision**: Move or duplicate the `_parse_overhang` helper from `dxf_builder.py` to `geometry_solver.py` or define a local version in `mxf_builder.py`.
- **Rationale**: Centralizing or using a safe local parser prevents tight coupling with the DXF package while ensuring robust regex-based unit string parsing.

## Risks / Trade-offs

- **[Risk] Float Precision in Coordinate Strings**
  - *Mitigation*: Format floats with `:g` or a fixed precision (e.g., `.3f` or `.4f` or `:g`) so that Pamir parses coordinates without rounding errors.
- **[Risk] Division by Zero for Flat Roofs**
  - *Mitigation*: Explicitly handle `Flat` roofs or $0^\circ$ pitch by bypassing tangent calculations and generating a single horizontal surface at $Z = 3.05\text{ m}$.
