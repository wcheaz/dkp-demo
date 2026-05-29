## Context

`@mlightcad/cad-simple-viewer` uses a strict singleton `AcApDocManager`. Only one `CadViewer` can render at a time. The current implementation always assigns the live viewer to the **last** design with DXF content (`activeViewerIndex` computed via `reduce`). Older designs with DXF show a static fallback image, but screenshot capture (PNG via WebGL) has proven unreliable across three attempts — see `hidden/SUMMARY.md`.

The DXF content (`dxfContent: string`, base64-encoded) is already stored on every `DesignEntry`, so any past design can be reloaded into the viewer at any time.

## Goals / Non-Goals

**Goals:**

- Allow the user to click any design card that has DXF content to make it the active live viewer
- When switching, unmount the current `CadViewer` (destroying the singleton) and mount a new one for the clicked design
- Show a clear clickable overlay on inactive designs with DXF content indicating the user can click to view
- Preserve current behavior: the newest design with DXF content is active by default
- Clean up the broken screenshot infrastructure (`captureViewToDataUrl`, `onCapturePreview`, `dxfPreview`)

**Non-Goals:**

- Simultaneous live viewing of multiple designs (impossible with singleton)
- PNG/HTML screenshot capture of any kind
- Persisting viewer state (zoom level, pan position) across switches

## Decisions

### 1. Active viewer index as user-controllable state

**Decision:** Replace the computed `activeViewerIndex` with a `useState<number>` initialized to the last DXF-bearing index. A click handler on inactive designs updates this state.

**Rationale:** The computed `reduce` approach always points to the latest design. Using state preserves that default while allowing user override via click.

**Alternative considered:** A ref-based approach without re-render — rejected because the viewer swap needs to trigger React unmount/remount, which requires a state-driven render.

### 2. Clickable overlay instead of placeholder image

**Decision:** Render a styled overlay div on top of the placeholder area for inactive DXF designs, with text like "Click to view" and a pointer cursor. The entire card's viewer area is the click target.

**Rationale:** Makes it immediately obvious that the design is viewable. Simpler than adding a separate button.

**Alternative considered:** A small "View" button below the placeholder — rejected because it's less discoverable and takes extra space.

### 3. React key-based remounting (existing pattern)

**Decision:** Continue using `key={entry.id}` on `CadViewer` to force React remounting when the active design changes. This is already the pattern in `design-component.tsx` line 147.

**Rationale:** The key change causes React to unmount the old `CadViewer` (triggering its cleanup which calls `AcApDocManager.instance.destroy()`) and mount a fresh one for the new design. This is the proven singleton-safe pattern from Phase 1.

### 4. Remove screenshot infrastructure

**Decision:** Remove `captureViewToDataUrl` from `cad-viewer.tsx`, the `onCapturePreview` prop, the `emitPreview` function, the `handleCapturePreview` callback in `design-component.tsx`, and the `dxfPreview` field from `DesignEntry`.

**Rationale:** All three screenshot attempts failed. The click-to-reactivate approach eliminates the need for any preview capture. Removing dead code simplifies the component.

## Risks / Trade-offs

- **[Viewer load delay on switch]** Each click-to-reactivate triggers a full `CadViewer` mount + DXF parse + render cycle (~1-2 seconds). → Acceptable trade-off; the current design already has this delay on initial load. A loading spinner within the viewer area during the transition would mitigate perceived delay.
- **[State desync on new design]** When a new design is generated, `activeViewerIndex` should auto-switch to it. The default index initialization handles this on mount, but the existing state must also be updated when a new design appears. → The `useEffect` watching `dxfContent` in `cad-viewer.tsx` already reloads DXF; the parent should reset `activeViewerIndex` when the designs array grows.
- **[No zoom/pan persistence]** Switching away from a design loses its zoom/pan state. → Acceptable for now; the viewer auto-zooms to fit on load.
