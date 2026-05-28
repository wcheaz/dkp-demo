## Context

Phases 1-4 of the DXF generation feature are complete and archived. The codebase has:

- `agent/src/dxf_builder.py` (368 lines) — geometry engine producing valid R2000 DXF with 5 layers
- `agent/src/agent.py:413-442` — `generate_dxf` agent tool, base64-encodes output into `DesignEntry.dxfContent`
- `test/test_dxf_builder.py` (428 lines) — comprehensive unit tests covering all roof types, layer validation, coordinate values, round-trip re-readability
- `test/test_generate_dxf.py` (128 lines) — agent tool tests
- `test/test_dxf_endpoint.py` (106 lines) — HTTP endpoint tests
- `.agents/skills/run-generate-design/SKILL.md` (326 lines) — the skill that encodes the agent's decision loop

The skill's Step 4 (Execute Simulated Tool Actions) has 6 tool actions (4a-4f) but no DXF generation step. The system prompt (`agent/src/agent.py:267`) lists `generate_dxf` in the tool catalog, but the skill never instructs the agent to call it.

## Goals / Non-Goals

**Goals:**

- Verify existing `test/test_dxf_builder.py` tests pass and cover all roof types, layers, entity counts, coordinates, and DXF round-trip
- Add `generate_dxf` as a tool action in the `run-generate-design` skill, triggered automatically after design generation or modification completes with full parameters
- Add a DXF builder API reference doc to `.agents/skills/run-generate-design/references/` so the agent knows the builder's interface and output shape
- Validate that generated DXF files render correctly in the embedded cad-viewer and at least one external tool

**Non-Goals:**

- Changes to `dxf_builder.py` geometry engine — it is feature-complete
- Changes to the agent tool (`generate_dxf`), endpoint, or DesignEntry model — they are working
- Evaluating cad-viewer's offline HTML export capability — low priority, deferred
- Adding new DXF entity types or annotation features
- Browser automated tests for the cad-viewer rendering

## Decisions

### D1: DXF generation step placement in skill workflow

**Decision:** Add a new Step 4g (`DXF generation`) after the existing tool actions, triggered when `design-generation` or `design-modification` produces a `"complete"` status (all 4 desirable fields present).

**Rationale:** DXF generation requires complete parameters (`floorPlanDimensions` + `roofType` at minimum). It should fire automatically after design completion, parallel to how pricing auto-fires (Step 4c) when status is `"complete"`. Placing it after 4f keeps the existing step numbering intact and matches the natural workflow: design → price → DXF.

**Alternative considered:** Add DXF as a sub-step within 4d/4e. Rejected because it would change existing step structure and make the skill harder to follow.

### D2: DXF generation trigger rule

**Decision:** Auto-trigger `generate_dxf` when design status is `"complete"`. Do not require explicit user request.

**Rationale:** The DXF is a CAD-ready artifact that adds value to every completed design. The user does not need to ask for it separately. This mirrors the auto-pricing behavior already in the skill.

**Alternative considered:** Only generate on explicit request. Rejected because it reduces demo impact — the viewer and download button would sit empty until the user thinks to ask.

### D3: DXF builder reference doc format

**Decision:** Create `references/dxf-builder-api.md` with the builder's function signature, parameter mapping, output shape, and layer schema. Written as a concise reference (not full API docs).

**Rationale:** The skill's `read_skill_resource` mechanism lets the agent load reference docs on demand. A DXF builder reference gives the agent context about what `build_dxf` produces without bloating the main SKILL.md.

### D4: Test verification strategy

**Decision:** Run `pytest test/test_dxf_builder.py` as a verification gate. Confirm all tests pass. No new tests needed — the existing suite already covers all roof types, layers, entity counts, coordinates, round-trip, and edge cases.

**Rationale:** The existing 428-line test file has 20+ test classes covering every requirement in `openspec/specs/dxf-builder/spec.md`. Adding redundant tests wastes loop iterations.

## Risks / Trade-offs

- **[DXF rendering varies across viewers]** — Some CAD viewers may render dimensions or hatches differently. Mitigation: validate in LibreCAD (free, widely used) and the embedded cad-viewer; document any visual discrepancies as known limitations.
- **[Skill step ordering]** — Adding 4g after 4f means DXF generation happens after reset actions, which is correct (reset destroys designs, so DXF would not apply). No conflict.
- **[Manual validation step]** — DXF output validation in external CAD tools requires human execution. Mitigation: place in Human Handoff section, not in the autonomous task path.
