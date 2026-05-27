## ADDED Requirements

### Requirement: POST /api/dxf/generate returns DXF from DesignParameters
The Starlette application SHALL register a route `POST /api/dxf/generate` that accepts a JSON request body matching the `DesignParameters` schema. The endpoint SHALL construct a `DesignParameters` Pydantic model from the request body, call `dxf_builder.build_dxf(params)`, and return the raw DXF bytes as an HTTP response with `Content-Type: application/dxf` and `Content-Disposition: attachment; filename="design.dxf"`.

#### Scenario: Valid parameters return DXF file
- **WHEN** a POST request is sent to `/api/dxf/generate` with JSON body `{"floorPlanDimensions": "10x15m", "roofType": "Gable", "roofPitch": 30}`
- **THEN** the response SHALL have status 200, `Content-Type: application/dxf`, `Content-Disposition: attachment; filename="design.dxf"`, and the body SHALL be valid DXF bytes (re-readable by `ezdxf.read(BytesIO(body))`)

#### Scenario: Missing required parameters return 400
- **WHEN** a POST request is sent to `/api/dxf/generate` with JSON body `{"floorPlanDimensions": "10x15m"}` (missing `roofType`, causing `build_dxf` to raise `ValueError`)
- **THEN** the response SHALL have status 400 and a JSON body with an `error` key containing a descriptive message

#### Scenario: Invalid roofType returns 400
- **WHEN** a POST request is sent to `/api/dxf/generate` with JSON body `{"floorPlanDimensions": "10x15m", "roofType": "Gambrel"}`
- **THEN** the response SHALL have status 400 and a JSON body with an `error` key containing the ValueError message from `build_dxf`

#### Scenario: Malformed JSON returns 422
- **WHEN** a POST request is sent to `/api/dxf/generate` with a non-JSON body or invalid JSON
- **THEN** the response SHALL have status 422

#### Scenario: Minimal valid request with flat roof
- **WHEN** a POST request is sent to `/api/dxf/generate` with JSON body `{"floorPlanDimensions": "8x12m", "roofType": "Flat"}`
- **THEN** the response SHALL have status 200 with valid DXF content containing all five layers
