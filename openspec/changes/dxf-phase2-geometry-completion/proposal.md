## Why

The DXF builder (`agent/src/dxf_builder.py`) currently produces a valid but minimal drawing: a floor-plan rectangle and a roof-type outline on two layers. To be useful as a CAD-ready deliverable, the DXF must also include truss cross-sections, dimensioned annotations, and a title block. This change completes Phase 2 of the geometry engine by adding those three missing elements, all within the existing `dxf_builder.py` module.

## What Changes

- **Truss layout geometry**: Compute total truss count from the existing formula `round(floor_area * 0.147)`, then draw evenly-spaced 2D cross-section lines (rafters + tie-beam) on a new `Trusses` layer.
- **Dimensions and annotations**: Add ezdxf linear dimensions for building width/length, ridge height, and overhang, plus text labels, on a new `Dimensions` layer.
- **Title block and border**: Draw an A-series sheet border with project metadata (building type, location, date) extracted from `DesignParameters`, on a `Title_Block` layer.
- **Verification of existing Phase 2 work**: Confirm the floor-plan outline and roof-plan geometry per type are complete and correct before building on top of them.

## Capabilities

### New Capabilities

- `dxf-truss-layout`: Truss cross-section geometry — 2D rafter + tie-beam lines spaced along the building length on a `Trusses` layer.
- `dxf-dimensions-annotations`: Linear dimension entities and text labels for key measurements on a `Dimensions` layer.
- `dxf-title-block`: A-series sheet border with project metadata on a `Title_Block` layer.

### Modified Capabilities

- `dxf-builder`: `build_dxf` gains three new drawing phases (trusses, dimensions, title block) and three new layers. The function signature and return type remain unchanged.

## Non-goals

- No agent tool or frontend changes — this change is limited to the geometry engine module.
- No 3D geometry or perspective views.
- No DXF blocks, external references, or paper-space layouts.
- No hatch/fill patterns for cross-sections.
- No ARC or CIRCLE entities — all truss geometry uses LINE entities only.
- Roof-pitch-based rafter angle calculation is out of scope for this change; cross-sections use a fixed triangle profile based on `roofPitch` for gable/hip, a sloped line for mono-pitch, and a flat line for flat.

## Impact

- **Files modified**: `agent/src/dxf_builder.py` (primary), `test/` (new tests).
- **New layers added to DXF output**: `Trusses`, `Dimensions`, `Title_Block`.
- **Dependencies**: No new Python packages — uses existing `ezdxf` dimension, text, and polyline APIs.
- **API**: `build_dxf(params)` signature unchanged; callers are unaffected.
