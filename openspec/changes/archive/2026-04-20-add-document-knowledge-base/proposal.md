## Why

The agent currently has no access to domain-specific knowledge about truss and roof engineering. Information exists in `hidden/Trusses AI English` but is unreachable during agent execution. Users cannot ask questions about engineering specifications, load calculations, or project documentation. This change enables the agent to answer domain-relevant questions by providing structured access to existing documentation.

## What Changes

- Move `hidden/Trusses AI English` to `agent/knowledge/trusses-ai-english/`
- Add `agent/knowledge/` to `.gitignore` to keep documentation out of version control
- Create `agent/knowledge/trusses-ai-english/summary.md` with:
  - Brief overview of the knowledge base content
  - Summary of information contained in each subdirectory
- Implement direct document reading in the agent:
  - Create a tool to read individual documents from the knowledge base directory
  - Ensure the agent references `summary.md` first for overview, then reads specific documents as needed
- Add a frontend tool to retrieve general knowledge about what the agent knows
- Update agent state to track knowledge base queries and responses

## Capabilities

### New Capabilities

- `document-knowledge-base`: Agent can read documents from a structured knowledge base of truss and roof engineering documentation. The agent references a summary file for overview, then reads specific documents as needed.

### Modified Capabilities

None

## Impact

- **Agent code**: `agent/src/agent.py` and `agent/src/main.py` will be modified to uncomment and implement state, dependencies, agent instance, tools, and result validators
- **New directory**: `agent/knowledge/trusses-ai-english/` (gitignored)
- **Frontend**: Minimal changes to add a tool for "what do you know?" queries
- **State**: Agent state will track knowledge base interactions
- **API**: No API changes; knowledge base access is internal to agent tools
