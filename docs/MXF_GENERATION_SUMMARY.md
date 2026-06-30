# MXF Layout Generation Summary

This document summarizes the work delivered by the `mxf-layout-generation`
change. It adds MiTek Pamir support to the design pipeline by exporting the
building's outer wall layout as a standard-compliant MiTek Exchange XML
(`.mxf` Layout format) file, complementing the existing DXF and IFC outputs so
wall boundaries can be imported directly into Pamir for native auto-framing and
plate-stress calculations.

## 1. Layout MXF builder

Implemented in `agent/src/mxf_builder.py` (`build_mxf`).

- Consumes a `DesignParameters` payload and emits a Pamir-compatible Layout MXF
  byte stream via Python's built-in `xml.etree.ElementTree`, pretty-printed with
  `xml.dom.minidom.toprettyxml` for readability.
- The root `<Mxf>` element carries the exact markers Pamir expects:
  `version="MXF Version 5.11"`, `originator="dkp-demo agent"`, and the
  `xmlns:xsd` / `xmlns:xsi` namespace declarations.
- The document is anchored at local origin `(0, 0, 0)` with all coordinates
  written in metres (converted from the `floorPlanDimensions` string by the
  shared `parse_dimensions` helper).
- Constants `WALL_THICKNESS = 0.2` and `WALL_HEIGHT = 3.0` mirror the Pamir
  reference export (`hidden/Sample_Project/Test Project 2.mxf`) so layouts import
  cleanly without rescaling.

## 2. Wall geometry and inward thickness vectors

Implemented in `wall_specs` (`agent/src/mxf_builder.py`).

- The building is closed by exactly four walls (`W0`–`W3`) placed clockwise
  around the floor-plan rectangle.
- Each wall emits a `<Position>` carrying `origin`, `xAxis` (running axis),
  `yAxis` (vertical axis), and `zAxis` (thickness axis). The thickness (Z) axis
  points **inwards** on every wall so the perimeter matches the standard Pamir
  import convention and walls do not shift outward beyond the building boundary:
  - **W0** (Bottom, Y=0): xAxis east `(1, 0, 0)`, zAxis north `(0, 1, 0)`.
  - **W1** (Right, X=W): xAxis north `(0, 1, 0)`, zAxis west `(-1, 0, 0)`.
  - **W2** (Top, Y=D): xAxis west `(-1, 0, 0)`, zAxis south `(0, -1, 0)`.
  - **W3** (Left, X=0): xAxis south `(0, -1, 0)`, zAxis east `(1, 0, 0)`.

## 3. Wall skin corner offsets and wall plates

Implemented in `_face_polygon` / `build_mxf` (`agent/src/mxf_builder.py`).

- Each wall definition carries a `<SkinList>` with a **FrontFace** polygon
  spanning `0` to `length`, and a **BackFace** (inner skin) polygon spanning
  `thickness` (0.2) to `length - thickness`. Shortening the inner skin replicates
  the corner overlap logic in Pamir exports and prevents inner skins from
  intersecting at the corners.
- A `<WallPlateList>` defines a wall plate with `offset="0.05"`,
  `height="0.05"`, and `width="0.1"`.
- `build_mxf` raises a `ValueError` when `floorPlanDimensions` is missing or the
  width/depth cannot be parsed, rejecting invalid dimensions before any XML is
  emitted.

## 4. REST API endpoint

Implemented in `agent/src/main.py` (`POST /api/mxf/generate`).

- Accepts a `DesignParameters` JSON body, builds the layout MXF bytes, and
  returns them with `Content-Type: application/mxf` and a
  `Content-Disposition: attachment; filename="design.mxf"` header.
- Mirrors the stateless architecture of the DXF and IFC download routes so the
  endpoint is decoupled from the agent loop.

## 5. Frontend download and tool registration

- `src/lib/types.ts` and `agent/src/agent.py` gained an optional `mxfContent`
  field on `DesignEntry` to carry the base64-encoded MXF content.
- A client-side `generate_mxf` tool in `src/app/page.tsx` fetches the bytes from
  `/api/mxf/generate`, base64-encodes them, and stores the result in `mxfContent`
  in React state.
- `src/components/design-component.tsx` renders an `MxfDownloadButton` (decoding
  the base64 content into a Blob URL with `useMemo` cleanup) next to the IFC
  download button whenever `entry.mxfContent` is present.
- Translation keys for the download label were added to both
  `src/i18n/messages/en.json` and `src/i18n/messages/sk.json`.
- The `run-generate-design` agent skill (`.agents/skills/run-generate-design/`)
  was extended with the MXF generation step, including a new
  `references/mxf-builder-api.md` reference document.

## Verification

- Backend builder: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py`.
- API endpoint: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_endpoint.py`.
- Lint/style: `uv run --project agent ruff check agent/src`.
- Frontend gates (`npx tsc --noEmit`, `npm run lint`, `npm run i18n:check`) pass
  at or within the recorded baselines under
  `.ralph/baselines/mxf-layout-generation-*`.

## Future roadmap: MXF surface generation

Roof (`<RoofList>`) and floor (`<FloorList>`) surfaces are intentionally omitted
in this phase per `design.md` non-goals — MXF surface generation is tracked as a
follow-up in `hidden/TODO.md`. Pamir's import wizard can auto-generate these
surfaces in one click (Automatic Surface) once the wall boundaries are defined,
so the omission does not block a productive import; automating surface
pre-calculation remains open for a future change.
