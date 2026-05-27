## Context

`dxf_builder.py` is a standalone module that accepts a `DesignParameters` Pydantic model and returns DXF bytes via `build_dxf()`. It currently produces two layers (`Floor_Plan`, `Roof_Outline`) with plan-view geometry. The caller (`agent.py`) does not inspect the DXF content — it only passes the result through. This means the module has full autonomy over layer structure, entity types, and coordinate systems.

All coordinates are in millimeters (DXF convention). The building origin is (0,0). Width runs along X, depth along Y.

**Existing `DesignParameters` fields used:**
- `floorPlanDimensions` — parsed by `_parse_dimensions()` into `(width_mm, depth_mm)`
- `roofType` — selects the roof drawer function
- `roofPitch` — available but currently unused
- `overhang` — available but currently unused
- `buildingType`, `location` — available for title block metadata

**Truss count formula** (from TODO): `total_trusses = round(floor_area * 0.147)` where `floor_area` is in square meters.

## Goals / Non-Goals

**Goals:**
- Add three new drawing layers (`Trusses`, `Dimensions`, `Title_Block`) to the DXF output
- Each truss drawn as a 2D cross-section (triangle for gable/hip, sloped line for mono-pitch, flat for flat) composed of LINE entities
- Linear dimension entities for building width, depth, ridge height, and overhang
- Text labels for key measurements
- A-series sheet border with project metadata text

**Non-Goals:**
- No 3D or isometric views
- No HATCH, ARC, or CIRCLE entities
- No paper-space layouts or viewports
- No changes to agent tools, frontend, or API surface
- No hatch fills on truss cross-sections

## Decisions

### D1: Truss cross-section as simple LINE entities

Each truss cross-section is a 2D profile drawn with LINE entities. For gable/hip roofs, the cross-section is an isosceles triangle (two rafters + tie-beam). For mono-pitch, a right triangle. For flat, a horizontal line.

- **Why**: LINE entities are the simplest entity type that `ezdxf` supports well and that any CAD tool can render. Avoids complexity of LWPOLYLINE closed shapes for what is fundamentally three line segments.
- **Alternative**: LWPOLYLINE with close=True would produce the same triangle with one entity instead of three. Rejected because LINE entities are easier to debug and individually select in CAD tools.

### D2: Truss spacing algorithm

Trusses are evenly distributed along the building's longer axis (or depth axis if square). The first and last truss are placed at a fixed inset of `width * 0.05` from the building edges, with remaining trusses evenly spaced in between.

- **Why**: Produces a realistic engineering layout without requiring complex load calculations.
- **Alternative**: Uniform spacing from edge to edge. Rejected because real truss layouts have edge clearance.

### D3: Ridge height derived from roofPitch

Ridge height for the cross-section is calculated as `ridge_height_mm = (width_mm / 2) * tan(roofPitch_degrees * pi / 180)`. If `roofPitch` is None or 0, defaults to 30 degrees for gable/hip and 10 degrees for mono-pitch.

- **Why**: Uses available `roofPitch` field. The default ensures geometry is visible even when the agent doesn't collect pitch.
- **Fallback**: Default 30° for gable/hip, 10° for mono-pitch, 0° for flat.

### D4: Dimension entities use ezdxf linear dimension API

Dimensions are placed using `msp.add_linear_dim()` with a fixed offset from the geometry. Width dimension below the floor plan, depth dimension to the left. Ridge height dimension to the right of the first truss cross-section.

- **Why**: ezdxf's dimension API produces proper DXF DIMENSION entities that render with dimension lines, arrows, and text in all CAD viewers.
- **Text height**: 250mm (legible at building scale).

### D5: Title block is an A3 border with metadata text

An A3 sheet (420000 x 297000 mm at 1:1) is oversized relative to the building. Instead, the title block is a fixed-size rectangle in the lower-right corner of the drawing area, sized at 40000 x 15000 mm, containing:
- Building type
- Location
- Date (current UTC date in YYYY-MM-DD)
- Floor plan dimensions
- Roof type

- **Why**: A fixed-size title block is simpler than scaling to paper size and works at any building scale.
- **Alternative**: Full A-series border. Rejected because building dimensions vary widely and a fixed border would either clip or leave massive whitespace.

### D6: Layer naming convention

New layers follow the existing pattern: `Floor_Plan`, `Roof_Outline` → `Trusses`, `Dimensions`, `Title_Block`. Title case with underscores.

- **Why**: Consistency with existing layers. ezdxf and CAD tools handle underscores well.

## Risks / Trade-offs

- **Risk**: `roofPitch` is Optional and may be None → Mitigation: explicit defaults (30° gable/hip, 10° mono-pitch, 0° flat).
- **Risk**: `overhang` is a string field with unknown format → Mitigation: parse with same regex approach as floorPlanDimensions; if unparseable, default to 500mm.
- **Risk**: Dimension entities may overlap geometry at very small building sizes → Mitigation: offset dimensions by a percentage of building size (10%).
- **Trade-off**: Simple triangular cross-sections are not engineering-accurate for hip roofs → Accepted; the DXF is for visualization, not structural certification.
