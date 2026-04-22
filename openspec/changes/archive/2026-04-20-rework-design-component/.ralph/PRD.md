# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

## Why

The current `src/components/procurement-codes.tsx` component is unused and implements procurement-code download functionality that does not align with the application's design-oriented workflow. The application needs a component that displays AI-generated design diagrams alongside the user prompts that produced them. This component will serve as the visual output area where each completed AI prompt results in a new design entry showing the generated diagram image and its associated prompt text. Multiple designs must be visible simultaneously in a scrollable list, images must have a consistent standard size, and users must be able to click any image to view it enlarged in a modal overlay.

## What Changes

- **BREAKING**: Rename `src/components/procurement-codes.tsx` to `src/components/design-component.tsx` and replace the exported component name from `ProcurementCodes` to `DesignComponent`.
- Remove all procurement-specific logic: TXT/CSV/XLSX download handlers, `xlsx` imports, and `procurement_codes` state references.
- Update `AgentState` in `src/lib/types.ts` to replace the `procurement_codes`-related types with a new `DesignEntry` type and a `designs` array field.
- Add image display support: each `DesignEntry` renders an `<img>` element sourced from a URL/path. During testing, all image sources resolve to `tmp/next.svg`. The component must accept standard image formats (jpg, jpeg, png, gif, svg, webp, bmp).
- Add prompt text display: each `DesignEntry` renders the user prompt text below its image as a description/caption.
- Add append behavior: when the AI agent finishes processing a prompt, the calling code appends a new `DesignEntry` to the `designs` array, which causes a new card to appear in the component's list.
- Add a temporary agent tool (`add_design_entry`) in `agent/src/agent.py` that appends a `DesignEntry` to the shared agent state after every agent execution. The tool is temporary (marked with comments) and will be replaced when real image generation is integrated. The agent state (`YourState`) needs a `designs` field to sync with the frontend's `AgentState.designs` via CopilotKit's shared state. **Update:** The agent tool approach did not work for automatic state propagation. The agent-side code is commented out and preserved for future reference. Instead, a reusable `AddDesignButton` component is added to the frontend for manual testing — clicking the button appends a test design entry with `imageUrl: "tmp/next.svg"` and generic prompt text.
- Integrate `DesignComponent` into the frontend page (`src/app/page.tsx`), replacing the existing `<YourComponent>` render. The `useCoAgent` hook already initializes `designs: []` and `useCopilotReadable` already reads `state.designs`, so only the import and JSX render need to change.
- Remove individual entry deletion buttons (the procurement-codes pattern of per-item remove). This is a growing list, not a managed list.
- Add scrollable container: the list of design cards SHALL be wrapped in a scrollable container so that multiple designs are visible at once and the user can scroll to see earlier entries.
- Add standard image sizing: each image in a card SHALL be sized to 80% (4/5ths) of the card's natural width, with a height of approximately 40% (2/5ths) of the viewport height. Images SHALL scale proportionally within these bounds.
- Add image modal: clicking any image SHALL open a modal overlay displaying the image at a larger size. The modal SHALL be dismissible by clicking outside the image or pressing Escape.

## Capabilities

### New Capabilities

- `design-display`: A component that renders a scrollable list of design entries with multiple entries visible simultaneously. Each entry displays a consistently-sized image and its associated user-prompt text. Clicking an image opens a full-screen modal overlay with the enlarged image. The list grows as the AI agent completes prompts. During testing, all images resolve to `tmp/next.svg`.

### Modified Capabilities

_(None — no existing specs are being modified.)_

## Impact

