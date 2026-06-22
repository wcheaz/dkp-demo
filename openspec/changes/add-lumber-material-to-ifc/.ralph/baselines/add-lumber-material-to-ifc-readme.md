# Quality Gate Baselines

This document lists the baseline status of quality gates for the `add-lumber-material-to-ifc` change.

## Baseline Summary

| Gate | Command | Exit Code | Status | Exact Failing Identifiers |
|---|---|---|---|---|
| pytest | `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` | 0 | PASSING | none |
| mypy | `uv run --project agent mypy agent/src/` | 1 | FAILING (pre-existing, out of scope) | `agent/src/dxf_builder.py:99` |

## Notes

- The `pytest` gate passes cleanly with all 26 tests collected and passing, captured in `add-lumber-material-to-ifc-pytest.txt`.
- The `mypy` gate fails with a single pre-existing error that is OUT OF SCOPE for this change:
  - `agent/src/dxf_builder.py:99: error: Incompatible types in assignment (expression has type "tuple[int, float, float]", variable has type "tuple[float, int, float]")  [assignment]`
  - This failure lives in `dxf_builder.py`, not in `ifc_builder.py` (the in-scope source file for this change). It must be tolerated by later tasks as a matching-baseline failure.
- Both gates were verified deterministic across two consecutive runs (identical exit codes, identical failing identifiers, and identical pass counts on both runs).
- Full raw output for each gate is preserved in the corresponding `.txt` file, each ending with a literal `EXIT=<integer>` final line.
