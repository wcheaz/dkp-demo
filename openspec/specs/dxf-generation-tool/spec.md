## Purpose

Agent tool for generating DXF CAD files from collected design parameters and storing them in the design entry.

## Requirements

### Requirement: generate_dxf tool generates DXF and stores in DesignEntry
The agent SHALL expose a tool named `generate_dxf` decorated with `@agent.tool` and `@_timed_tool`. The tool SHALL accept `ctx: RunContext[StateDeps]` and `design_id: int`. It SHALL look up the `DesignEntry` with matching `id` in `ctx.deps.state.designs`, call `dxf_builder.build_dxf(entry.parameters)`, encode the returned bytes as base64 via `base64.b64encode()`, store the base64 string in `entry.dxfContent`, and return a confirmation string including the design ID and the raw DXF byte size.

#### Scenario: Successful DXF generation for a design with complete parameters
- **WHEN** `generate_dxf` is called with `design_id=1` and designs list contains an entry with `id=1` whose `parameters` has `floorPlanDimensions="10x15m"` and `roofType="Gable"`
- **THEN** the tool SHALL call `build_dxf(entry.parameters)`, base64-encode the result, store it in the matched entry's `dxfContent` field, and return a string containing `"design 1"` and the DXF byte size

#### Scenario: Design ID not found
- **WHEN** `generate_dxf` is called with `design_id=99` and no design in the designs list has `id=99`
- **THEN** the tool SHALL return the string `"No design found with id 99."` and SHALL NOT modify any state

#### Scenario: Design has no parameters
- **WHEN** `generate_dxf` is called with `design_id=1` and the matched entry has `parameters=None`
- **THEN** the tool SHALL return the string `"Design 1 has no parameters. Collect parameters first."` and SHALL NOT modify any state

#### Scenario: build_dxf raises ValueError for invalid parameters
- **WHEN** `generate_dxf` is called with `design_id=1` and the matched entry has `parameters` with `roofType=None` (causing `build_dxf` to raise `ValueError`)
- **THEN** the tool SHALL catch the `ValueError` and return a string starting with `"Cannot generate DXF:"` followed by the error message, and SHALL NOT modify any state

### Requirement: generate_dxf tool docstring describes usage
The `generate_dxf` tool SHALL have a docstring that describes its purpose: generating a downloadable DXF CAD file for a completed design. The docstring SHALL document the `design_id` parameter as an integer referencing an existing design entry.

#### Scenario: Docstring contains parameter description
- **WHEN** the tool's docstring is read
- **THEN** it SHALL contain the word `design_id` and describe it as the ID of the design entry to generate DXF for

### Requirement: generate_dxf uses base64 encoding without data URI prefix
The `dxfContent` value stored in the DesignEntry SHALL be a plain base64-encoded string produced by `base64.b64encode(dxf_bytes).decode("ascii")`. It SHALL NOT include a data URI prefix such as `data:application/dxf;base64,`.

#### Scenario: dxfContent is plain base64
- **WHEN** `generate_dxf` successfully generates DXF content for a design
- **THEN** the entry's `dxfContent` SHALL be a valid base64 string (matching regex `^[A-Za-z0-9+/]+=*$`) with no data URI prefix
