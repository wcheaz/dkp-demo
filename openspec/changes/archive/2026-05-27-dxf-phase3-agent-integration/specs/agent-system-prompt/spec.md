## MODIFIED Requirements

### Requirement: System prompt defines tool usage rules
The system prompt SHALL contain detailed instructions for each tool: `get_knowledge_summary`, `query_knowledge_base`, `generate_design`, `modify_design_entry`, `update_design_parameters`, `generate_quote`, `reset_design`, and `generate_dxf`.

The tool catalog section of `_BASE_PROMPT` SHALL include the entry: `- generate_dxf: Generate a downloadable DXF CAD file for a completed design.`

The prompt SHALL instruct the agent to call `generate_dxf` after `generate_design` completes with all required parameters present, or when the user explicitly requests a DXF or CAD file.

#### Scenario: Tool rules present
- **WHEN** the system prompt is read
- **THEN** it SHALL contain sections for each of the 8 tools with usage conditions and parameter descriptions

#### Scenario: generate_dxf in tool catalog
- **WHEN** the `_BASE_PROMPT` string is read
- **THEN** it SHALL contain the line `- generate_dxf: Generate a downloadable DXF CAD file for a completed design.` within the tool catalog section

#### Scenario: generate_dxf trigger rule present
- **WHEN** the system prompt is read
- **THEN** it SHALL instruct the agent to call `generate_dxf` when a design completes with all required parameters or when the user requests a DXF file

#### Scenario: Existing tool catalog entries preserved
- **WHEN** the updated `_BASE_PROMPT` is compared to the previous version
- **THEN** all 7 existing tool catalog entries (`get_knowledge_summary`, `query_knowledge_base`, `generate_design`, `modify_design_entry`, `update_design_parameters`, `generate_quote`, `reset_design`) SHALL remain unchanged
