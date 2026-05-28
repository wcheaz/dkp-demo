## Why

The DXF generation pipeline (Phases 1-4) is functionally complete — builder, agent tool, HTTP endpoint, and embedded CAD viewer all exist. However, the `run-generate-design` skill has no awareness of `generate_dxf`, so the agent never triggers DXF generation during its decision loop. Additionally, the existing unit tests for `dxf_builder.py` need a verification gate to confirm coverage and correctness before the feature is considered production-ready.

## What Changes

- Verify existing unit tests for `dxf_builder.py` cover all roof types, layer names, entity counts, coordinate values, and DXF round-trip re-readability
- Add a `generate_dxf` tool action step to the `run-generate-design` skill's decision-loop workflow, so the agent automatically triggers DXF generation after design completion
- Add DXF builder API reference documentation to the skill's references directory
- Validate generated DXF output renders correctly in the embedded cad-viewer and at least one external CAD tool (LibreCAD)

## Capabilities

### New Capabilities

- `dxf-skill-integration`: Adds `generate_dxf` as a tool action in the `run-generate-design` skill workflow, triggered after design generation or modification completes. Includes a reference doc for the DXF builder API.

### Modified Capabilities

_(none — existing DXF specs and test files require no requirement-level changes)_

## Impact

- `.agents/skills/run-generate-design/SKILL.md` — new tool action step and DXF reference
- `.agents/skills/run-generate-design/references/` — new reference doc for DXF builder API
- `test/test_dxf_builder.py` — verification gate (read-only, no changes expected)
- Manual validation: generated DXF files opened in embedded viewer + LibreCAD