- **Files modified**: `src/components/procurement-codes.tsx` (renamed to `design-component.tsx`, heavily rewritten), `src/lib/types.ts` (new types, removed old types), `src/app/page.tsx` (replace `<YourComponent>` with `<DesignComponent>`, add `<AddDesignButton>`), `src/components/add-design-button.tsx` (new reusable component), `agent/src/agent.py` (agent tool additions commented out, preserved for reference).
- **Dependencies removed**: `xlsx` import in the component (the library may still be used elsewhere).
- **Dependencies added**: None — the modal is implemented with plain React state and CSS (no external modal library).
- **Breaking change**: Any code importing `ProcurementCodes` or `procurement_codes` state must be updated. Currently no code imports the component or references that state field, so migration impact is zero.
- **State shape**: `AgentState` changes from `procurement_codes` array to `designs` array with `DesignEntry` items containing `imageUrl` and `promptText` fields.

## Non-Goals

- Image upload or file picker functionality — images are sourced programmatically by the AI agent, not uploaded by the user.
- Image format conversion or validation beyond standard web `<img>` tag support.
- Download/export functionality for designs (removed from procurement codes, not replaced).
- Pagination or virtual scrolling for large lists (deferred to a follow-up change).
- Persisting designs across page reloads or sessions.
- Carousel, grid, or non-vertical layout modes for the design list.
- Zoom, pan, or rotation controls within the modal.

## Testing Approach

- All image sources point to `tmp/next.svg` (already present in the repository) for deterministic rendering.
- The component must render correctly when the `designs` array is empty (show an empty-state message) and when it contains one or more entries.
- Verification is visual/structural: each entry must contain an `<img>` element and a text element with the prompt string.
- Image sizing is verified by inspecting computed styles: image width SHALL be ~80% of card width, height SHALL be ~40vh.
- Modal behavior is verified by clicking an image and confirming an overlay appears with the same image at a larger size.

## Human Handoff

_(None — this change is fully implementable without manual intervention.)_

## Specifications

design-display/spec.md
## ADDED Requirements

### Requirement: DesignComponent renders a scrollable list of design entries
The `DesignComponent` SHALL accept an `AgentState` containing a `designs` array of `DesignEntry` objects. Each `DesignEntry` SHALL have an `imageUrl` (string) and a `promptText` (string). The component SHALL render one card per entry inside a scrollable container. Multiple cards SHALL be visible simultaneously. The scrollable container SHALL use `overflow-y: auto` so the user can scroll through the design history. Each card SHALL contain an `<img>` element with `src` set to the entry's `imageUrl` and a text element displaying the entry's `promptText`.

#### Scenario: Empty state when no designs exist
- **WHEN** the `designs` array on `AgentState` is empty or undefined
- **THEN** the component SHALL display an empty-state message indicating no designs are available, and SHALL render zero design cards.

#### Scenario: Single design entry displayed
- **WHEN** the `designs` array contains one `DesignEntry` with `imageUrl` set to `"tmp/next.svg"` and `promptText` set to `"Draw a flowchart of user login"`
- **THEN** the component SHALL render exactly one card containing an `<img>` element whose `src` attribute equals `"tmp/next.svg"` and a text element containing `"Draw a flowchart of user login"`.

#### Scenario: Multiple design entries displayed in order with scroll
- **WHEN** the `designs` array contains five entries in order: A, B, C, D, E
- **THEN** the component SHALL render five cards in the same order inside a scrollable container, each showing its own image and prompt text. At least two cards SHALL be visible without scrolling.

### Requirement: DesignComponent accepts standard image formats
The `<img>` element in each design card SHALL accept any standard image format path or URL assigned to `imageUrl`, including but not limited to: jpg, jpeg, png, gif, svg, webp, and bmp. The component SHALL NOT perform format validation or conversion — it SHALL pass `imageUrl` directly to the `<img src>` attribute.

#### Scenario: PNG image renders without error
- **WHEN** a `DesignEntry` has `imageUrl` set to `"tmp/design-output.png"`
- **THEN** the component SHALL render an `<img>` element with `src="tmp/design-output.png"` without throwing or catching format errors.

#### Scenario: SVG image renders without error
- **WHEN** a `DesignEntry` has `imageUrl` set to `"tmp/next.svg"`
- **THEN** the component SHALL render an `<img>` element with `src="tmp/next.svg"` without throwing or catching format errors.

