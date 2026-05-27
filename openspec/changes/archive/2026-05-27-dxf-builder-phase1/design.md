## Context

The agent service (`agent/src/agent.py`) collects `DesignParameters` from users — including `floorPlanDimensions` (e.g. "10x15m"), `roofType` (Gable, Hip, Mono-pitch, Flat), and `roofPitch` (degrees). Currently these parameters drive pricing and SVG generation but produce no CAD output. The `dxf_builder` module will be a standalone, testable function that converts those parameters into a valid DXF file.

The module is intentionally decoupled from the agent so it can be unit-tested without any agent imports, model dependencies, or network calls.

## Goals / Non-Goals

**Goals:**

- Produce a valid DXF file from `floorPlanDimensions`, `roofType`, and `roofPitch`
- Draw a 2D floor-plan outline (building perimeter) on a `Floor_Plan` layer
- Draw a roof-plan outline per roof type on a `Roof_Outline` layer
- Use DXF conventions (millimeters, standard layers)
- Return DXF content as `bytes` for downstream consumption (file save, HTTP response, etc.)

**Non-Goals:**

- Full geometry engine (trusses, cross-sections, hatching) — deferred to Phase 2
- Agent tool integration (`generate_dxf` tool) — deferred to Phase 3
- Frontend download button — deferred to Phase 4
- Dimensions, annotations, title blocks — deferred to Phase 2
- ARC/CIRCLE entities for rounded eaves — deferred to Phase 2

## Decisions

### 1. Library: `ezdxf`

**Choice**: Use `ezdxf` for DXF generation.

**Rationale**: Pure-Python, actively maintained, well-documented, no system-level dependencies. The TODO already identified it as the target library. Alternative (`dxfwrite`) is unmaintained. Low-level hand-coding of DXF text format is error-prone and unnecessary.

### 2. DXF version: AC1015 (AutoCAD 2000)

**Choice**: Use `ezdxf.new("R2000")` which produces AC1015.

**Rationale**: Maximum compatibility with AutoCAD, LibreCAD, DraftSight, and web viewers. Supports LWPOLYLINE, layers, and all entity types needed for this and future phases. No reason to target a newer version for simple 2D geometry.

### 3. Unit system: millimeters

**Choice**: All coordinates in millimeters. Parse `floorPlanDimensions` meters and multiply by 1000.

**Rationale**: DXF convention for architectural/engineering drawings is millimeters. Conversion is trivial: `"10x15m"` → 10000mm x 15000mm.

### 4. Coordinate system: origin at bottom-left

**Choice**: Floor-plan rectangle starts at (0, 0) with width along X-axis and depth along Y-axis.

**Rationale**: Standard CAD convention. Simple to reason about. Roof geometry derives from the floor-plan rectangle corners.

### 5. Layer naming

**Choice**: Two layers — `Floor_Plan` and `Roof_Outline`.

**Rationale**: Clean separation of concerns. Users can toggle visibility per layer. Names are human-readable and match the TODO's layer naming convention.

### 6. Floor-plan parsing

**Choice**: Reuse the existing regex pattern from `generate_quote`: `r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?"`. If parsing fails, raise `ValueError` with a clear message.

**Rationale**: The agent already uses this format. No new parsing rules needed. `ValueError` is the right exception for invalid input — callers (tests, future agent tool) can catch it explicitly.

### 7. Roof geometry per type

**Algorithms** (all coordinates in mm, derived from floor-plan rectangle):

- **Gable**: Ridge line runs parallel to the longer axis, centered. Ridge endpoints at midpoint of each long side. Eave overhang extends the rectangle by `overhang` amount (default 500mm if not specified).
- **Hip**: Ridge line is shorter than the building length, centered. Hip lines connect ridge endpoints to the outer corners of the short sides. Ridge length = building length - building width.
- **Mono-pitch**: Single sloping plane. High side along one long edge, low side along the opposite. Draw as a single LWPOLYLINE rectangle offset by roof pitch.
- **Flat**: Roof outline matches the floor-plan rectangle exactly (with overhang). Draw as a simple LWPOLYLINE rectangle.

**Pitch handling**: For Phase 1, `roofPitch` does not affect the 2D plan-view geometry (plan view is an orthogonal projection). Pitch is stored as metadata but does not change the roof outline shape in plan. This keeps Phase 1 simple — pitch affects cross-section geometry which is Phase 2.

### 8. Return type: `bytes`

**Choice**: `build_dxf()` returns `bytes` containing the DXF file content.

**Rationale**: `ezdxf` can write to a `BytesIO` via `doc.write()`. Bytes are the most flexible return type — can be written to a file, served as an HTTP response, or base64-encoded.

### 9. Function signature

```python
def build_dxf(params: DesignParameters) -> bytes:
```

**Rationale**: Accepts the existing `DesignParameters` Pydantic model. The function reads only `floorPlanDimensions`, `roofType`, and `overhang`. If any required field is `None`, raises `ValueError`.

## Risks / Trade-offs

- **Risk**: `ezdxf` version incompatibility with older CAD viewers → Mitigation: Target AC1015 (R2000) which is universally supported.
- **Risk**: `floorPlanDimensions` parsing fails on unexpected formats → Mitigation: Clear `ValueError` message; reuse proven regex from `generate_quote`.
- **Risk**: Roof geometry is simplified (plan-view only, no pitch projection) → Mitigation: By design for Phase 1. Pitch-aware cross-sections are Phase 2.
- **Trade-off**: Returning `bytes` means callers must handle encoding for display, but this is the most flexible interface for serving via HTTP or writing to disk.
