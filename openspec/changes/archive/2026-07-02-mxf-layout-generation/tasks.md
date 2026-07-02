## 1. Pre-flight and Baselines

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `[.ralph/baselines/](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/)`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `[.ralph/baselines/mxf-layout-generation-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-test.txt)`, `[.ralph/baselines/mxf-layout-generation-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-typecheck.txt)`, `[.ralph/baselines/mxf-layout-generation-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-lint.txt)`, and `[.ralph/baselines/mxf-layout-generation-i18n.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-i18n.txt)` exist with full command outputs
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `[.ralph/baselines/mxf-layout-generation-readme.md](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-readme.md)` lists passing/failing gates, exit codes, and exact failing identifiers
    - `[ -f .ralph/baselines/mxf-layout-generation-test.txt ] && [ -f .ralph/baselines/mxf-layout-generation-typecheck.txt ] && [ -f .ralph/baselines/mxf-layout-generation-lint.txt ] && [ -f .ralph/baselines/mxf-layout-generation-i18n.txt ] && [ -f .ralph/baselines/mxf-layout-generation-readme.md ]` exits 0
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Shared Data Contract

- [x] **Freeze MXF layout generation data contract**
  - Scope: `[agent.py](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py)`, `[types.ts](file:///home/ncheaz/git/dkp-demo/src/lib/types.ts)`
  - Change: Add the optional `mxfContent` property to both the Python and TypeScript definitions of `DesignEntry`.
  - Done when:
    - `rg "mxfContent\?:" src/lib/types.ts` exits 0
    - `rg "mxfContent" agent/src/agent.py` exits 0
    - `DEEPSEEK_API_KEY=dummy-key-for-tests PYTHONPATH=agent/src:agent uv run --project agent python -c "from src.agent import DesignEntry; assert 'mxfContent' in DesignEntry.model_fields"` exits 0
    - `npx tsc --noEmit` exits 0, or failures match the baseline in `[.ralph/baselines/mxf-layout-generation-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-typecheck.txt)` with no new type-checking errors in `[types.ts](file:///home/ncheaz/git/dkp-demo/src/lib/types.ts)`
    - `uv run --project agent ruff check agent/src/agent.py` exits 0
  - Stop and hand off if: importing agent.py raises an unresolvable exception or type check errors occur in files not touched by this task.

## 3. Backend MXF Generator

- [x] **Create the MXF builder module**
  - Scope: `[mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py)` [NEW], `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)` [NEW]
  - Change: Implement a layout MXF builder that parses `[DesignParameters](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py#L170-L180)`, converts coordinates to meters, writes a valid XML structure representing the 4 building walls with inward-pointing thickness vectors, and write unit tests for coordinate calculations.
  - Done when:
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_mxf_generation_success` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_mxf_generation_invalid_dimensions` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py` exits 0
    - `uv run --project agent ruff check agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
  - Stop and hand off if: wall geometry solver does not form a closed rectangle or thickness axis math is mathematically ambiguous.

## 4. Backend API Integration

- [x] **Expose the REST API endpoint for MXF generation**
  - Scope: `[main.py](file:///home/ncheaz/git/dkp-demo/agent/src/main.py)`, `[test_mxf_endpoint.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_endpoint.py)` [NEW]
  - Change: Add a `/api/mxf/generate` POST route in `main.py` returning layout MXF bytes from a `DesignParameters` payload.
  - Done when:
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_endpoint.py -k test_mxf_endpoint` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_endpoint.py` exits 0
    - `uv run --project agent ruff check agent/src/main.py test/test_mxf_endpoint.py` exits 0
  - Stop and hand off if: route registration throws server initialization errors or response content headers conflict with Starlette spec.

## 5. Frontend Integration & Skill Updates

