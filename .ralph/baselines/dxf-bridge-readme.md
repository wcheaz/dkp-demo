# DXF Bridge Test Gate Baselines

Captured on: 2026-05-28

## Gates

| Test File | Exit Code | Test Count |
|-----------|-----------|------------|
| `test/test_dxf_builder.py` | 0 | 48 passed |
| `test/test_generate_dxf.py` | N/A | removed in iteration 9 (commit 34eebc3) |
| `test/test_dxf_endpoint.py` | 0 | 8 passed |
| **Combined** | **0** | **56 passed, 2 warnings** |

## Notes

- `test/test_generate_dxf.py` was removed by prior work (iteration 9) before this baseline was captured
- Run command: `python3 -m pytest test/test_dxf_builder.py test/test_dxf_endpoint.py -q`
- Unit tests (48) cover all roof types, layers, entity counts, coordinates, and DXF round-trip re-readability
- Endpoint tests (8) cover the `/api/dxf/generate` HTTP endpoint
- All gates green (exit code 0)
