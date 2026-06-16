## ADDED Requirements

### Requirement: POST /api/ifc/generate returns IFC from DesignParameters
The Starlette application SHALL register a route `POST /api/ifc/generate` that accepts a JSON request body representing `DesignParameters`. The endpoint SHALL construct a `DesignParameters` Pydantic model from the request body, call `ifc_builder.build_ifc(params)`, and return the generated IFC bytes as an HTTP response with `Content-Type: application/ifc` (or `application/octet-stream`) and a header `Content-Disposition: attachment; filename="design.ifc"`.

#### Scenario: Valid parameters return IFC file
- **WHEN** a POST request is sent to `/api/ifc/generate` with a valid JSON body representing full parameters
- **THEN** the response status SHALL be 200
- **AND** the response `Content-Disposition` header SHALL be `attachment; filename="design.ifc"`
- **AND** the body SHALL contain valid IFC2x3 formatted bytes.

#### Scenario: Incomplete parameters return 400
- **WHEN** a POST request is sent to `/api/ifc/generate` with missing mandatory parameters
- **THEN** the response status SHALL be 400
- **AND** the body SHALL contain a JSON response with an `error` details field.

#### Scenario: Invalid JSON payload returns 422
- **WHEN** a POST request is sent to `/api/ifc/generate` with a malformed or non-JSON body
- **THEN** the response status SHALL be 422.
