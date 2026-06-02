# cad-test-viewer — Quality Gate Baselines

## Gates

| Gate | Status | Exit Code | Notes |
|------|--------|-----------|-------|
| `pytest test/test_dxf_builder.py` | FAIL | 1 | 12 failed, 36 passed |
| `npx eslint .` | FAIL | 1 | 1831 problems (29 errors, 1802 warnings) |

## Failing Gate Details — pytest

### Failing test identifiers (12 total)

- `TestTitleBlock::test_rectangle_lines`
- `TestTitleBlock::test_mtext_content_populated`
- `TestTitleBlock::test_none_fields_use_defaults`
- `TestRoundTripAllRoofTypes::test_all_five_layers_present[Gable]`
- `TestRoundTripAllRoofTypes::test_all_five_layers_present[Hip]`
- `TestRoundTripAllRoofTypes::test_all_five_layers_present[Mono-pitch]`
- `TestRoundTripAllRoofTypes::test_all_five_layers_present[Flat]`
- `TestGenerateExampleFiles::test_write_example_dxf[gable]`
- `TestGenerateExampleFiles::test_write_example_dxf[hip]`
- `TestGenerateExampleFiles::test_write_example_dxf[mono-pitch]`
- `TestGenerateExampleFiles::test_write_example_dxf[flat]`
- `TestGenerateExampleFiles::test_write_example_dxf[decimal]`

### Root cause

All 12 failures stem from `Title_Block` layer not being created by `build_dxf()`. The round-trip and example-file tests expect `_ALL_FIVE_LAYERS` (including `Title_Block`) to be present. The title-block tests expect LINE and MTEXT entities on the `Title_Block` layer.

## Failing Gate Details — eslint

### Source file errors (non-worker)

**`src/app/page.tsx`** — 6 errors:
- `react-hooks/immutability` (lines 375, 470, 545, 598, 710, 815): `latestStateRef.current` cannot be modified inside effect/callback

**`src/app/page.tsx`** — 2 warnings:
- `react-hooks/exhaustive-deps` (lines 353, 410): missing dep `setState`

**`src/components/cad-viewer.tsx`** — 1 warning:
- `react-hooks/exhaustive-deps` (line 86): missing dep `dxfContent`

**`src/components/design-component.tsx`** — 3 warnings:
- `@next/next/no-img-element` (lines 166, 173, 265): `<img>` instead of `<Image />`

**`src/app/api/health/route.ts`** — 1 warning:
- `@typescript-eslint/no-unused-vars` (line 16): `error` defined but unused

### Worker file errors (pre-existing, out of scope)

**`public/workers/dxf-parser-worker.js`** — warnings only (`@typescript-eslint/no-unused-expressions`)
**`public/workers/libredwg-parser-worker.js`** — errors (`@typescript-eslint/no-this-alias`) + many warnings
**`public/workers/mtext-renderer-worker.js`** — warnings only (`@typescript-eslint/no-unused-expressions`)

## Pre-existing Failing Identifiers

All errors and warnings above are pre-existing and not introduced by the cad-test-viewer change.
