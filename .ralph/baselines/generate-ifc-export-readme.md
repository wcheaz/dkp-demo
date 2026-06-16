# generate-ifc-export Pre-flight Baselines

Captured at the start of the `generate-ifc-export` change to establish the
"no new failures" reference for every downstream task.

## Gates

| Gate | Command | File | Result | Details |
|------|---------|------|--------|---------|
| pytest: test/ | `PYTHONPATH=agent/src:agent uv run --project agent pytest test/` | `generate-ifc-export-test.txt` | PASS (exit 0) | 87 passed, 3 skipped, 9 warnings |
| typecheck | `npx tsc --noEmit` | `generate-ifc-export-typecheck.txt` | PASS (exit 0) | No diagnostics emitted |
| lint | `npm run lint` | `generate-ifc-export-lint.txt` | FAIL (exit 1) | 1840 problems (36 errors, 1804 warnings) |
| mypy | `uv run --project agent mypy agent/src/` | `generate-ifc-export-mypy.txt` | FAIL (exit 1) | 1 error in 1 file (checked 4 source files) |

## Failing Gates

### lint (exit 1) — 36 errors

All errors are pre-existing and outside this change's scope. Breakdown by file/rule:

- `public/workers/dxf-parser-worker.js` — `@typescript-eslint/no-this-alias` ×1
- `public/workers/libredwg-parser-worker.js` — `@typescript-eslint/no-this-alias` ×3
- `public/workers/mtext-renderer-worker.js` — `@typescript-eslint/no-this-alias` ×18, `@typescript-eslint/no-require-imports` ×1
- `scripts/patch-three-dxf-loader.js` — `@typescript-eslint/no-require-imports` ×2 (lines 1, 2)
- `src/app/page.tsx` — `react-hooks/immutability` ×6 (lines 375, 470, 545, 598, 710, 815 — "This value cannot be modified", `latestStateRef`)
- `src/components/cad-viewer-3d.tsx` — `@typescript-eslint/no-explicit-any` ×3 (lines 212, 241, 274); `react-hooks/immutability` ×1 (line 269 — "Cannot access variable before it is declared", `fitCamera`)
- `src/components/design-component.tsx` — `react-hooks/set-state-in-effect` ×1 (line 102 — `setActiveViewerIndex` in effect)

The 1804 warnings are dominated by minified vendored worker bundles under
`public/workers/` (`@typescript-eslint/no-unused-expressions`) and Next.js
`@next/next/no-img-element` / `react-hooks/exhaustive-deps` notices.

### mypy (exit 1) — 1 error

- `agent/src/dxf_builder.py:89: error: Incompatible types in assignment (expression has type "tuple[int, float, float]", variable has type "tuple[float, int, float]")  [assignment]`

## Notes

- pytest: 3 skipped tests relate to title block generation disabled in `dxf_builder.py`; unrelated to this change.
- pytest: 9 pre-existing warnings come from `ezdxf` / `pydantic-ai` deprecations; unrelated to this change.
- The `react-hooks/immutability` and `react-hooks/set-state-in-effect` rules in `page.tsx` / `cad-viewer-3d.tsx` / `design-component.tsx` are emitted by a stricter React Compiler ESLint config and are pre-existing.
- Subsequent tasks must introduce no NEW failures beyond this baseline. When a gate is "failures match the pre-flight baseline with no new failures", compare against the identifiers above.