### Requirement: Images have a standard consistent size
Each image in a design card SHALL be sized to `width: 80%` (4/5ths) of the card's natural width and `height: 40vh` (approximately 2/5ths of the viewport height). Images SHALL use `object-fit: contain` to preserve their aspect ratio within these bounds without distortion.

#### Scenario: Image dimensions are consistent across entries
- **WHEN** the `designs` array contains three entries with different source images
- **THEN** all three `<img>` elements SHALL have the same computed width (80% of card width) and the same computed height (40vh), and all SHALL have `object-fit: contain`.

#### Scenario: Image does not overflow card bounds
- **WHEN** a design card is rendered with an image
- **THEN** the image SHALL NOT cause horizontal overflow of the card. The image width SHALL be constrained to 80% of the card width.

### Requirement: Clicking an image opens a modal overlay
The component SHALL implement a modal overlay for image enlargement. When the user clicks an `<img>` element in a design card, the component SHALL set internal state to display a modal. The modal SHALL render a fixed-position overlay covering the entire viewport (`position: fixed; inset: 0`) with a semi-transparent dark backdrop (`bg-black/80` or equivalent). The modal SHALL display the clicked image at a larger size constrained by `max-width: 90vw` and `max-height: 90vh` with `object-fit: contain`, centered within the overlay.

#### Scenario: Click image opens modal
- **WHEN** the user clicks on an `<img>` element inside a design card
- **THEN** a modal overlay SHALL appear covering the viewport, displaying the same image at a larger size (up to 90vw × 90vh).

#### Scenario: Modal displays correct image
- **WHEN** the user clicks the image of the second design entry (imageUrl: `"tmp/second.svg"`)
- **THEN** the modal SHALL display an `<img>` with `src="tmp/second.svg"` at the enlarged size.

### Requirement: Modal is dismissible by backdrop click and Escape key
The modal SHALL close and disappear when the user clicks on the backdrop area (outside the enlarged image) or presses the Escape key. Clicking on the enlarged image itself SHALL NOT close the modal.

#### Scenario: Clicking backdrop closes modal
- **WHEN** the modal is open and the user clicks on the dark backdrop area (not on the image)
- **THEN** the modal SHALL close and the overlay SHALL be removed from the DOM.

#### Scenario: Pressing Escape closes modal
- **WHEN** the modal is open and the user presses the Escape key
- **THEN** the modal SHALL close and the overlay SHALL be removed from the DOM.

#### Scenario: Clicking the enlarged image does not close modal
- **WHEN** the modal is open and the user clicks on the enlarged image itself
- **THEN** the modal SHALL remain open.

### Requirement: AgentState carries designs array
`AgentState` in `src/lib/types.ts` SHALL define a `designs` field of type `DesignEntry[]`. `DesignEntry` SHALL be an exported interface with `imageUrl: string` and `promptText: string`. The old `procurement_codes`-related types and `your_data` field SHALL be removed from `AgentState`.

#### Scenario: AgentState type compiles with designs field
- **WHEN** TypeScript compilation is run on `src/lib/types.ts`
- **THEN** the file SHALL compile without errors and `AgentState` SHALL have exactly one field: `designs: DesignEntry[]`.

#### Scenario: DesignEntry has required fields
- **WHEN** a `DesignEntry` object is created with `{ imageUrl: "tmp/next.svg", promptText: "test prompt" }`
- **THEN** the object SHALL satisfy the `DesignEntry` interface without TypeScript errors.

### Requirement: DesignComponent is exported from design-component.tsx
The component SHALL be exported as a named export `DesignComponent` from `src/components/design-component.tsx`. The old file `src/components/procurement-codes.tsx` SHALL NOT exist after this change. The old named export `ProcurementCodes` SHALL NOT exist.

#### Scenario: Import DesignComponent succeeds
- **WHEN** another module imports `{ DesignComponent }` from `@/components/design-component`
- **THEN** the import SHALL resolve without error and `DesignComponent` SHALL be a valid React function component.

