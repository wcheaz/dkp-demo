## Why

Currently, our truss and roof engineering backend only outputs DXF and IFC files. This limits integration with MiTek Pamir, the leading structural framing and design software. Exporting standard MiTek Exchange XML files (`.mxf` Layout files) will allow users to import wall layouts directly into Pamir, enabling automated truss framing, plate sizing, and structural calculations natively within the Pamir engine.

## What Changes

- **Backend MXF Generator**: Create a new module [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py) that consumes [DesignParameters](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py#L170-L180) and outputs a valid, standard-compliant Layout MXF file. The builder will define walls with inward-projecting thickness vectors to align with standard Pamir perimeter logic.
- **Agent Tool Integration**: Register the `generate_mxf` tool in the Pydantic AI agent within [agent.py](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py) to orchestrate MXF generation during the design loop or upon user request.
- **REST API Endpoint**: Add a `POST /api/mxf/generate` endpoint in [main.py](file:///home/ncheaz/git/dkp-demo/agent/src/main.py) to allow stateless download of layout MXF files.
- **Frontend Download Interface**: Extend [types.ts](file:///home/ncheaz/git/dkp-demo/src/lib/types.ts) to support `mxfContent` and update [design-component.tsx](file:///home/ncheaz/git/dkp-demo/src/components/design-component.tsx) to render a download button when `mxfContent` is available.
- **Future Tasks Documentation**: Add a future roadmap note to [TODO.md](file:///home/ncheaz/git/dkp-demo/hidden/TODO.md) concerning eventual roof and floor surface pre-calculations.

## Capabilities

### New Capabilities
- `mxf-generation`: Provides the capability to generate valid, standard-compliant Layout MXF files containing building wall placements from design parameters for seamless import into MiTek Pamir.

### Modified Capabilities
<!-- None -->

## Impact

- **Backend**:
  - [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py) [NEW]
  - [agent.py](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py) (Add Pydantic models for `mxfContent` and register `generate_mxf` tool)
  - [main.py](file:///home/ncheaz/git/dkp-demo/agent/src/main.py) (Expose `/api/mxf/generate` route)
- **Frontend**:
  - [types.ts](file:///home/ncheaz/git/dkp-demo/src/lib/types.ts) (Add `mxfContent` to `DesignEntry`)
  - [page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/page.tsx) (Hook up `generate_mxf` tool client-side)
  - [design-component.tsx](file:///home/ncheaz/git/dkp-demo/src/components/design-component.tsx) (Add `MxfDownloadButton`)
- **Documentation**:
  - [TODO.md](file:///home/ncheaz/git/dkp-demo/hidden/TODO.md) (Roadmap note on surface calculations)
