## 1. Types and File Rename

- [x] 1.1 Update `src/lib/types.ts`: remove `YourDataType` and the old `AgentState` definition. Add exported `DesignEntry` interface with `imageUrl: string` and `promptText: string`. Redefine `AgentState` as `{ designs: DesignEntry[] }`.
  **Done when:** File `src/lib/types.ts` contains `export interface DesignEntry` with fields `imageUrl: string` and `promptText: string`, contains `export type AgentState` with field `designs: DesignEntry[]`, does NOT contain `YourDataType`, and `npx tsc --noEmit` exits zero.
  **Stop and hand off if:** TypeScript compilation fails and the error is not caused by this change (e.g., pre-existing errors in unrelated files).

- [x] 1.2 Rename `src/components/procurement-codes.tsx` to `src/components/design-component.tsx` using `git mv`.
  **Done when:** `test -f src/components/design-component.tsx` succeeds, `test -f src/components/procurement-codes.tsx` fails, and `git status` shows the rename.

## 2. Component Rewrite — Core Structure and Scrollable List

- [x] 2.1 Rewrite `src/components/design-component.tsx`: remove all `xlsx` imports, remove `ProcurementCodesProps` interface, remove all download handlers (TXT, CSV, XLSX), remove the delete button per entry, remove the old `ProcurementCodes` export. Add new `DesignComponentProps` interface with `{ state: AgentState; setState: (state: AgentState) => void }`. Export a named `DesignComponent` function component. The component body can return a placeholder `<div>` for now — the render details are in task 2.2.
  **Done when:** File `src/components/design-component.tsx` does NOT contain `import.*xlsx`, does NOT contain `ProcurementCodesProps`, does NOT contain `handleDownload`, does NOT contain `handleDownloadCSV`, does NOT contain `handleDownloadExcel`, does NOT contain `handleDownloadText`, does NOT contain `ProcurementCodes` export. File DOES contain `export function DesignComponent` and `DesignComponentProps`. `npx tsc --noEmit` exits zero.
  **Stop and hand off if:** `npx tsc --noEmit` fails and the error is in this file but the cause is unclear from the error message.

- [ ] 2.2 Implement the render body of `DesignComponent`: show a header, an empty-state message when `state.designs` is empty or undefined, and a vertical list of cards inside a scrollable container when entries exist. The scrollable container SHALL use `overflow-y: auto` with a `max-height` so multiple cards are visible simultaneously. Each card SHALL render an `<img>` with `width: 80%` of card width, `height: 40vh`, and `object-fit: contain`, plus a text element with `entry.promptText` below the image. Use glassmorphism styling (`bg-white/20 backdrop-blur-md rounded-2xl shadow-xl`). No delete buttons, no download buttons. The `<img>` elements SHALL have `onClick` handlers (wire to a no-op `() => {}` for now — modal wiring is in task 3.1).
  **Done when:** File `src/components/design-component.tsx` contains a `<div>` or `<section>` with `overflow-y: auto` class, contains `<img` elements with `object-fit: contain` style or class, contains a fallback/empty-state element (e.g., "No designs" text) rendered when `state.designs` is empty, contains `entry.promptText` or `item.promptText` in a text element, and `npx tsc --noEmit` exits zero.
  **Stop and hand off if:** `npx tsc --noEmit` fails and the error is in this file but unclear how to resolve.

## 3. Image Modal

- [ ] 3.1 Add modal state and rendering to `DesignComponent`: add `useState<string | null>(null)` for `modalImageUrl`. Replace the image `onClick` no-op from task 2.2 with `() => setModalImageUrl(entry.imageUrl)`. When `modalImageUrl` is non-null, render a fixed-position overlay (`fixed inset-0 z-50 bg-black/80 flex items-center justify-center`) containing an `<img>` with `src={modalImageUrl}`, `max-width: 90vw`, `max-height: 90vh`, `object-fit: contain`. On the image element, call `e.stopPropagation()` on click. On the overlay div, call `() => setModalImageUrl(null)` on click. Add a `useEffect` that attaches a `keydown` listener for the `Escape` key calling `() => setModalImageUrl(null)`, with cleanup on unmount.
  **Done when:** File `src/components/design-component.tsx` contains `useState`, contains `modalImageUrl` or equivalent state variable, contains `e.stopPropagation()`, contains `keydown` or `Escape` listener in a `useEffect`, contains an overlay element with `fixed` and `z-50` classes, and `npx tsc --noEmit` exits zero.
  **Stop and hand off if:** `npx tsc --noEmit` fails due to a React hooks rule violation that is not resolved by a single fix attempt.

## 4. Final Verification

- [ ] 4.1 Run `npx tsc --noEmit && npm run lint` across the full codebase and confirm both exit zero. Verify structural requirements: `grep -c 'export function DesignComponent' src/components/design-component.tsx` returns 1, `grep -c 'export interface DesignEntry' src/lib/types.ts` returns 1, `grep -c 'designs.*DesignEntry' src/lib/types.ts` returns at least 1, `test ! -f src/components/procurement-codes.tsx` succeeds.
  **Done when:** `npx tsc --noEmit` exits zero, `npm run lint` exits zero, all grep/test commands above succeed.
  **Stop and hand off if:** Typecheck or lint fails in a file that was not modified by this change (pre-existing issue).
