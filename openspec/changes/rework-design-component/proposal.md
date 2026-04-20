## Why

The current `src/components/procurement-codes.tsx` component is unused and implements procurement-code download functionality that does not align with the application's design-oriented workflow. The application needs a component that displays AI-generated design diagrams alongside the user prompts that produced them. This component will serve as the visual output area where each completed AI prompt results in a new design entry showing the generated diagram image and its associated prompt text.

## What Changes

- **BREAKING**: Rename `src/components/procurement-codes.tsx` to `src/components/design-component.tsx` and replace the exported component name from `ProcurementCodes` to `DesignComponent`.
- Remove all procurement-specific logic: TXT/CSV/XLSX download handlers, `xlsx` imports, and `procurement_codes` state references.
- Update `AgentState` in `src/lib/types.ts` to replace the `procurement_codes`-related types with a new `DesignEntry` type and a `designs` array field.
- Add image display support: each `DesignEntry` renders an `<img>` element sourced from a URL/path. During testing, all image sources resolve to `tmp/next.svg`. The component must accept standard image formats (jpg, jpeg, png, gif, svg, webp, bmp).
- Add prompt text display: each `DesignEntry` renders the user prompt text below its image as a description/caption.
- Add append behavior: when the AI agent finishes processing a prompt, the calling code appends a new `DesignEntry` to the `designs` array, which causes a new card to appear in the component's list.
- Remove individual entry deletion buttons (the procurement-codes pattern of per-item remove). This is a growing list, not a managed list.

## Capabilities

### New Capabilities

- `design-display`: A component that renders a scrollable list of design entries. Each entry displays an image and its associated user-prompt text. The list grows as the AI agent completes prompts. During testing, all images resolve to `tmp/next.svg`.

### Modified Capabilities

_(None — no existing specs are being modified.)_

## Impact

- **Files modified**: `src/components/procurement-codes.tsx` (renamed to `design-component.tsx`, heavily rewritten), `src/lib/types.ts` (new types, removed old types).
- **Dependencies removed**: `xlsx` import in the component (the library may still be used elsewhere).
- **Breaking change**: Any code importing `ProcurementCodes` or `procurement_codes` state must be updated. Currently no code imports the component or references that state field, so migration impact is zero.
- **State shape**: `AgentState` changes from `procurement_codes` array to `designs` array with `DesignEntry` items containing `imageUrl` and `promptText` fields.

## Non-Goals

- Image upload or file picker functionality — images are sourced programmatically by the AI agent, not uploaded by the user.
- Image format conversion or validation beyond standard web `<img>` tag support.
- Download/export functionality for designs (removed from procurement codes, not replaced).
- Pagination or virtual scrolling for large lists (deferred to a follow-up change).
- Persisting designs across page reloads or sessions.

## Testing Approach

- All image sources point to `tmp/next.svg` (already present in the repository) for deterministic rendering.
- The component must render correctly when the `designs` array is empty (show an empty-state message) and when it contains one or more entries.
- Verification is visual/structural: each entry must contain an `<img>` element and a text element with the prompt string.

## Human Handoff

_(None — this change is fully implementable without manual intervention.)_
