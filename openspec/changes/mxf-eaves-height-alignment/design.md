## Context

In our current geometry engine implementation, roof surfaces for Layout MXFs are calculated using a baseline where the roof plane intersects the wall top plate ($3.05\text{ m}$) exactly at the wall face. This sets the eaves height to $3.05 - overhang \cdot \tan(\theta)$, which falls below $3.05\text{ m}$. In contrast, MiTek Pamir imports layout planes by anchoring them at the eaves height ($Z_{\text{eaves}}$), which is kept constant at $3.12\text{ m}$ (representing the top of the wall plate plus a standard $70\text{ mm}$ rafter thickness offset). Because our generated roof surfaces are too low, the physical trusses generated during auto-framing protrude above the roof plane at the eaves, causing "Frame too short" warnings in Pamir.

## Goals / Non-Goals

**Goals:**
- Adjust the MXF roof surface Z-coordinate calculations in `geometry_solver.py` to anchor the eaves height at $3.12\text{ m}$ ($3.05\text{ m} + 0.07\text{ m}$ eaves offset).
- Ensure all sloped roof types (Gable, Hip, Mono-pitch) calculate their ridge height starting from the anchored $Z_{\text{eaves}} = 3.12\text{ m}$ and sloping upward.
- Ensure flat roofs generate a flat plane at a constant $Z = 3.12\text{ m}$ to match the rafter/joist depth.
- Fix all unit test assertions in `test_mxf_builder.py` to match the adjusted Z-coordinates.

**Non-Goals:**
- Supporting dynamically configurable heel heights or rafter depths (a constant eaves offset of $0.07\text{ m}$ matches the Pamir design templates).
- Modifying DXF or IFC builders (which draw centerlines or 3D elements that are already geometrically congruent).

## Decisions

### 1. Anchor Eaves Height
- **Decision**: Define a new module-level constant in `geometry_solver.py`:
  `MXF_ROOF_EAVES_Z = MXF_ROOF_Z_BASE + 0.07` (evaluates to $3.12\text{ m}$).
  Use `MXF_ROOF_EAVES_Z` as the base height for all roof surface polygons.
- **Rationale**: This mirrors the exact roof plane definitions exported by Pamir (such as in `Test Project 2.mxf`), resolving the frame overhang clash at the eaves.

### 2. Update Slope Formulations
- **Flat**: `Z = MXF_ROOF_EAVES_Z` ($3.12\text{ m}$).
- **Mono-pitch**: `z_eaves = MXF_ROOF_EAVES_Z`, `z_ridge = z_eaves + (width_m + overhang_m) * rise`.
- **Gable/Hip**: `z_eaves = MXF_ROOF_EAVES_Z`, `z_ridge = z_eaves + (run_ridge + overhang_m) * rise`.
- **Rationale**: Ensures the slope matches the pitch $\theta$ exactly while referencing the correct eaves baseline.

## Risks / Trade-offs

- **[Risk] Test Regression**
  - *Mitigation*: Run the full unit test suite `pytest` before and after changes. Carefully update all expected coordinate values in `test_mxf_builder.py` and `test_mxf_endpoint.py`.
