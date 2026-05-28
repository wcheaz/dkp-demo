# DXF Phase 5 Test Gate Baselines

Captured on: 2026-05-28

## Gates

| Gate | Baseline File | Exit Code | Test Count |
|------|--------------|-----------|------------|
| DXF Builder Unit Tests | `dxf-phase5-test.txt` | 0 | 48 passed |
| DXF Integration Tests | `dxf-phase5-integration.txt` | 0 | 17 passed, 2 warnings |

## Notes

- Integration tests require `DEEPSEEK_API_KEY` and `OPENAI_BASE_URL` environment variables from `.env`
- Unit tests (48) cover all roof types, layers, entity counts, coordinates, and DXF round-trip re-readability
- Integration tests (17) cover the `generate_dxf` agent tool and `/api/dxf/generate` HTTP endpoint
- Both gates are green (exit code 0)
