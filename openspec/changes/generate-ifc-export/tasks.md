## 1. Setup & Pre-flight

- [x] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under [baselines/](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/)
  - Change: Capture current state of all gates later tasks require.
    - Test: `PYTHONPATH=agent/src:agent uv run --project agent pytest test/ > .ralph/baselines/generate-ifc-export-test.txt; echo "EXIT=$?" >> .ralph/baselines/generate-ifc-export-test.txt`
    - Typecheck: `npx tsc --noEmit > .ralph/baselines/generate-ifc-export-typecheck.txt; echo "EXIT=$?" >> .ralph/baselines/generate-ifc-export-typecheck.txt`
    - Lint: `npm run lint > .ralph/baselines/generate-ifc-export-lint.txt; echo "EXIT=$?" >> .ralph/baselines/generate-ifc-export-lint.txt`
    - Mypy: `uv run --project agent mypy agent/src/ > .ralph/baselines/generate-ifc-export-mypy.txt; echo "EXIT=$?" >> .ralph/baselines/generate-ifc-export-mypy.txt`
    - README: Create [generate-ifc-export-readme.md](file:///home/ncheaz/git/dkp-demo/.ralph/baselines/generate-ifc-export-readme.md) listing passing/failing gates, exit codes, and exact failing identifiers.
  - Done when:
    - `test -f .ralph/baselines/generate-ifc-export-test.txt` exits 0
    - `tail -n 1 .ralph/baselines/generate-ifc-export-test.txt | grep -q "^EXIT=[0-9]\+$"` exits 0
    - `test -f .ralph/baselines/generate-ifc-export-typecheck.txt` exits 0
    - `tail -n 1 .ralph/baselines/generate-ifc-export-typecheck.txt | grep -q "^EXIT=[0-9]\+$"` exits 0
    - `test -f .ralph/baselines/generate-ifc-export-lint.txt` exits 0
    - `tail -n 1 .ralph/baselines/generate-ifc-export-lint.txt | grep -q "^EXIT=[0-9]\+$"` exits 0
    - `test -f .ralph/baselines/generate-ifc-export-mypy.txt` exits 0
    - `tail -n 1 .ralph/baselines/generate-ifc-export-mypy.txt | grep -q "^EXIT=[0-9]\+$"` exits 0
    - `test -f .ralph/baselines/generate-ifc-export-readme.md` exits 0
  - Stop and hand off if:
    - any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

- [x] **Configure backend Python dependencies**
  - Scope: [pyproject.toml](file:///home/ncheaz/git/dkp-demo/agent/pyproject.toml), [uv.lock](file:///home/ncheaz/git/dkp-demo/agent/uv.lock), [requirements.txt](file:///home/ncheaz/git/dkp-demo/requirements.txt)
  - Change: Add `ifcopenshell` package to Python dependencies.
  - Done when:
    - `rg -i "ifcopenshell" agent/pyproject.toml` exits 0
    - `rg -i "ifcopenshell" requirements.txt` exits 0
    - `uv run --project agent python -c "import ifcopenshell"` exits 0
  - Stop and hand off if:
    - installation or synchronization of `ifcopenshell` fails due to compilation errors, missing prebuilt wheels, or dependency resolution conflicts.

## 2. Shared Contracts & Refactoring

- [x] **Extend DesignEntry shared contract**
  - Scope: [types.ts](file:///home/ncheaz/git/dkp-demo/src/lib/types.ts), [agent.py](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py)
  - Change: Add `ifcContent` base64 string property to `DesignEntry` in both TypeScript and Python Pydantic models.
  - Done when:
    - `rg "ifcContent" src/lib/types.ts` exits 0
    - `rg "ifcContent" agent/src/agent.py` exits 0
    - `npx tsc --noEmit` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - `uv run --project agent ruff check agent/src/agent.py` exits 0
    - `uv run --project agent mypy agent/src/agent.py` exits 0
  - Stop and hand off if:
    - model extension causes typescript compilation errors or pydantic model schema conflicts.

- [x] **Extract shared geometry calculation module**
  - Scope: [geometry_solver.py](file:///home/ncheaz/git/dkp-demo/agent/src/geometry_solver.py), [dxf_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/dxf_builder.py)
  - Change: Decouple geometry math into a single module so wall coordinates and truss layouts are shared.
  - Done when:
    - `PYTHONPATH=agent/src:agent uv run --project agent python -c "import src.geometry_solver"` exits 0
    - `uv run --project agent ruff check agent/src/geometry_solver.py` exits 0
    - `uv run --project agent mypy agent/src/geometry_solver.py` exits 0
    - `uv run --project agent ruff check agent/src/dxf_builder.py` exits 0
    - `uv run --project agent mypy agent/src/dxf_builder.py` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_dxf_builder.py` exits 0
  - Stop and hand off if:
    - refactoring breaks existing DXF generation tests and restoring the geometry interface does not resolve them.

## 3. IFC Generation & API Integration

- [x] **Implement IFC Builder module**
  - Scope: [ifc_builder.py](file:///home/ncheaz/git/dkp-demo/agent/src/ifc_builder.py), [test_ifc_builder.py](file:///home/ncheaz/git/dkp-demo/test/test_ifc_builder.py)
  - Change: Create the IFC constructor to output structural wall and truss representations using the IFC2x3 schema.
  - Done when:
    - `PYTHONPATH=agent/src:agent uv run --project agent python -c "from src.ifc_builder import build_ifc"` exits 0
    - `uv run --project agent ruff check agent/src/ifc_builder.py` exits 0
    - `uv run --project agent mypy agent/src/ifc_builder.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_builder.py` exits 0
  - Stop and hand off if:
    - `ifcopenshell` fails to compile coordinate placements or raises unhandled schema exceptions.

- [x] **Register IFC export API endpoint**
  - Scope: [main.py](file:///home/ncheaz/git/dkp-demo/agent/src/main.py), [test_ifc_endpoint.py](file:///home/ncheaz/git/dkp-demo/test/test_ifc_endpoint.py)
  - Change: Implement and map the `POST /api/ifc/generate` route.
  - Done when:
    - `uv run --project agent ruff check agent/src/main.py` exits 0
    - `uv run --project agent mypy agent/src/main.py` exits 0
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/test_ifc_endpoint.py` exits 0
  - Stop and hand off if:
    - route registration causes conflicts or Starlette server startup failure.

## 4. Frontend UI & Localization

- [ ] **Implement generate_ifc frontend tool**
  - Scope: [page.tsx](file:///home/ncheaz/git/dkp-demo/src/app/page.tsx)
  - Change: Add a `useFrontendTool` named `generate_ifc` that receives `design_id`, calls the backend's `/api/ifc/generate` endpoint, base64-encodes the response, and stores it in `entry.ifcContent` in React state.
  - Done when:
    - `rg "generate_ifc" src/app/page.tsx` exits 0
    - `npx tsc --noEmit` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - `npx eslint src/app/page.tsx` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if:
    - the tool cannot update state or endpoint fetch fails.

- [ ] **Implement Download IFC button in UI with localization**
  - Scope: [design-component.tsx](file:///home/ncheaz/git/dkp-demo/src/components/design-component.tsx), [en.json](file:///home/ncheaz/git/dkp-demo/src/i18n/messages/en.json), [sk.json](file:///home/ncheaz/git/dkp-demo/src/i18n/messages/sk.json), [check-i18n-parity.mjs](file:///home/ncheaz/git/dkp-demo/scripts/check-i18n-parity.mjs)
  - Change: Add a localized "Download IFC" button to the design component that is visible when `ifcContent` is present.
  - Done when:
    - `rg "downloadIfc" src/components/design-component.tsx` exits 0
    - `rg "downloadIfc" src/i18n/messages/en.json` exits 0
    - `rg "downloadIfc" src/i18n/messages/sk.json` exits 0
    - `node scripts/check-i18n-parity.mjs` exits 0
    - `npx tsc --noEmit` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - `npx eslint src/components/design-component.tsx` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
  - Stop and hand off if:
    - component does not compile, triggers state update loops, or translation parsing fails.

## 5. Integrated Quality Gates

- [ ] **Verify full system compatibility**
  - Scope: Entire codebase under [src/](file:///home/ncheaz/git/dkp-demo/agent/src/) and [test/](file:///home/ncheaz/git/dkp-demo/test/)
  - Change: Complete and verify that all integration gates pass without error.
  - Done when:
    - `uv run --project agent ruff check agent/src/` exits 0
    - `uv run --project agent mypy agent/src/` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - `PYTHONPATH=agent/src:agent uv run --project agent pytest test/` exits 0
    - `npx tsc --noEmit` exits 0
    - `npm run lint` exits 0, or failures match the pre-flight baseline with no new failures in this task's scope
    - `node scripts/check-i18n-parity.mjs` exits 0
  - Stop and hand off if:
    - baseline-checked gates fail with new failures outside this change's scope.
