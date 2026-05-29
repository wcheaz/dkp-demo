## Purpose

Defines the integration of DXF generation into the `run-generate-design` skill workflow, including auto-trigger rules, API reference documentation, and tool action listing.

## Requirements

### Requirement: generate_dxf step in run-generate-design skill workflow

The `run-generate-design` skill SHALL include a Step 4g — DXF generation that triggers when `design-generation` or `design-modification` produces a `"complete"` status (all 4 desirable fields present: `building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`). The step SHALL instruct the agent to call the `generate_dxf` tool with the current design's `id`.

#### Scenario: DXF auto-generated after complete design generation
- **WHEN** the skill's Step 4d (design generation) produces a design entry with status `"complete"` (all 4 desirable fields present)
- **THEN** Step 4g SHALL execute automatically, calling `generate_dxf` with the design entry's `id`, and the design entry's `dxfContent` SHALL be populated with base64-encoded DXF data

#### Scenario: DXF generated after design modification produces complete status
- **WHEN** the skill's Step 4e (design modification) updates a design entry to have status `"complete"` (all 4 desirable fields present)
- **THEN** Step 4g SHALL execute automatically, calling `generate_dxf` with the modified design entry's `id`

#### Scenario: DXF skipped for incomplete design
- **WHEN** the skill's Step 4d produces a design entry with status `"Design In Progress"` (one or more desirable fields missing)
- **THEN** Step 4g SHALL NOT execute for that design entry

#### Scenario: DXF skipped for non-design intents
- **WHEN** the classified intent does not include `design-generation` or `design-modification`
- **THEN** Step 4g SHALL NOT execute

### Requirement: DXF builder API reference doc

The skill's references directory SHALL contain a file `references/dxf-builder-api.md` documenting the `build_dxf` function's signature, input parameters (mapped from `DesignParameters` fields), output format (R2000 DXF bytes), and the five DXF layers with their entity types. The reference SHALL be loadable via the skill's `read_skill_resource` mechanism.

#### Scenario: Agent loads DXF builder reference
- **WHEN** the agent calls `read_skill_resource("run-generate-design", "references/dxf-builder-api.md")`
- **THEN** the returned content SHALL contain the `build_dxf` function signature, the mapping from `DesignParameters` fields to DXF content, and the layer schema (`Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, `Title_Block`)

#### Scenario: Reference doc describes auto-trigger rule
- **WHEN** the DXF builder reference is read
- **THEN** it SHALL state that DXF generation is auto-triggered when design status is `"complete"` and that the tool requires `floorPlanDimensions` and `roofType` at minimum

### Requirement: DXF tool action listed in skill's auto-execution rules

The skill's Step 4 introduction SHALL document the DXF auto-execution rule: when design-generation or design-modification produces `"complete"` status, Step 4g (DXF generation) SHALL execute automatically alongside Step 4c (pricing calculation).

#### Scenario: Auto-execution rules mention DXF
- **WHEN** the skill's Step 4 section is read
- **THEN** the auto-execution rules SHALL state that both pricing (4c) and DXF generation (4g) are automatically executed when a design reaches `"complete"` status
