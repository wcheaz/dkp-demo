# pamir-ifc-pricing-bridge Pre-flight Baselines

Captured at the start of the `pamir-ifc-pricing-bridge` change to establish the
"no new failures" reference for every downstream task.

## Gates

| Gate | Command | File | Result | Details |
|------|---------|------|--------|---------|
| pytest: test/ | `PYTHONPATH=agent/src:agent uv run --project agent pytest test/ -v` | `pamir-ifc-pricing-bridge-test.txt` | PASS (exit 0) | 123 passed, 3 skipped, 9 warnings |
| typecheck | `npx tsc --noEmit` | `pamir-ifc-pricing-bridge-typecheck.txt` | PASS (exit 0) | No diagnostics emitted |
| lint | `npm run lint` | `pamir-ifc-pricing-bridge-lint.txt` | FAIL (exit 1) | 1852 problems (44 errors, 1808 warnings) |

## Failing Gates

### lint (exit 1) — 44 errors

All errors are pre-existing and outside this change's scope. Breakdown by file/rule:

- `public/workers/mtext-renderer-worker.js` — `@typescript-eslint/no-this-alias` ×18, `@typescript-eslint/no-require-imports` ×1
- `public/workers/libredwg-parser-worker.js` — `@typescript-eslint/no-this-alias` ×3
- `public/workers/dxf-parser-worker.js` — `@typescript-eslint/no-this-alias` ×1
- `scripts/patch-three-dxf-loader.js` — `@typescript-eslint/no-require-imports` ×2 (lines 1, 2)
- `scripts/test-ifc-parser.js` — `@typescript-eslint/no-require-imports` ×4 (lines 1, 2, 3, 51)
- `src/app/page.tsx` — `react-hooks/immutability` ×7 (lines 376, 471, 546, 599, 711, 817, 916 — "This value cannot be modified", `latestStateRef`)
- `src/components/cad-viewer-3d.tsx` — `@typescript-eslint/no-explicit-any` ×3 (lines 212, 241, 274); `react-hooks/immutability` ×1 (line 269 — "Cannot access variable before it is declared", `fitCamera`)
- `src/components/design-component.tsx` — `react-hooks/set-state-in-effect` ×1 (line 136 — `setActiveViewerIndex` in effect)
- `tmp_build/page.js` — `@typescript-eslint/no-require-imports` ×3 (lines 5, 6, 7) — generated build artifact

The 1808 warnings are dominated by minified vendored worker bundles under
`public/workers/` (`@typescript-eslint/no-unused-expressions`) and Next.js
`@next/next/no-img-element` / `react-hooks/exhaustive-deps` notices.

## Notes

- pytest: 3 skipped tests relate to disabled title block generation in `dxf_builder.py`; unrelated to this change.
- pytest: 9 pre-existing warnings come from `ezdxf` / `pyparsing` / `pydantic-ai` deprecations; unrelated to this change.
- The `react-hooks/immutability` and `react-hooks/set-state-in-effect` rules in `page.tsx` / `cad-viewer-3d.tsx` / `design-component.tsx` are emitted by a stricter React Compiler ESLint config and are pre-existing.
- `scripts/test-ifc-parser.js` (4 pre-existing `require()` errors) is in scope for change §2, so the §2 done-conditions compare against these 4 identifiers. Net change must not introduce NEW lint errors beyond this set.
- Subsequent tasks must introduce no NEW failures beyond this baseline. When a gate is "failures match the pre-flight baseline with no new failures", compare against the identifiers above.
