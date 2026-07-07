# gable-roof-generation-fixes Pre-flight Baselines

Captured at the start of the `gable-roof-generation-fixes` change to establish
the "no new failures" reference for every downstream task. This change is
Python-only (scope: `agent/src/geometry_solver.py`, `agent/src/ifc_builder.py`,
`agent/src/mxf_builder.py`, `agent/src/dxf_builder.py`, `agent/src/main.py`,
plus tests under `test/`), so the captured gates are the three Python quality
gates that the later task `Done when` bullets invoke:

- `uv run --project agent ruff check agent/src` (broad; final gate)
- `uv run --project agent mypy agent/src` (broad; final gate)
- `PYTHONPATH=agent/src:agent uv run --project agent pytest` (broad; final gate)

The narrow per-task `ruff` / `mypy` invocations on individual files
(e.g. `agent/src/mxf_builder.py`) are subsets of these broad gates and inherit
the same baseline state (all clean at HEAD).

Every gate was executed **twice** and confirmed deterministic before recording
these files: identical exit codes, identical error identifiers (none — all
gates PASS), and identical pass/skip/warning counts (pytest) across both runs.
The only run-over-run variation was sub-second timing in the pytest summary
line (`3.19s` vs `3.21s` vs `3.25s`).

## Gates

| Gate | Command | File | Result | Details |
|------|---------|------|--------|---------|
| lint (ruff) | `uv run --project agent ruff check agent/src` | `gable-roof-generation-fixes-lint.txt` | PASS (exit 0) | `All checks passed!` |
| typecheck (mypy) | `uv run --project agent mypy agent/src` | `gable-roof-generation-fixes-typecheck.txt` | PASS (exit 0) | `Success: no issues found in 7 source files` |
| pytest | `PYTHONPATH=agent/src:agent uv run --project agent pytest` | `gable-roof-generation-fixes-test.txt` | PASS (exit 0) | 208 passed, 3 skipped, 9 warnings |

## Failing Gates

None. All three gates pass cleanly at HEAD, so every downstream `Done when`
bullet — including the strict narrow-gate forms like
`uv run --project agent mypy agent/src/mxf_builder.py ... exits 0` — must hold
**strict clean** at task completion. There is no pre-existing baseline failure
that the implementation work is authorized to defer.

## Passing Gates

- **ruff (exit 0):** `All checks passed!` on `agent/src` (7 source files).
- **mypy (exit 0):** `Success: no issues found in 7 source files`. This
  supersedes the older `mxf-roof-surfaces` baseline, which recorded 5 pre-
  existing type errors in `agent/src/mxf_builder.py` and `agent/src/dxf_builder.py`.
  Those errors have since been resolved at HEAD (likely by the intervening
  `mxf-roof-surfaces` implementation work), so all narrow mypy gates in this
  change's tasks must pass cleanly.
- **pytest (exit 0):** 208 passed, 3 skipped, 9 warnings. The 3 skipped tests
  relate to title-block generation disabled in `dxf_builder.py` (same as in
  prior baselines) and are unrelated to this change. The 9 warnings come from
  `ezdxf` / `pydantic-ai` deprecations
  (`PyparsingDeprecationWarning`, `OpenAIModel` rename, `Agent.to_ag_ui()`
  deprecation) and are unrelated to this change. The 208-passed count
  supersedes the older `mxf-roof-surfaces` baseline (172 passed); the
  additional 36 tests were added by intervening changes and all pass.

  Per-file distribution (from the captured log):
  - `test/test_dxf_builder.py` — 55 of 58 run (3 skipped)
  - `test/test_dxf_endpoint.py` — 9 passed
  - `test/test_ifc_builder.py` — 39 passed
  - `test/test_ifc_endpoint.py` — 8 passed
  - `test/test_mxf_builder.py` — 48 passed
  - `test/test_mxf_endpoint.py` — 14 passed
  - `test/test_pricing.py` — 11 passed
  - `test/test_reset_design.py` — 22 passed

## Notes

- Subsequent tasks must introduce no NEW failures beyond this baseline. When a
  gate is described as "failures match the pre-flight baseline with no new
  failures", the baseline is **zero failures** for all three gates, so any
  new failure is by definition a regression.
- Because all gates are clean at HEAD, the narrow per-task gates
  (e.g. `mypy agent/src/geometry_solver.py agent/src/mxf_builder.py ... exits 0`)
  inherit the same clean baseline and must pass strictly; there are no
  pre-existing errors in any in-scope file for downstream tasks to defer.
- Baseline files all end with a literal `EXIT=<integer>` footer line:
  - `gable-roof-generation-fixes-lint.txt` → `EXIT=0`
  - `gable-roof-generation-fixes-typecheck.txt` → `EXIT=0`
  - `gable-roof-generation-fixes-test.txt` → `EXIT=0`
