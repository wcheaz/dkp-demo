# DXF Builder API Reference

Function signature, parameter mapping, and output shape for `build_dxf` in `agent/src/dxf_builder.py`.

## Function Signature

```
build_dxf(params: Any) -> bytes
```

Returns a UTF-8-encoded DXF string (R2004 format) as raw bytes.

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

- **DXF version:** R2004 (`AC1018`)
- **Coordinate system:** millimetres, origin at bottom-left corner of floor plan
- **Encoding:** UTF-8

## Layers and Entity Rules

The DXF contains exactly 7 layers. To ensure full compatibility with the client-side WebGL 3D viewer (which uses `three-dxf-loader`), **`DIMENSION` entities must never be used**, as they cause WebGL parser crashes. All annotations must be drawn as `TEXT` entities.

| Layer Name | Contents | Entity Types Allowed |
|------------|----------|----------------------|
| `Floor_Plan` | 2D isometric projected wireframe of 3D wall box | `LINE` |
| `Wall_Centerlines` | Centerline rectangle of the floor plan at Z=0 | `LWPOLYLINE` |
| `Roof_Outline` | Roof framing and ridge outline | `LINE` |
| `Trusses` | Cross-section truss lines spaced along the depth axis | `LINE` |
| `Dimensions` | Configured but kept empty to avoid 3D viewer issues | None |
| `Labels` | Standard text labels for annotations (Width, Depth, Ridge Height) | `TEXT` |
| `Lumber_Specs` | Lumber grade and member specs metadata block | `MTEXT` |

## 3D Viewer Compatibility Constraint
- **No `DIMENSION` Objects:** Do not use `ezdxf`'s dimension style managers or add dimension objects (`add_linear_dim`).
- **Use Primitive text:** Write all text annotations (width, depth, ridge height, overhang) as standard `TEXT` or `MTEXT` primitives on the `Labels` and `Lumber_Specs` layers.

## Auto-Trigger Rule

DXF generation fires automatically when design status is `"complete"` (all 4 desirable fields present). The agent calls `generate_dxf` with the current design ID; no explicit user request is needed. This mirrors the auto-pricing behaviour in Step 4c.
