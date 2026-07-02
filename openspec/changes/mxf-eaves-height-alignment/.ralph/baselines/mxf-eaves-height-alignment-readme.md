# Pre-flight Baselines — mxf-eaves-height-alignment

Captured at task `Pre-flight: record quality gate baselines` for change `mxf-eaves-height-alignment`.
All gates captured from repo root `/home/ncheaz/git/dkp-demo` using the `agent` uv project.
No code edits were made; artifacts written only under `.ralph/baselines/`.

## Gates

| Gate       | Command                                                            | Exit code | Status | Failing identifiers |
|------------|--------------------------------------------------------------------|-----------|--------|---------------------|
| test       | `PYTHONPATH=agent/src:agent uv run --project agent pytest`         | 0         | PASS   | none                |
| typecheck  | `uv run --project agent mypy agent/src`                            | 0         | PASS   | none                |
| lint       | `uv run --project agent ruff check agent/src`                      | 0         | PASS   | none                |

## Artifacts

- `mxf-eaves-height-alignment-test.txt` — pytest: 207 passed, 3 skipped, 9 warnings. Ends with `EXIT=0`.
- `mxf-eaves-height-alignment-typecheck.txt` — mypy: `Success: no issues found in 7 source files`. Ends with `EXIT=0`.
- `mxf-eaves-height-alignment-lint.txt` — ruff: `All checks passed!`. Ends with `EXIT=0`.

## Notes

- All three gates are clean (exit 0) at baseline. Later tasks may treat these as required-clean gates; any regression after this change is introduced by that task, not pre-existing.
- The 3 skipped tests are pre-existing skips (deprecation/optional paths), not failures.
- `PYTHONPATH=agent/src:agent` is required for the pytest gate so test modules resolve `agent.src.*` imports.
