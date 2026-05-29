## 1. Pre-flight

- [x] 1.1 **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/click-to-reactivate-viewer-typecheck.txt` exists with `npx tsc --noEmit` output and ends with `EXIT=<integer>`
    - `.ralph/baselines/click-to-reactivate-viewer-lint.txt` exists with `npx next lint` output and ends with `EXIT=<integer>`
    - `.ralph/baselines/click-to-reactivate-viewer-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Remove screenshot infrastructure from CadViewer

- [ ] 2.1 **Remove captureViewToDataUrl, emitPreview, and onCapturePreview from cad-viewer.tsx**
  - Scope: `src/components/cad-viewer.tsx`
  - Change: The `CadViewer` component no longer accepts `onCapturePreview`, no longer contains `captureViewToDataUrl()`, `emitPreview()`, or any WebGL pixel-reading code. The component only handles live rendering: mount → load DXF → auto-zoom → unmount → destroy.
  - Done when:
    - `rg "captureViewToDataUrl" src/components/cad-viewer.tsx` returns no matches
    - `rg "emitPreview" src/components/cad-viewer.tsx` returns no matches
    - `rg "onCapturePreview" src/components/cad-viewer.tsx` returns no matches
    - `rg "readPixels" src/components/cad-viewer.tsx` returns no matches
    - `npx tsc --noEmit` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: removing the screenshot code breaks the component's core rendering logic (mount/load/unmount cycle).

## 3. Implement click-to-reactivate in DesignComponent

- [ ] 3.1 **Replace computed activeViewerIndex with user-controllable state and add click handler**
  - Scope: `src/components/design-component.tsx`
  - Change: The `activeViewerIndex` becomes a `useState<number>` initialized to the last DXF-bearing index. A click handler updates it. The state resets when the `designs` array length changes (new design appended). Inactive designs with `dxfContent` render a clickable overlay instead of the placeholder `<img>`.
  - Done when:
    - `rg "activeViewerIndex" src/components/design-component.tsx` shows a `useState` declaration (not `useMemo` or `reduce`)
    - Clicking the overlay of an inactive DXF design changes `activeViewerIndex` to that design's index
    - The `CadViewer` receives `key={entry.id}` and only renders for `index === activeViewerIndex`
    - `rg "handleCapturePreview" src/components/design-component.tsx` returns no matches (callback removed)
    - `rg "dxfPreview" src/components/design-component.tsx` returns no matches (preview image fallback removed)
    - `rg "onCapturePreview" src/components/design-component.tsx` returns no matches
    - `npx tsc --noEmit` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: the `CadViewer` key-based remounting pattern from design decision 3 conflicts with the state-driven index switching.

## 4. Cleanup

- [ ] 4.1 **Remove dxfPreview field from DesignEntry type**
  - Scope: `src/lib/types.ts`
  - Change: The `dxfPreview?: string` field is removed from `DesignEntry`. No code references it.
  - Done when:
    - `rg "dxfPreview" src/` returns no matches
    - `npx tsc --noEmit` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if: other code outside `src/` references `dxfPreview`.

## 5. Final quality gate

- [ ] 5.1 **Verify full build and lint pass**
  - Scope: project root
  - Change: All code changes are verified clean.
  - Done when:
    - `npx tsc --noEmit` exits 0
    - `npx next lint` exits 0, or failures match the pre-flight baseline with no new failures
  - Stop and hand off if: new failures appear that are not in the pre-flight baseline and are not directly caused by this change's edits.
