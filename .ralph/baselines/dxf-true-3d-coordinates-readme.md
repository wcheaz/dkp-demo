# dxf-true-3d-coordinates Pre-flight Baselines

## Gates

| Gate | File | Result | Details |
|------|------|--------|---------|
| pytest: test/test_dxf_builder.py + test/test_dxf_endpoint.py | `dxf-true-3d-coordinates-test.txt` | PASS (exit 0) | 65 passed, 3 skipped, 0 failed |

## Failing Gates

None.

## Notes

- 3 skipped tests are in `TestTitleBlock` (title block generation is disabled in dxf_builder.py, unrelated to this change).
- All other tests pass with the current isometric projection (`_to_iso`) implementation.
EXIT=0
