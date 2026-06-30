## 1. Pre-flight and Baselines

- [ ] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/mxf-layout-generation-test.txt`, `.ralph/baselines/mxf-layout-generation-typecheck.txt`, and `.ralph/baselines/mxf-layout-generation-lint.txt` exist with full command outputs
    - every captured gate file ends with a literal `EXIT=<integer>` line
    - `.ralph/baselines/mxf-layout-generation-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
    - `[ -f .ralph/baselines/mxf-layout-generation-test.txt ] && [ -f .ralph/baselines/mxf-layout-generation-typecheck.txt ] && [ -f .ralph/baselines/mxf-layout-generation-lint.txt ] && [ -f .ralph/baselines/mxf-layout-generation-readme.md ]` exits 0
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Backend MXF Generator

- [ ] **Create the MXF builder module**
  - Scope: [mxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py) [NEW], [test_mxf_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_builder.py) [NEW]
  - Change: Implement a layout MXF builder that parses [DesignParameters](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py#L170-L180), converts coordinates to meters, writes a valid XML structure representing the 4 building walls with inward-pointing thickness vectors, and write unit tests for coordinate calculations.
  - Done when:
    - `pytest test/test_mxf_builder.py` exits 0
    - The output XML contains a valid `<BuildingWallList>` and `<WallList>` matching the building perimeter, where wall thickness points inward
  - Stop and hand off if: wall geometry solver does not form a closed rectangle or thickness axis math is mathematically ambiguous.

## 3. Backend API Integration

- [ ] **Expose the generate_mxf agent tool and REST API endpoint**
  - Scope: [agent.py](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py), [main.py](file:///home/ncheaz/git/dkp-demo/agent/src/main.py), [test_mxf_endpoint.py](file:///home/ncheaz/git/dkp-demo/test/test_mxf_endpoint.py) [NEW]
  - Change: Add `mxfContent` property to [DesignEntry](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py#L183-L192), register the `generate_mxf` tool in the Pydantic AI agent, and add a `/api/mxf/generate` POST route returning layout MXF bytes.
  - Done when:
    - `pytest test/test_mxf_endpoint.py` exits 0
    - `pytest test/` exits 0, or failures match the baseline in `.ralph/baselines/mxf-layout-generation-test.txt` with no new failures in backend modules
  - Stop and hand off if: tool signature conflicts with CopilotKit agent wrapper or route registration throws server initialization errors.

## 4. Frontend Download Integration

- [ ] **Add the frontend MXF download button and types**
  - Scope: [types.ts](file:///home/ncheaz/git/dkp-demo/src/lib/types.ts), [page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/page.tsx), [design-component.tsx](file:///home/ncheaz/git/dkp-demo/src/components/design-component.tsx)
  - Change: Add `mxfContent` to type definitions, register client-side `generate_mxf` frontend tool in page layout, and render `MxfDownloadButton` next to the IFC download button.
  - Done when:
    - `npx tsc --noEmit` exits 0, or failures match the baseline in `.ralph/baselines/mxf-layout-generation-typecheck.txt` with no new failures in touched files
    - `npm run lint` exits 0, or failures match the baseline in `.ralph/baselines/mxf-layout-generation-lint.txt` with no new errors in touched files
  - Stop and hand off if: frontend state synchronization creates unhandled promise rejections or rendering crashes the DOM.

## 5. Documentation Update

- [ ] **Document future roadmaps and verify quality gates**
  - Scope: [TODO.md](file:///home/ncheaz/git/dkp-demo/hidden/TODO.md), [MXF_GENERATION_SUMMARY.md](file:///home/ncheaz/git/dkp-demo/ralph-docs/MXF_GENERATION_SUMMARY.md) [NEW]
  - Change: Append roadmap notes on roof and floor surfaces in [TODO.md](file:///home/ncheaz/git/dkp-demo/hidden/TODO.md) and create a summary documentation file under the `ralph-docs/` directory.
  - Done when:
    - `[ -f ralph-docs/MXF_GENERATION_SUMMARY.md ]` exits 0
    - `rg "MXF surface generation" hidden/TODO.md` returns at least one match
    - `pytest` exits 0, or failures match the baseline in `.ralph/baselines/mxf-layout-generation-test.txt`
  - Stop and hand off if: the `ralph-docs/` directory is unwritable.
