# click-to-reactivate-viewer — Quality Gate Baselines

## Gates

| Gate | Status | Exit Code | Notes |
|------|--------|-----------|-------|
| `npx tsc --noEmit` | PASS | 0 | Clean, no errors |
| `npx eslint .` | FAIL | 1 | 1833 problems (29 errors, 1804 warnings) |

## Failing Gate Details — `npx eslint .`

### Source file errors (non-worker)

**`src/app/page.tsx`** — 1 error:
- `react-compiler/no-mutating-ref` (lines 375, 470, 545, 598, 710, 815): `latestStateRef.current` cannot be modified inside effect/callback (react-compiler rule)

**`src/components/cad-viewer.tsx`** — 0 errors, 1 warning:
- `react-hooks/exhaustive-deps` (line 143): missing dep `dxfContent`

**`src/components/design-component.tsx`** — 0 errors, 5 warnings:
- `@typescript-eslint/no-unused-vars` (line 4): `useMemo` imported but unused
- `@next/next/no-img-element` (lines 153, 162, 169, 261): `<img>` instead of `<Image />`

**`src/app/api/health/route.ts`** — 0 errors, 1 warning:
- `@typescript-eslint/no-unused-vars` (line 16): `error` defined but unused

### Worker file errors (pre-existing, out of scope)

**`public/workers/dxf-parser-worker.js`** — warnings only (`@typescript-eslint/no-unused-expressions`)

**`public/workers/libredwg-parser-worker.js`** — 3 errors (`@typescript-eslint/no-this-alias` at lines 6050, 6086, 6528) + many warnings

**`public/workers/mtext-renderer-worker.js`** — many warnings (`@typescript-eslint/no-unused-expressions`)

## Pre-existing Failing Identifiers

All errors and warnings above are pre-existing and not introduced by the click-to-reactivate-viewer change.
