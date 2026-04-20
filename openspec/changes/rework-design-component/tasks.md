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

- [x] 2.2 Implement the render body of `DesignComponent`: show a header, an empty-state message when `state.designs` is empty or undefined, and a vertical list of cards inside a scrollable container when entries exist. The scrollable container SHALL use `overflow-y: auto` with a `max-height` so multiple cards are visible simultaneously. Each card SHALL render an `<img>` with `width: 80%` of card width, `height: 40vh`, and `object-fit: contain`, plus a text element with `entry.promptText` below the image. Use glassmorphism styling (`bg-white/20 backdrop-blur-md rounded-2xl shadow-xl`). No delete buttons, no download buttons. The `<img>` elements SHALL have `onClick` handlers (wire to a no-op `() => {}` for now — modal wiring is in task 3.1).
  **Done when:** File `src/components/design-component.tsx` contains a `<div>` or `<section>` with `overflow-y: auto` class, contains `<img` elements with `object-fit: contain` style or class, contains a fallback/empty-state element (e.g., "No designs" text) rendered when `state.designs` is empty, contains `entry.promptText` or `item.promptText` in a text element, and `npx tsc --noEmit` exits zero.
  **Stop and hand off if:** `npx tsc --noEmit` fails and the error is in this file but unclear how to resolve.

## 3. Image Modal

- [x] 3.1 Add modal state and rendering to `DesignComponent`: add `useState<string | null>(null)` for `modalImageUrl`. Replace the image `onClick` no-op from task 2.2 with `() => setModalImageUrl(entry.imageUrl)`. When `modalImageUrl` is non-null, render a fixed-position overlay (`fixed inset-0 z-50 bg-black/80 flex items-center justify-center`) containing an `<img>` with `src={modalImageUrl}`, `max-width: 90vw`, `max-height: 90vh`, `object-fit: contain`. On the image element, call `e.stopPropagation()` on click. On the overlay div, call `() => setModalImageUrl(null)` on click. Add a `useEffect` that attaches a `keydown` listener for the `Escape` key calling `() => setModalImageUrl(null)`, with cleanup on unmount.
  **Done when:** File `src/components/design-component.tsx` contains `useState`, contains `modalImageUrl` or equivalent state variable, contains `e.stopPropagation()`, contains `keydown` or `Escape` listener in a `useEffect`, contains an overlay element with `fixed` and `z-50` classes, and `npx tsc --noEmit` exits zero.
  **Stop and hand off if:** `npx tsc --noEmit` fails due to a React hooks rule violation that is not resolved by a single fix attempt.

## 4. Frontend Integration

- [x] 4.1 Replace `<YourComponent>` with `<DesignComponent>` in `src/app/page.tsx`. Add import `import { DesignComponent } from "@/components/design-component"` at the top of the file. Replace the `<YourComponent state={state} setState={setState} />` render at line 319 with `<DesignComponent state={state} setState={setState} />`. Remove or comment out the old `import { YourComponent }` import line. The `useCoAgent<AgentState>` hook already initializes `initialState: { designs: [] }` and `useCopilotReadable` already reads `state.designs`, so no changes to state initialization are needed.
  **Done when:** `grep -c 'DesignComponent' src/app/page.tsx` returns at least 2 (import + render), `grep -c 'YourComponent' src/app/page.tsx` returns 0, `npx tsc --noEmit` exits zero.
  **Stop and hand off if:** `npx tsc --noEmit` fails and the error is in `page.tsx` but the `DesignComponent` import or prop types do not match expectations.

## 5. Agent Tool — Comment Out and Fallback to Manual Testing

- [x] 5.1 Comment out the agent-side TEMPORARY changes in `agent/src/agent.py`. The `add_design_entry` tool approach did not work for automatic state propagation, so the code must be disabled without deleting it (preserved for future reference). Specifically:
  1. Comment out the `DesignEntry` model class (lines ~71-74).
  2. Comment out the `designs` field on `YourState` (line ~83).
  3. Comment out the `add_design_entry` tool function (lines ~284-299).
  4. Remove the `add_design_entry` instruction from the `system_prompt` string (lines ~139-141) — restore the system prompt to end after the existing "cite the source document path" instruction.
  **Done when:** `grep -c 'add_design_entry' agent/src/agent.py` returns 0 (no active references), the `DesignEntry` class and `designs` field are wrapped in `#` comment lines, the system prompt does NOT reference `add_design_entry`, and `cd agent && python -m ruff check . && python -m mypy .` both exit zero.
  **Stop and hand off if:** Commenting out `DesignEntry` or `designs` causes import errors in other parts of the agent that reference these symbols.

- [x] 5.2 Create a new reusable component `src/components/add-design-button.tsx` that renders a button which, when clicked, appends a test design entry to the designs array. The component SHALL be exported as `AddDesignButton` and accept `{ state: AgentState; setState: (state: AgentState) => void }` props. The button's `onClick` handler SHALL create a `DesignEntry` with `imageUrl: "tmp/next.svg"` and `promptText: "Test design #N"` (where N is `state.designs.length + 1`), then call `setState` with the new entry appended to `state.designs`. The button SHALL use glassmorphism styling consistent with the rest of the UI (`bg-white/20 hover:bg-white/30 text-white font-bold py-2 px-4 rounded-full`). The component is intentionally generic and reusable — it accepts `state`/`setState` props rather than hardcoding state access.
  **Done when:** File `src/components/add-design-button.tsx` exists, contains `export function AddDesignButton`, contains `import.*AgentState` and `import.*DesignEntry` from `@/lib/types`, contains an `<button>` element, and `npx tsc --noEmit` exits zero.
  **Stop and hand off if:** `npx tsc --noEmit` fails because `AgentState` or `DesignEntry` are not correctly exported from `@/lib/types`.

- [ ] 5.3 Integrate `AddDesignButton` into `src/app/page.tsx`. Add import `import { AddDesignButton } from "@/components/add-design-button"`. Render `<AddDesignButton state={state} setState={setState} />` in `YourMainContent`, positioned above the `<DesignComponent>` render. The button and the design list should be stacked vertically within the same container.
  **Done when:** `grep -c 'AddDesignButton' src/app/page.tsx` returns at least 2 (import + render), `npx tsc --noEmit` exits zero, and the page renders a clickable button above the design list.
  **Stop and hand off if:** `npx tsc --noEmit` fails because the `AddDesignButton` import does not resolve or prop types mismatch.

## 6. Final Verification

- [ ] 6.1 Run `npx tsc --noEmit && npm run lint` on the frontend and `cd agent && python -m ruff check . && python -m mypy .` on the agent. Confirm all exit zero. Verify structural requirements: `grep -c 'export function DesignComponent' src/components/design-component.tsx` returns 1, `grep -c 'export function AddDesignButton' src/components/add-design-button.tsx` returns 1, `grep -c 'export interface DesignEntry' src/lib/types.ts` returns 1, `test ! -f src/components/procurement-codes.tsx` succeeds, `grep -c 'DesignComponent' src/app/page.tsx` returns at least 2, `grep -c 'AddDesignButton' src/app/page.tsx` returns at least 2, `grep -c 'add_design_entry' agent/src/agent.py` returns 0 (all commented out), `grep -c 'TEMPORARY' agent/src/agent.py` returns at least 1 (preserved comments).
  **Done when:** All four commands exit zero and all grep/test assertions succeed.
  **Stop and hand off if:** Typecheck or lint fails in a file that was not modified by this change (pre-existing issue).
