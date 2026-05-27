## Why

Users need CAD-ready DXF files from their collected `DesignParameters` so they can open roof/truss designs in AutoCAD, LibreCAD, DraftSight, or any DXF-compatible tool. Phase 1 establishes the foundational `dxf_builder` module that produces a valid DXF from the three core parameters: `floorPlanDimensions`, `roofType`, and `roofPitch`. Without this foundation, later phases (full geometry engine, agent integration, frontend download) have nothing to build on.

## What Changes

- Add `ezdxf` (pure-Python DXF library) to `requirements.txt`
- Create `agent/src/dxf_builder.py` — a standalone module with `build_dxf(params: DesignParameters) -> bytes` that produces a valid DXF file
- The initial implementation draws a 2D floor-plan outline and a roof-plan outline (per roof type) using the three core parameters
- Add unit tests in `test/test_dxf_builder.py` that verify output validity via `ezdxf.read()`

## Capabilities

### New Capabilities

- `dxf-builder`: Standalone DXF generation from `DesignParameters`. Parses floor dimensions, converts to millimeters, draws floor-plan outline (LWPOLYLINE) and roof-plan outline (LINE/LWPOLYLINE) on separate layers, returns DXF content as bytes.

### Modified Capabilities

_(None — this change does not modify existing spec-level behavior.)_

## Impact

- **New file**: `agent/src/dxf_builder.py`
- **New file**: `test/test_dxf_builder.py`
- **Dependency**: `ezdxf` added to `requirements.txt` (pure-Python, no system deps)
- **No agent changes**: The module is decoupled from the agent and has no imports from `agent.py`
- **No frontend changes**: Phase 1 is backend-only