- [x] **Integrate frontend MXF download and update agent skill capabilities**
  - Scope: `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/page.tsx)`, `[design-component.tsx](file:///home/ncheaz/git/dkp-demo/src/components/design-component.tsx)`, `[en.json](file:///home/ncheaz/git/dkp-demo/src/i18n/messages/en.json)`, `[sk.json](file:///home/ncheaz/git/dkp-demo/src/i18n/messages/sk.json)`, `[SKILL.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/SKILL.md)`, `[mxf-builder-api.md](file:///home/ncheaz/git/dkp-demo/.agents/skills/run-generate-design/references/mxf-builder-api.md)` [NEW]
  - Change: Register client-side `generate_mxf` frontend tool in page layout (fetches from `/api/mxf/generate`, base64 encodes it, and stores in `mxfContent` in React state), add translation keys for MXF downloading, render `MxfDownloadButton` next to the IFC download button, and update agent skill runner guidelines and reference documentation to include MXF generation capability.
  - Done when:
    - `rg "<MxfDownloadButton" src/components/design-component.tsx` exits 0
    - `rg "generate_mxf" src/app/page.tsx` exits 0
    - `rg "generate_mxf" .agents/skills/run-generate-design/SKILL.md` exits 0
    - `[ -f .agents/skills/run-generate-design/references/mxf-builder-api.md ]` exits 0
    - `npm run i18n:check` exits 0
    - `npx tsc --noEmit` exits 0, or failures match the baseline in `[.ralph/baselines/mxf-layout-generation-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-typecheck.txt)` with no new errors in `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/page.tsx)` or `[design-component.tsx](file:///home/ncheaz/git/dkp-demo/src/components/design-component.tsx)`
    - `npm run lint` exits 0, or failures match the baseline in `[.ralph/baselines/mxf-layout-generation-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-lint.txt)` with no new errors in `[page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/page.tsx)` or `[design-component.tsx](file:///home/ncheaz/git/dkp-demo/src/components/design-component.tsx)`
  - Stop and hand off if: frontend state synchronization creates unhandled promise rejections, rendering crashes the DOM, or the skill directory `.agents/skills/` is unwritable.

## 6. Documentation

- [x] **Document future roadmaps**
  - Scope: `[TODO.md](file:///home/ncheaz/git/dkp-demo/hidden/TODO.md)`, `[MXF_GENERATION_SUMMARY.md](file:///home/ncheaz/git/dkp-demo/docs/MXF_GENERATION_SUMMARY.md)` [NEW]
  - Change: Append roadmap notes on roof and floor surfaces in `[TODO.md](file:///home/ncheaz/git/dkp-demo/hidden/TODO.md)` and create a summary documentation file under the `docs/` directory.
  - Done when:
    - `[ -f docs/MXF_GENERATION_SUMMARY.md ]` exits 0
    - `rg "MXF surface generation" hidden/TODO.md` exits 0
  - Stop and hand off if: the `docs/` directory is unwritable.

## 7. Wall Plate and Testing Suite Bug Fixes

- [x] **Generate WallPlateList under Wall elements in MXF layout XML**
  - Scope: `[mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py)`, `[test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py)`
  - Change: The generated MXF layout XML contains a `<WallPlateList>` containing a `<WallPlate offset="0.05" height="0.05" width="0.1" />` element under every `<Wall>`, and the test suite asserts this structure.
  - Done when:
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_mxf_builder.py -k test_wall_plate_list` exits 0
    - `uv run --project agent ruff check agent/src/mxf_builder.py test/test_mxf_builder.py` exits 0
  - Stop and hand off if: the wall plate parameters (offset, width, height) are dynamically configured elsewhere and contradict standard defaults, or the XML parsing library fails to navigate the updated structure.

## 8. Quality Gates Verification

- [x] **Verify final integrated quality gates**
  - Scope: no code edits; project-wide quality gates
  - Change: Confirm no typecheck, lint, or test regressions have been introduced across the entire repository.
  - Done when:
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest` exits 0, or failures match the baseline in `[.ralph/baselines/mxf-layout-generation-test.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-test.txt)` with no new failures.
    - `npx tsc --noEmit` exits 0, or failures match the baseline in `[.ralph/baselines/mxf-layout-generation-typecheck.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-typecheck.txt)` with no new failures.
    - `uv run --project agent ruff check agent/src` exits 0
    - `npm run lint` exits 0, or failures match the baseline in `[.ralph/baselines/mxf-layout-generation-lint.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-lint.txt)` with no new failures.
    - `npm run i18n:check` exits 0, or failures match the baseline in `[.ralph/baselines/mxf-layout-generation-i18n.txt](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/mxf-layout-generation-i18n.txt)` with no new failures.
  - Stop and hand off if: any regression is found in files untouched by this change.


