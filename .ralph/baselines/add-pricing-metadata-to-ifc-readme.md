# add-pricing-metadata-to-ifc Pre-flight Baselines

Captured at the start of the `add-pricing-metadata-to-ifc` change to establish
the "no new failures" reference for every downstream task. This change touches
Python code only (`agent/src/ifc_builder.py` + `test/test_ifc_builder.py`), so
the gates below are the only ones later tasks require.

## Gates

| Gate | Command | File | Result | Details |
|------|---------|------|--------|---------|
| pytest | `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` | `add-pricing-metadata-to-ifc-pytest.txt` | PASS (exit 0) | 27 passed in 0.68s |
| mypy | `uv run --project agent mypy agent/src/` | `add-pricing-metadata-to-ifc-mypy.txt` | FAIL (exit 1) | 1 error in 1 file (checked 6 source files) |

## Failing Gates

### mypy (exit 1) — 1 error

- `agent/src/dxf_builder.py:99: error: Incompatible types in assignment (expression has type "tuple[int, float, float]", variable has type "tuple[float, int, float]")  [assignment]`

This is a pre-existing type error in `dxf_builder.py`, which is outside this
change's scope (this change edits `ifc_builder.py`). It is identical in kind to
the one recorded by the earlier `generate-ifc-export` baseline (then reported at
line 89; the line number shifted due to unrelated edits).

## Notes

- pytest baseline = 27 passed, exit 0 (clean). Downstream tasks that assert a
  specific passing-test count should compare against this 27-test baseline.
- The two implementation tasks classify this as the authoritative reference:
  later `mypy` gates pass when "failures match the pre-flight baseline with no
  new failures in this task's scope" — i.e. the single `dxf_builder.py:99` error
  above and nothing in `ifc_builder.py`.
- Subsequent tasks must introduce no NEW failures beyond this baseline.
