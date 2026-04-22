## Context

The application is a Next.js project with React components that display AI-generated output. The existing `src/components/procurement-codes.tsx` component is unused — it renders a list of procurement code entries with TXT/CSV/XLSX download buttons and per-item deletion. It imports `AgentState` from `@/lib/types` and uses the `xlsx` library for export.

The current `AgentState` type in `src/lib/types.ts` is minimal (`your_data: YourDataType[]`) and does not reference `procurement_codes` at runtime, meaning the procurement-codes component is fully disconnected from the actual state shape. The component can be rewritten without breaking any active feature.

The project stores a test image at `tmp/next.svg` that will serve as the deterministic image source during development and testing.

## Goals / Non-Goals

**Goals:**

- Replace the unused procurement-codes component with a design display component that renders a growing list of design entries.
- Multiple designs SHALL be visible simultaneously in a scrollable vertical list.
- Each design entry MUST display an image at a consistent standard size and the user-prompt text that generated it.
- The component must accept standard image formats (jpg, jpeg, png, gif, svg, webp, bmp) via the `<img>` tag's natural support.
- During testing, all images resolve to `tmp/next.svg`.
- The `AgentState` type must be updated to carry a `designs` array with a typed `DesignEntry` shape.
- The component must show an empty-state message when no designs exist.
- Clicking an image SHALL open a modal overlay with the image displayed at a larger size, dismissible by clicking outside the image or pressing Escape.

**Non-Goals:**

- Image upload or file selection by the user.
- Image format conversion, compression, or validation beyond what the browser's `<img>` tag natively supports.
- Download/export of designs (the old procurement-codes export feature is removed, not replaced).
- Pagination, virtual scrolling, or lazy loading for large lists.
- Persistence of designs across page reloads or browser sessions.
- Ordering, filtering, or search within designs.
- Zoom, pan, or rotation controls within the modal.
- Grid or horizontal layout modes.

## Decisions

### D1: File rename strategy — rename in-place, full rewrite

**Decision**: Rename `src/components/procurement-codes.tsx` to `src/components/design-component.tsx` and rewrite the file contents entirely.

**Rationale**: The component is unused (zero imports in the codebase) and the internal logic is entirely procurement-specific. A rewrite is cleaner than incremental edits because no existing behavior needs to be preserved.

**Alternative considered**: Create a new file and delete the old one. Rejected because the old file is the intended starting point per the user request, and a rename preserves git history.

### D2: Data model — `DesignEntry` type with `imageUrl` and `promptText`

**Decision**: Define the following types:

```typescript
export interface DesignEntry {
  imageUrl: string;
  promptText: string;
}

export type AgentState = {
  designs: DesignEntry[];
};
```

**Rationale**: These are the minimum fields needed: an image source URL and the prompt that produced it. No `id` field is needed since React can use array index as key for this static-append-only list. No `createdAt` timestamp since ordering is not a requirement.

**Alternative considered**: Include an `id` field (UUID or auto-increment) for stable keys. Rejected because the list is append-only and never reordered or filtered, so array index is sufficient for the current scope. If pagination or reordering is added later, an `id` field should be introduced in a follow-up change.

### D3: Image source resolution — direct `imageUrl` field, hardcoded to test path

**Decision**: The `imageUrl` field on `DesignEntry` holds the full path/URL to the image. During testing, all entries use `tmp/next.svg`. The component passes `imageUrl` directly to the `<img src>` attribute with no transformation.

**Rationale**: Keeping the URL as a plain string with no resolution logic means the component has no awareness of "test mode" versus "production mode." The test harness or calling code controls the URL. This avoids conditional logic inside the component and keeps it deterministic for the loop.

**Alternative considered**: Add a `TEST_IMAGE_URL` constant that overrides all image sources. Rejected because it adds unnecessary indirection — the calling code already controls what goes into `imageUrl`.

### D4: Component layout — scrollable vertical card list with standard image sizing

**Decision**: Render designs as a vertical list of cards inside a scrollable container. The container uses `overflow-y: auto` with a `max-height` constraint so multiple cards are visible simultaneously and the user can scroll through the history. Each card contains an `<img>` and a `<p>` for prompt text. Images are sized to `width: 80%` of the card width and `height: 40vh` (approximately 2/5ths of viewport height), using `object-fit: contain` to preserve aspect ratio. Use glassmorphism styling (`bg-white/20 backdrop-blur-md rounded-2xl shadow-xl`) as the existing component for visual consistency.

**Rationale**: A scrollable container with a fixed max-height ensures that the page doesn't grow unboundedly as designs accumulate. Multiple cards remain visible at once. The 80%-width / 40vh-height dimensions provide a consistent viewing experience without images overwhelming the card or the page. `object-fit: contain` prevents distortion.

**Alternative considered**: Use a fixed pixel height for images. Rejected because viewport-relative units (vh) adapt better across screen sizes. Alternative considered: use `max-height` instead of `height` to let smaller images stay small. Rejected because consistency is preferred — all images should occupy the same space for visual alignment.

### D5: Image modal — pure React state + CSS overlay, no external library

**Decision**: Implement the image modal using React component state (`useState`) and a CSS overlay. When the user clicks an image, a state variable `modalImageUrl` is set to the clicked image's URL. This renders a fixed-position overlay (`fixed inset-0 z-50 bg-black/80`) containing the image at a larger size (`max-width: 90vw`, `max-height: 90vh`, `object-fit: contain`). The modal is dismissed by:
1. Clicking the backdrop (not the image itself) — use `onClick` on the overlay div, with `e.stopPropagation()` on the image.
2. Pressing the Escape key — use a `useEffect` that attaches a `keydown` listener for `Escape`.

No external modal library is used.

