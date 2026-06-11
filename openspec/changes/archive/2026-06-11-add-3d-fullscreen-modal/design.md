## Context

The main page currently provides a 2D CAD preview via `@mlightcad/cad-simple-viewer` (wrapped in `CadViewer`). To facilitate better spatial analysis of the generated truss designs, we are integrating the custom client-side Three.js-based 3D viewer (`CadViewer3D`) into the fullscreen modal.

Additionally, to ensure the agent's skills and simulated behaviors remain aligned with 3D viewer limits (namely, the `three-dxf-loader` crash on `DIMENSION` objects), we are updating the agent skill definition and its references to document and simulate compatible geometries.

The files to be updated are:
- `src/components/design-component.tsx`: Fullscreen layout and rendering toggle.
- `src/components/cad-viewer-3d.tsx`: Inject translation hook (`useTranslations`) and localize button labels.
- `src/i18n/messages/en.json` & `src/i18n/messages/sk.json`: Translate new UI strings.
- `.agents/skills/run-generate-design/references/dxf-builder-api.md`: Update layer details to document that `Labels` and `Dimensions` layers use standard `TEXT` primitives instead of `DIMENSION` objects for 3D compatibility.

## Goals / Non-Goals

**Goals:**
- Dynamically import the `CadViewer3D` component in `src/components/design-component.tsx` with `ssr: false`.
- Replace the 2D CAD viewer canvas with the interactive 3D WebGL viewer inside the fullscreen modal view block.
- Localize all labels and loading overlays in the 3D viewport control panel for both English and Slovak.
- Ensure proper cleanup of WebGL contexts and OrbitControls instance when exiting the fullscreen view to avoid memory leaks.
- Align the agent's documentation in `dxf-builder-api.md` so that the `Dimensions` and `Labels` layers are documented as using standard `TEXT` or `MTEXT` labels instead of `DIMENSION` entities.

**Non-Goals:**
- Replacing 2D CAD views on the design list feed cards.
- Implementing any backend edits to `dxf_builder.py` or the generation pipelines (which have already been modified to output `TEXT` entities).
- Modifying Three.js or loader package configurations.

## Decisions

### Decision 1: Use Next.js Dynamic Importing with ssr: false
- **Rationale**: The WebGL/Three.js renderer accesses global client-side objects like `window`, `navigator`, and `document` which are not available during Server-Side Rendering (SSR). Disabling SSR ensures compilation and builds do not crash.
- **Alternatives Considered**: 
  - *Conditional mounting inside useEffect*: Rejected because dynamic importing separates code chunks and decreases initial page load size.

### Decision 2: Localize via core JSON messages and `useTranslations` hook
- **Rationale**: Keeping the standard Next.js translation strategy ensures consistent locale support and lets Slovak/English language selection cascade automatically to the 3D controls.
- **Alternatives Considered**: 
  - *Hardcoded maps*: Rejected because it bypasses the system dictionary framework.

### Decision 3: Single-view Mode for Fullscreen (3D-Only)
- **Rationale**: Fullscreen mode is primarily used for deep analysis, making 3D rendering the most valuable experience. Keeping the inline card views 2D ensures fast page loading and low memory usage.
- **Alternatives Considered**: 
  - *2D/3D Tabbed Toggle in Fullscreen*: Rejected as it adds visual clutter to the modal and is unnecessary since the 2D view is already available in the standard list view card.

### Decision 4: Update Agent Skill Documentation for 3D Compatibility
- **Rationale**: Aligning the simulated agent outputs and reference documentation with the actual code behavior of `dxf_builder.py` (which produces standard text labels instead of `DIMENSION` objects) ensures that the autonomous agent uses and understands correct, compatible dxf schemas.
- **Alternatives Considered**: 
  - *Leave agent documentation as-is*: Rejected because it would leave outdated references to `DIMENSION` entities, causing confusion and potential issues in future agent runs.

## Risks / Trade-offs

- **[Risk] WebGL Context Loss / Memory Leak on repeated mounts**  
  - *Mitigation*: The `useEffect` cleanup hook in `src/components/cad-viewer-3d.tsx` calls `renderer.dispose()` and `controls.dispose()` and removes the DOM element to release GPU memory.
- **[Risk] Layout resizing container issues**  
  - *Mitigation*: Set `renderer.setSize(w, h, false)` on window resize and container mounts to fit dynamically sized container divs.
