## ADDED Requirements

### Requirement: query_knowledge_base tool
The system SHALL register an async `query_knowledge_base` tool on the agent that accepts `query: str`, performs keyword-scoring search across all subdirectories in `KNOWLEDGE_BASE_DIR`, and returns the concatenated markdown content from the top 3 matching projects with source file paths.

#### Scenario: Exact keyword match in subdirectory name
- **WHEN** `query_knowledge_base` is called with `query="truss"`
- **THEN** subdirectories whose names contain query words SHALL receive a weighted name score (2x per word match) plus a section-content score

#### Scenario: Fallback to first three directories
- **WHEN** no subdirectory scores above zero for the query
- **THEN** the tool SHALL return results from the first 3 subdirectories alphabetically

#### Scenario: Result includes source paths
- **WHEN** markdown files are read from matched subdirectories
- **THEN** each result SHALL be prefixed with `--- Source: <relative-path> ---` where the path is relative to `KNOWLEDGE_BASE_DIR.parent.parent`

#### Scenario: Query logged in state
- **WHEN** `query_knowledge_base` completes
- **THEN** a `KnowledgeQuery` SHALL be appended to `ctx.deps.state.knowledge_queries` with the query text, truncated result (first 500 chars), and UTC ISO timestamp

#### Scenario: Missing summary file
- **WHEN** `summary.md` does not exist in `KNOWLEDGE_BASE_DIR`
- **THEN** the tool SHALL return `"Knowledge base summary not found. Please contact the administrator."`

### Requirement: get_knowledge_summary tool
The system SHALL register an async `get_knowledge_summary` tool on the agent that takes no parameters and returns the contents of `KNOWLEDGE_BASE_DIR / "summary.md"`.

#### Scenario: Summary returned
- **WHEN** `get_knowledge_summary` is called
- **THEN** the full text of `summary.md` SHALL be returned as a string

#### Scenario: Missing summary file
- **WHEN** `summary.md` does not exist
- **THEN** the tool SHALL return `"Knowledge base summary not found. Please contact the administrator."`
