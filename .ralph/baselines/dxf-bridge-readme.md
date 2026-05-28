# DXF Bridge Test Gate Baselines

Captured on: 2026-05-28

## Gates

| Test File | Exit Code | Test Count |
|-----------|-----------|------------|
| `test/test_dxf_builder.py` | 0 | 48 passed |
| `test/test_generate_dxf.py` | 0 | 8 passed |
| `test/test_dxf_endpoint.py` | 0 | 9 passed |
| **Combined** | **0** | **65 passed, 2 warnings** |

## Notes

- Tests require `DEEPSEEK_API_KEY` and `OPENAI_BASE_URL` environment variables from `.env`
- Run command: `cd agent && source .venv/bin/activate && set -a && source ../.env && python3 -m pytest ../test/test_dxf_builder.py ../test/test_generate_dxf.py ../test/test_dxf_endpoint.py -q`
- Unit tests (48) cover all roof types, layers, entity counts, coordinates, and DXF round-trip re-readability
- Agent tool tests (8) cover the `generate_dxf` backend tool
- Endpoint tests (9) cover the `/api/dxf/generate` HTTP endpoint
- All gates green (exit code 0)