#### Scenario: Old procurement-codes file does not exist
- **WHEN** the filesystem is checked for `src/components/procurement-codes.tsx`
- **THEN** the file SHALL NOT exist.

### Requirement: Designs list is append-only
The component SHALL render the `designs` array as a read-only display. The component SHALL NOT provide UI for deleting, reordering, or editing entries. New entries are appended to the array by external calling code (the AI agent's post-prompt handler) via `setState`.

#### Scenario: No delete button on entries
- **WHEN** the `designs` array contains one or more entries and the component is rendered
- **THEN** each design card SHALL NOT contain a delete, remove, or close button.

#### Scenario: Appending a new design via setState
- **WHEN** external code calls `setState` with a new `AgentState` where `designs` is `[...existingDesigns, newEntry]`
- **THEN** the component SHALL re-render showing all previous entries plus the new entry at the end of the list.

### Requirement: DesignComponent is rendered in the frontend page
`src/app/page.tsx` SHALL import and render `DesignComponent` instead of `YourComponent`. The `<YourComponent>` reference SHALL be replaced with `<DesignComponent state={state} setState={setState} />`. The old `YourComponent` import SHALL be removed.

#### Scenario: Page imports DesignComponent
- **WHEN** `src/app/page.tsx` is inspected
- **THEN** the file SHALL contain `import { DesignComponent } from "@/components/design-component"` and SHALL NOT contain `import.*YourComponent`.

#### Scenario: Page renders DesignComponent
- **WHEN** `src/app/page.tsx` is rendered in the browser
- **THEN** the page SHALL render `<DesignComponent>` with `state` and `setState` props, and SHALL NOT render `<YourComponent>`.

### Requirement: Agent tool code is commented out and preserved
The `DesignEntry` model, `designs` field on `YourState`, and `add_design_entry` tool in `agent/src/agent.py` SHALL be commented out (not deleted). The agent's `system_prompt` SHALL NOT reference `add_design_entry`. This code is preserved for future reference when real image generation is integrated.

#### Scenario: Agent code is commented out
- **WHEN** `agent/src/agent.py` is inspected for `add_design_entry`
- **THEN** the `DesignEntry` class, `designs` field, and `add_design_entry` function SHALL be present but commented out.
- **AND** the `system_prompt` string SHALL NOT contain `add_design_entry`.

#### Scenario: Agent passes lint and typecheck
- **WHEN** `cd agent && python -m ruff check . && python -m mypy .` is run
- **THEN** both commands SHALL exit zero with no errors.

### Requirement: AddDesignButton component appends test entries
A reusable `AddDesignButton` component SHALL be exported from `src/components/add-design-button.tsx`. It SHALL accept `{ state: AgentState; setState: (state: AgentState) => void }` props. When clicked, the button SHALL append a `DesignEntry` with `imageUrl: "tmp/next.svg"` and `promptText: "Test design #N"` (where N is the new total count) to `state.designs` via `setState`. The component is intentionally generic for reuse in other contexts.

#### Scenario: Button click appends entry
- **WHEN** the user clicks the `AddDesignButton` and the current `state.designs` has 0 entries
- **THEN** `setState` SHALL be called with a new state where `designs` contains one entry with `imageUrl: "tmp/next.svg"` and `promptText: "Test design #1"`.

#### Scenario: Multiple clicks append multiple entries
- **WHEN** the user clicks `AddDesignButton` three times
- **THEN** `state.designs` SHALL contain three entries with prompt texts "Test design #1", "Test design #2", and "Test design #3", in order.

### Requirement: AddDesignButton is rendered in the frontend page
`src/app/page.tsx` SHALL import and render `AddDesignButton` above the `DesignComponent` render within `YourMainContent`. The button SHALL receive `state` and `setState` as props.

#### Scenario: Page imports and renders AddDesignButton
- **WHEN** `src/app/page.tsx` is inspected
- **THEN** the file SHALL contain `import { AddDesignButton } from "@/components/add-design-button"` and SHALL render `<AddDesignButton state={state} setState={setState} />` above `<DesignComponent>`.

### Requirement: Test images resolve to tmp/next.svg
During testing, all `DesignEntry` instances SHALL have their `imageUrl` set to `"tmp/next.svg"`. This ensures deterministic rendering without depending on external image generation.

#### Scenario: Test entry uses tmp/next.svg
- **WHEN** a test creates a `DesignEntry` with `imageUrl: "tmp/next.svg"`
- **THEN** the rendered `<img>` element SHALL have `src="tmp/next.svg"` and the file `tmp/next.svg` SHALL exist in the repository.



## Design

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

## Current Task Context

## Current Task
- 5.1 Comment out the agent-side TEMPORARY changes in `agent/src/agent.py`. The `add_design_entry` tool approach did not work for automatic state propagation, so the code must be disabled without deleting it (preserved for future reference). Specifically:
## Completed Tasks for Git Commit
- [x] 1.1 Update `src/lib/types.ts`: remove `YourDataType` and the old `AgentState` definition. Add exported `DesignEntry` interface with `imageUrl: string` and `promptText: string`. Redefine `AgentState` as `{ designs: DesignEntry[] }`.
- [x] 1.2 Rename `src/components/procurement-codes.tsx` to `src/components/design-component.tsx` using `git mv`.
- [x] 2.1 Rewrite `src/components/design-component.tsx`: remove all `xlsx` imports, remove `ProcurementCodesProps` interface, remove all download handlers (TXT, CSV, XLSX), remove the delete button per entry, remove the old `ProcurementCodes` export. Add new `DesignComponentProps` interface with `{ state: AgentState; setState: (state: AgentState) => void }`. Export a named `DesignComponent` function component. The component body can return a placeholder `<div>` for now — the render details are in task 2.2.
- [x] 2.2 Implement the render body of `DesignComponent`: show a header, an empty-state message when `state.designs` is empty or undefined, and a vertical list of cards inside a scrollable container when entries exist. The scrollable container SHALL use `overflow-y: auto` with a `max-height` so multiple cards are visible simultaneously. Each card SHALL render an `<img>` with `width: 80%` of card width, `height: 40vh`, and `object-fit: contain`, plus a text element with `entry.promptText` below the image. Use glassmorphism styling (`bg-white/20 backdrop-blur-md rounded-2xl shadow-xl`). No delete buttons, no download buttons. The `<img>` elements SHALL have `onClick` handlers (wire to a no-op `() => {}` for now — modal wiring is in task 3.1).
- [x] 3.1 Add modal state and rendering to `DesignComponent`: add `useState<string | null>(null)` for `modalImageUrl`. Replace the image `onClick` no-op from task 2.2 with `() => setModalImageUrl(entry.imageUrl)`. When `modalImageUrl` is non-null, render a fixed-position overlay (`fixed inset-0 z-50 bg-black/80 flex items-center justify-center`) containing an `<img>` with `src={modalImageUrl}`, `max-width: 90vw`, `max-height: 90vh`, `object-fit: contain`. On the image element, call `e.stopPropagation()` on click. On the overlay div, call `() => setModalImageUrl(null)` on click. Add a `useEffect` that attaches a `keydown` listener for the `Escape` key calling `() => setModalImageUrl(null)`, with cleanup on unmount.
- [x] 4.1 Replace `<YourComponent>` with `<DesignComponent>` in `src/app/page.tsx`. Add import `import { DesignComponent } from "@/components/design-component"` at the top of the file. Replace the `<YourComponent state={state} setState={setState} />` render at line 319 with `<DesignComponent state={state} setState={setState} />`. Remove or comment out the old `import { YourComponent }` import line. The `useCoAgent<AgentState>` hook already initializes `initialState: { designs: [] }` and `useCopilotReadable` already reads `state.designs`, so no changes to state initialization are needed.