**Rationale**: The modal is simple enough that a full library (e.g., `react-modal`, Headless UI Dialog) would add an unnecessary dependency. Pure state + CSS gives full control with minimal code. The `stopPropagation` pattern on the image prevents accidental dismissal when clicking the enlarged image.

**Alternative considered**: Use a `<dialog>` HTML element. Rejected because `<dialog>` has inconsistent styling behavior across browsers and adds complexity for the overlay backdrop effect. Alternative considered: use `react-modal`. Rejected to avoid a new dependency for a single overlay.

### D6: No download/export buttons

**Decision**: Remove all download buttons (TXT, CSV, XLSX) from the component.

**Rationale**: The procurement-codes export feature is not applicable to design diagrams. No replacement export capability is in scope for this change. If export is needed later, it should be a separate change.

### D7: No per-item deletion

**Decision**: Remove the hover-reveal delete button that exists on each procurement-code entry.

**Rationale**: The design list is append-only — entries are added as the AI agent completes prompts. Removing entries is not part of the current workflow. If deletion is needed later, it should be a separate change.

### D8: Agent tool for appending design entries — temporary `add_design_entry`

**Decision**: Add a Pydantic `DesignEntry` model (mirroring the frontend's `DesignEntry` interface with `imageUrl: str` and `promptText: str`) and a `designs: List[DesignEntry] = []` field to `YourState` in `agent/src/agent.py`. Add a temporary `@agent.tool` function `add_design_entry(ctx, prompt_text)` that appends `DesignEntry(imageUrl="tmp/next.svg", promptText=prompt_text)` to `ctx.deps.state.designs`. Update the agent's `system_prompt` to instruct the agent to call `add_design_entry` with the user's original prompt text after every response. All additions are wrapped in `# TEMPORARY` comments marking them for removal when real image generation is integrated.

**Rationale**: The component renders from `state.designs`, which is shared between frontend and agent via CopilotKit's `useCoAgent` hook. The agent needs a way to populate this array. A `@agent.tool` is the idiomatic PydanticAI approach — the agent decides when to call it, guided by the system prompt. The tool is temporary because it hardcodes `imageUrl="tmp/next.svg"` instead of producing a real diagram. When image generation is integrated, this tool will be replaced with one that produces or receives an actual image URL.

**Alternative considered**: Use a `@agent.result_validator` to automatically append an entry after every response. Rejected because result validators are for post-processing output, not for triggering side effects on state. A tool gives the agent explicit control and a clear docstring to follow. Alternative considered: Call `setState` directly from the frontend after each agent response. Rejected because the state is shared — the agent should own the append logic to keep the data flow unidirectional (agent → state → frontend render).

**Update:** The agent tool approach did not work — the state changes from the agent-side `add_design_entry` tool did not propagate to the frontend as expected. The agent-side code is commented out and preserved for future reference.

### D9: Fallback — frontend `AddDesignButton` component for manual testing

**Decision**: Create a reusable `AddDesignButton` component in `src/components/add-design-button.tsx` that, when clicked, appends a test `DesignEntry` to the shared state. The component accepts `{ state, setState }` props and creates an entry with `imageUrl: "tmp/next.svg"` and `promptText: "Test design #N"`. It is rendered above the design list in `page.tsx`. The component is intentionally generic (accepting state/setState props) so it can be reused for other testing scenarios.

**Rationale**: The agent tool approach failed, so a manual frontend button provides a deterministic way to test the design display component without depending on agent state propagation. Making it a separate component rather than inline logic in `page.tsx` allows reuse — for example, placing it in different layouts or using it in other test pages.

**Alternative considered**: Add the button directly inside `DesignComponent`. Rejected because `DesignComponent` is the display component and should not own mutation logic. Keeping the button separate maintains single-responsibility.

## Risks / Trade-offs

- **[Array index as React key]** → If designs are ever reordered or filtered, array-index keys will cause incorrect reconciliation. Mitigation: the list is append-only for now. If reordering is added later, introduce an `id` field at that time.
- **[No image error handling]** → If an `imageUrl` points to a broken path, the `<img>` will show a broken-image icon. Mitigation: acceptable for testing scope. A follow-up change can add an `onError` fallback.
- **[State shape is a breaking change]** → `AgentState` is being rewritten. Any future code that relies on the old `your_data` field will break. Mitigation: `AgentState` is currently unused by the procurement-codes component at runtime (the component references `state.procurement_codes` which does not exist on the type), and the only other component (`your-component.tsx`) just does `JSON.stringify(state)`, so it will render whatever shape is provided.
- **[Large list performance]** → No virtualization means performance will degrade with hundreds of entries. Mitigation: acceptable for testing and initial rollout. Pagination/virtualization is explicitly a non-goal.
- **[vh-based image height on small screens]** → On very short viewports, 40vh may produce tiny images. Mitigation: acceptable for initial rollout. A `min-height` can be added in a follow-up if needed.

## Migration Plan

1. Update `src/lib/types.ts` with the new `DesignEntry` and `AgentState` types.
2. Rename `src/components/procurement-codes.tsx` to `src/components/design-component.tsx`.
3. Rewrite the component file with the new `DesignComponent` export, scrollable list, standard image sizing, and modal.
4. Replace `<YourComponent>` with `<DesignComponent>` in `src/app/page.tsx` (import + JSX render only; state shape already aligned).
5. Add `DesignEntry` model, `designs` field, `add_design_entry` tool, and system prompt update to `agent/src/agent.py` (all marked TEMPORARY).
6. Verify the component renders correctly with empty state and with populated entries using `tmp/next.svg`.
7. Verify image click opens the modal and Escape/backdrop click dismisses it.

No rollback strategy is needed — the old component is unused and the old types are not referenced at runtime.

## Open Questions

_(None — all design decisions are resolved.)_
