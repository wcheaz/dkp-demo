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
