# mxf-layout-generation Pre-flight Baselines

Captured at the start of the `mxf-layout-generation` change to establish the
"no new failures" reference for every downstream task. Every gate was executed
twice and confirmed deterministic (identical exit codes and summary counts
across both runs) before recording these files.

## Gates

| Gate | Command | File | Result | Details |
|------|---------|------|--------|---------|
| pytest: test/ | `PYTHONPATH=agent/src:agent uv run --project agent pytest test/` | `mxf-layout-generation-test.txt` | PASS (exit 0) | 145 passed, 3 skipped, 9 warnings |
| typecheck | `npx tsc --noEmit` | `mxf-layout-generation-typecheck.txt` | PASS (exit 0) | No diagnostics emitted (only an npm `allow-scripts` warning about an unparseable `.npmrc` entry) |
| lint | `npm run lint` | `mxf-layout-generation-lint.txt` | FAIL (exit 1) | 1852 problems (44 errors, 1808 warnings) |
| i18n | `npm run i18n:check` | `mxf-layout-generation-i18n.txt` | PASS (exit 0) | `i18n parity OK: 89 keys verified.` |

## Failing Gates

### lint (exit 1) — 44 errors

All 44 errors are pre-existing and outside this change's scope. Breakdown by
file/rule (35 standard single-line ESLint errors + 9 React-Compiler multi-line
errors):

**Vendored / build artefacts (pre-existing, out of scope):**

- `public/workers/mtext-renderer-worker.js` — 18 × `@typescript-eslint/no-this-alias` + 1 × `@typescript-eslint/no-require-imports` = 19 errors
- `public/workers/libredwg-parser-worker.js` — 3 × `@typescript-eslint/no-this-alias`
- `public/workers/dxf-parser-worker.js` — 1 × `@typescript-eslint/no-this-alias`
- `scripts/patch-three-dxf-loader.js` — 2 × `@typescript-eslint/no-require-imports` (lines 1, 2)
- `scripts/test-ifc-parser.js` — 4 × `@typescript-eslint/no-require-imports`
- `tmp_build/page.js` — 3 × `@typescript-eslint/no-require-imports` (build artefact)

**Source files (pre-existing, in files that this change may touch):**

- `src/app/page.tsx` — 7 × React-Compiler "This value cannot be modified" (lines 376, 471, 546, 599, 711, 817, 916 — `latestStateRef` mutations inside effect/callback)
- `src/components/cad-viewer-3d.tsx` — 3 × `@typescript-eslint/no-explicit-any` (lines 212, 241, 274) + 1 × React-Compiler "Cannot access variable before it is declared" (line 269, `fitCamera`)
- `src/components/design-component.tsx` — 1 × React-Compiler "Calling setState synchronously within an effect can trigger cascading renders" (line 136, `setActiveViewerIndex`)

The 1808 warnings are dominated by minified vendored worker bundles under
`public/workers/` (`@typescript-eslint/no-unused-expressions`) and Next.js
`@next/next/no-img-element` / `react-hooks/exhaustive-deps` notices.

## Passing Gates

- **pytest (exit 0):** 145 passed, 3 skipped, 9 warnings. The 3 skipped tests
  relate to title-block generation disabled in `dxf_builder.py`; unrelated to
  this change. The 9 warnings come from `ezdxf` / `pydantic-ai` deprecations
  (`PyparsingDeprecationWarning`, `OpenAIModel` rename, `Agent.to_ag_ui()`
  deprecation); unrelated to this change.
- **typecheck (exit 0):** `npx tsc --noEmit` produced no diagnostics.
- **i18n (exit 0):** `npm run i18n:check` reported parity OK across 89 keys
  between `src/i18n/messages/en.json` and `src/i18n/messages/sk.json`.

## Notes

- The React-Compiler (`react-compiler/*`) and `react-hooks/immutability` rules
  firing in `src/app/page.tsx`, `src/components/cad-viewer-3d.tsx`, and
  `src/components/design-component.tsx` are emitted by a stricter React
  Compiler ESLint config and are pre-existing. Task 5 ("Frontend Integration &
  Skill Updates") is permitted to touch these files; the "no new failures"
  comparison for that task compares against the identifiers listed above.
- Subsequent tasks must introduce no NEW failures beyond this baseline. When a
  gate is described as "failures match the pre-flight baseline with no new
  failures", compare against the identifiers in this README and the full
  command output in the corresponding `.txt` file.
