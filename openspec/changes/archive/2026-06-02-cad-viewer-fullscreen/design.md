## Context

The system currently renders DXF truss geometries within cards in the `DesignComponent` component. These cards are displayed inside the main content area (next to the Copilot sidebar). The height of the CAD viewer container is restricted to `27vh` and width to `55%` of the card size. Users need an easy way to expand the viewer to inspect details without navigating away from the design session or manually uploading files.

## Goals / Non-Goals

**Goals:**
- Provide a responsive maximized view of the CAD drawing within the main content panel.
- Ensure transitions between minimized and maximized views are fast, reliable, and do not trigger extra server-side DXF generations or client-side file reading.
- Implement an intuitive zoom-in magnifying glass button in the CAD preview card.
- Provide a back button to quickly exit the maximized view.
- Support both English and Slovak localizations.

**Non-Goals:**
- Creating a separate page/route that changes the browser URL.
- Adding DXF upload capabilities inside this maximized view.
- Overlaying or hiding the Copilot sidebar.

## Decisions

### D1: local state-based fullscreen rendering within `DesignComponent`
- **Decision:** Manage the fullscreen CAD view using component-level React states (`fullscreenDxf` and `fullscreenDesignId`) within `DesignComponent`. When `fullscreenDxf` is active, conditionally render the maximized workspace instead of the designs list.
- **Rationale:** 
  - Since DXF content base64 strings can be several megabytes in size, passing them via URL search parameters or standard route transitions (like routing to `/cad-viewer` with state) can hit browser URL length limits or cause unnecessary page re-renders.
  - Keeping the state local to the component avoids routing complexities and ensures instant transition.
- **Alternatives Considered:**
  - *Route transition to `/cad-viewer?dxf=...`*: Rejected due to URL length limits on large DXF payloads.
  - *Fixed viewport overlay (z-50) over the entire screen*: Rejected because the Copilot sidebar needs to remain visible and active during the session.

### D2: Magnifying glass button overlay on `CadViewer`
- **Decision:** Wrap the card-level `CadViewer` in a relative div container and absolute-position a magnifying glass button `absolute top-2 right-2 z-10`.
- **Rationale:** This keeps the layout clean and places the zoom control in an intuitive, standard location (top-right of the viewport).
- **Icon Specification:** A custom inline SVG containing a magnifying glass with a plus sign (`zoom-in` icon).

### D3: Fullscreen container layout and sizing
- **Decision:** The fullscreen container will render as a flex container occupying `w-full h-[80vh]` with a dark theme (`bg-[#1e1e1e]`), matching the styling of the `/cad-viewer` route.
- **Rationale:** `80vh` fits within the page layout without causing vertical scroll bar jumping or overlapping footer elements.

### D4: Dynamic resize and reload
- **Decision:** Mount a fresh instance of `<CadViewer>` with a unique `key={fullscreenDesignId}` inside the fullscreen container.
- **Rationale:** 
  - Changing the container dimensions from `27vh` to `80vh` requires WebGL resizing.
  - Initializing a fresh instance of `CadViewer` ensures that the internal Three.js canvas matches the exact dimensions of the newly rendered `80vh` container and triggers the zoom-to-fit initialization automatically.

## Risks / Trade-offs

- **[WebGL Context Exhaustion]** 
  - *Risk:* Instantiating and destroying multiple `CadViewer` instances can exhaust WebGL contexts in some browsers.
  - *Mitigation:* The `useEffect` cleanup hook in `src/components/cad-viewer.tsx` already properly calls `AcApDocManager.instance.destroy()`, releasing resources. Transitioning between fullscreen and preview correctly invokes the cleanup.
