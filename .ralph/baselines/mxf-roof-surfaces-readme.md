# mxf-roof-surfaces Pre-flight Baselines

Captured at the start of the `mxf-roof-surfaces` change to establish the
"no new failures" reference for every downstream task. This change is
Python-only (scope: `agent/src/mxf_builder.py`, `agent/src/geometry_solver.py`,
`agent/src/main.py`, plus tests under `test/`), so the captured gates are the
three Python quality gates that the later task `Done when` bullets invoke.

Every gate was executed **twice** and confirmed deterministic before recording
these files: identical exit codes, identical error identifiers (mypy), and
identical pass/skip/warning counts (pytest) across both runs. (The only
run-over-run variation was sub-second timing in the pytest summary line.)

## Gates

| Gate | Command | File | Result | Details |
|------|---------|------|--------|---------|
| lint (ruff) | `uv run --project agent ruff check agent/src` | `mxf-roof-surfaces-lint.txt` | PASS (exit 0) | `All checks passed!` |
| typecheck (mypy) | `uv run --project agent mypy agent/src` | `mxf-roof-surfaces-typecheck.txt` | FAIL (exit 1) | 5 errors in 2 files (see below) |
| pytest | `PYTHONPATH=agent/src:agent uv run --project agent pytest` | `mxf-roof-surfaces-test.txt` | PASS (exit 0) | 172 passed, 3 skipped, 9 warnings |

## Failing Gates

### typecheck — mypy (exit 1) — 5 errors

`Found 5 errors in 2 files (checked 7 source files)`. All five are **pre-existing
type-narrowing issues** in files this change will edit; exact identifiers:

**`agent/src/mxf_builder.py`** (4 errors) — root cause: the `definitions` list
of `dict[str, Any]` is iterated and unpacked into `object`-typed scalars, so
arithmetic and reassignment on those unpacked values fail:

- `mxf_builder.py:82` — `error: Unsupported left operand type for + ("object")  [operator]` (`spec["x_axis"] = (ox + rx, ...)`)
- `mxf_builder.py:83` — `error: Unsupported operand types for + ("object" and "float")  [operator]` (`spec["y_axis"] = (ox, oy, oz + 1.0)`)
- `mxf_builder.py:84` — `error: Unsupported left operand type for + ("object")  [operator]` (`spec["z_axis"] = (ox + ix, ...)`)
- `mxf_builder.py:86` — `error: Incompatible types in assignment (expression has type "float", target has type "Sequence[object]")  [assignment]` (`spec["length"] = width_m if index in (0, 2) else depth_m`)

**`agent/src/dxf_builder.py`** (1 error) — pre-existing ridge-coordinate tuple
type narrowing in the gable outline branch:

- `dxf_builder.py:99` — `error: Incompatible types in assignment (expression has type "tuple[int, float, float]", variable has type "tuple[float, int, float]")  [assignment]` (`ridge_start = (0, mid_y, z_ridge)`)

> **Note for downstream tasks.** Several implementation tasks carry *strict*
> narrow mypy `Done when` bullets of the form
> `uv run --project agent mypy agent/src/mxf_builder.py agent/src/geometry_solver.py`
> `exits 0`. Because the four `mxf_builder.py` errors above are pre-existing in
> an in-scope file, those narrow gates cannot pass until the implementing task
> resolves them. The errors are localized type annotations (annotate the dict
> tuple fields / the ridge variable) and do not require behavioural changes.
> `dxf_builder.py:99` is the only pre-existing failure outside the strict mypy
> scope of the implementation tasks (it is covered only by the broad
> `mypy agent/src` gate), so it is recorded here for completeness and should be
> preserved unless a task explicitly fixes it.

## Passing Gates

- **ruff (exit 0):** `All checks passed!` on `agent/src`.
- **pytest (exit 0):** 172 passed, 3 skipped, 9 warnings. The 3 skipped tests
  relate to title-block generation disabled in `dxf_builder.py` (same as the
  `mxf-layout-generation` baseline) and are unrelated to this change. The 9
  warnings come from `ezdxf` / `pydantic-ai` deprecations
  (`PyparsingDeprecationWarning`, `OpenAIModel` rename, `Agent.to_ag_ui()`
  deprecation) and are unrelated to this change.

## Notes

- Subsequent tasks must introduce no NEW failures beyond this baseline. When a
  gate is described as "failures match the pre-flight baseline with no new
  failures", compare against the identifiers in this README and the full
  command output in the corresponding `.txt` file.
- The `test/` pytest baseline (172 passed) supersedes the older
  `mxf-layout-generation` baseline (145 passed); the additional 27 tests were
  added by intervening changes and all pass.
