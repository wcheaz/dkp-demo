## ADDED Requirements

### Requirement: reset_design tool documented alongside modify_design_entry

The agent's system prompt section that documents frontend tools SHALL include `reset_design` documentation in the same block as `modify_design_entry`, so the agent is aware of both modification and reset capabilities when deciding which tool to use.

#### Scenario: System prompt lists both modify and reset tools

- **GIVEN** the agent system prompt in `agent/src/agent.py`
- **WHEN** the system prompt is read
- **THEN** the section documenting `modify_design_entry` and the section documenting `reset_design` SHALL both be present
- **AND** they SHALL appear in the same tool documentation block (not in separate disconnected sections)
