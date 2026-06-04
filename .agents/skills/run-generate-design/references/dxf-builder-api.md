# DXF Builder API Reference

Function signature, parameter mapping, and output shape for `build_dxf` in `agent/src/dxf_builder.py`.

## Function Signature

```
build_dxf(params: Any) -> bytes
```

Returns a UTF-8-encoded DXF string (R2000 format) as raw bytes.

## DesignParameters Field Mapping

| Field | Required | Format | Example |
|-------|----------|--------|---------|
| `floorPlanDimensions` | yes | `"<W>x<D>m"` | `"10x15m"` |
| `roofType` | yes | one of: `gable`, `hip`, `mono-pitch`, `flat` | `"gable"` |
| `roofPitch` | no | degrees (float) | `30` |
| `overhang` | no | `"<N>m"` | `"0.5m"` |
| `buildingType` | no | free text | `"Residential"` |
| `location` | no | free text | `"Bratislava"` |

`roofType` and `floorPlanDimensions` are the minimum required fields. If either is missing, `build_dxf` raises `ValueError`.

## Output Format

- **DXF version:** R2000 (`AC1015`)
- **Coordinate system:** millimetres, origin at bottom-left corner of floor plan
- **Encoding:** UTF-8

## Layers

The DXF contains exactly 5 layers:

| Layer Name | Contents |
|------------|----------|
| `Floor_Plan` | Closed polyline rectangle (width x depth) |
| `Roof_Outline` | Roof geometry — ridge lines for gable/hip, filled outline for mono-pitch/flat |
| `Trusses` | Cross-section truss lines spaced along the depth axis; count = `round(area_m2 * 0.147)` |
| `Labels` | Standard `TEXT` or `MTEXT` entities for all dimensional annotations (width, depth, ridge height, overhang) and text labels |
| `Title_Block` | Border box with building type, location, date, plan size, and roof type |

> **3D Compatibility Note:** `DIMENSION` entities are **excluded** from the output to prevent crashes in WebGL-based 3D viewers (e.g., `three-dxf-loader`). All dimension annotations use standard `TEXT` or `MTEXT` primitives on the `Labels` layer instead. Do **not** emit `DIMENSION`, `DIMENSION_ORDINATE`, `DIMENSION_LINEAR`, or any other `DIMENSION` sub-type entities.

## Auto-Trigger Rule

DXF generation fires automatically when design status is `"complete"` (all 4 desirable fields present). The agent calls `generate_dxf` with the current design ID; no explicit user request is needed. This mirrors the auto-pricing behaviour in Step 4c.
