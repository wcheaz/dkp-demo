# IFC Builder API Reference

Function signature, parameter mapping, and output shape for the backend IFC export.

## API Endpoint

- **Path:** `/api/ifc/generate`
- **Method:** `POST`
- **Body:** JSON object containing `DesignParameters`

Returns a raw IFC2x3 binary file stream.

## DesignParameters Field Mapping

| Field | Required | Format | Example |
|-------|----------|--------|---------|
| `floorPlanDimensions` | yes | `"<W>x<D>m"` | `"10x15m"` |
| `roofType` | yes | one of: `gable`, `hip`, `mono-pitch`, `flat` | `"gable"` |
| `roofPitch` | no | degrees (float) | `30` |
| `overhang` | no | `"<N>m"` | `"0.5m"` |
| `buildingType` | no | free text | `"Residential"` |
| `location` | no | free text | `"Bratislava"` |

`roofType` and `floorPlanDimensions` are the minimum required fields.

## Output Format

- **Schema:** IFC2x3 standard tree
- **Extrusion Representation:** Rectangular swept solids (`IfcExtrudedAreaSolid` and `IfcRectangleProfileDef`) for editable members.
- **Content Type:** `application/octet-stream` or `model/ifc`

## Auto-Trigger Rule

IFC generation fires automatically when design status is `"complete"` (all 4 desirable fields present). The agent calls `generate_ifc` with the current design ID; no explicit user request is needed. This mirrors the auto-pricing and DXF generation behavior.
