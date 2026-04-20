# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

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

## Specifications

document-knowledge-base/spec.md
## ADDED Requirements

### Requirement: Knowledge Base Directory Location and Structure
The agent SHALL have a knowledge base directory at `agent/knowledge/trusses-ai-english/` containing all domain documentation. The entire `agent/knowledge/` directory SHALL be gitignored. The knowledge base SHALL contain a `summary.md` file at its root.

#### Scenario: Knowledge base directory exists
- **GIVEN** agent codebase is checked out
- **WHEN** developer lists `agent/` directory
- **THEN** `agent/knowledge/trusses-ai-english/` exists
- **AND** directory contains 33 subdirectories with truss and roof engineering documentation
- **AND** `agent/knowledge/trusses-ai-english/summary.md` exists

#### Scenario: Knowledge base is gitignored
- **GIVEN** `.gitignore` file is loaded
- **WHEN** file contains line `agent/knowledge/`
- **THEN** files in `agent/knowledge/` are not tracked by git

### Requirement: Knowledge Base Summary File Format
The knowledge base SHALL contain a `summary.md` file with the following structure: (1) an overview section describing knowledge base contents, (2) a summary table with columns for Subdirectory, Description, and Key Topics, (3) detailed sections for each subdirectory with a brief description of contents, and (4) a "Last updated" field documenting when the summary was generated.

#### Scenario: Summary file has required sections
- **GIVEN** `agent/knowledge/trusses-ai-english/summary.md` file is read
- **WHEN** file is parsed
- **THEN** file contains a `## Overview` section
- **AND** file contains a summary table with Subdirectory, Description, and Key Topics columns
- **AND** file contains detailed sections for each of the 33 subdirectories
- **AND** file contains a "Last updated:" field

#### Scenario: Summary table covers all subdirectories
- **GIVEN** `summary.md` table is parsed
- **WHEN** table rows are counted
- **THEN** there are 33 rows (one for each subdirectory)
- **AND** each row has non-empty values for Subdirectory, Description, and Key Topics

### Requirement: Agent Document Reading Tool
The agent SHALL provide a `query_knowledge_base` tool that reads documents from the truss and roof engineering knowledge base. The tool SHALL first read `summary.md` to identify relevant subdirectories based on keywords in the query, then list and read markdown files from those subdirectories using Python file I/O. The tool SHALL accept a `query` string and return document contents with source file references.

#### Scenario: Successful knowledge base query for specific project
- **GIVEN** knowledge base exists and user asks "What is permanent roof load for Matlúch House?"
- **WHEN** agent calls `query_knowledge_base(query="permanent roof load Matlúch House")`
- **THEN** tool reads `summary.md` to identify subdirectory "001IK26A - Matlúch_House"
- **AND** tool lists markdown files in `agent/knowledge/trusses-ai-english/001IK26A - Matlúch_House/`
- **AND** tool reads relevant markdown files from that subdirectory
- **AND** tool returns file contents containing permanent roof load information
- **AND** each returned content includes the source file path (e.g., `agent/knowledge/trusses-ai-english/001IK26A - Matlúch_House/Truss Design Variant A/Floor Plan + 3D.md`)
- **AND** at least one returned content contains the value "650 N/m²"

#### Scenario: Query with no matching keywords
- **GIVEN** knowledge base exists and user asks for information not covered by any subdirectory
- **WHEN** agent calls `query_knowledge_base(query="quantum physics applications")`
- **THEN** tool reads `summary.md` and finds no matching subdirectory keywords
- **AND** tool returns a message stating "No relevant information found in the knowledge base"
- **AND** agent is informed to ask user for clarification

#### Scenario: Query matches multiple subdirectories
- **GIVEN** knowledge base exists and user asks a broad question
- **WHEN** agent calls `query_knowledge_base(query="snow load")`
- **THEN** tool reads `summary.md` and identifies multiple subdirectories with "snow load" as a key topic
- **AND** tool reads markdown files from up to 3 matching subdirectories
- **AND** tool returns file contents from each subdirectory with source file paths

### Requirement: File Not Found Handling
The document reading tool SHALL handle `FileNotFoundError` gracefully. If a referenced file does not exist, the tool SHALL log a warning and continue reading available files. The tool SHALL inform the agent of any missing files.

#### Scenario: Missing file handled gracefully
- **GIVEN** `summary.md` references a file that has been deleted
- **WHEN** tool attempts to read the missing file
- **THEN** tool logs a warning message containing the missing file path
- **AND** tool continues reading other available files from the subdirectory
- **AND** returned content includes a note that some files were not found

### Requirement: Frontend Knowledge Summary Tool
The frontend SHALL provide a `get_knowledge_summary` tool that returns a summary of what information is available in the knowledge base. This tool SHALL be exposed as a frontend action in CopilotKit and SHALL return the full content of `summary.md` or a structured representation thereof.

#### Scenario: Frontend tool returns knowledge summary
- **GIVEN** user is in the chat interface and asks "What do you know?"
- **WHEN** agent calls `get_knowledge_summary()`
- **THEN** tool returns a structured summary of the knowledge base
- **AND** summary includes an overview of available information
- **AND** summary lists all 33 subdirectories with brief descriptions
- **AND** summary mentions that detailed information is available about truss designs, load calculations, and engineering specifications

### Requirement: Agent State Tracks Knowledge Queries
The agent state SHALL include a `knowledge_queries` field that tracks all knowledge base queries made during the conversation, and a `last_knowledge_result` field that stores the most recent retrieval result. The state SHALL be updated on every call to `query_knowledge_base`.

#### Scenario: State updated after knowledge query
- **GIVEN** agent state is initialized with empty `knowledge_queries` and `last_knowledge_result`
- **WHEN** agent calls `query_knowledge_base(query="permanent roof load")`
- **THEN** `knowledge_queries` contains one entry with query="permanent roof load", retrieval result, and a timestamp
- **AND** `last_knowledge_result` contains the retrieval result
- **AND** subsequent calls to `query_knowledge_base` append to `knowledge_queries` rather than replacing it

#### Scenario: State persists across conversation turns
- **GIVEN** agent has made two knowledge queries in the conversation
- **WHEN** user asks a follow-up question about the first query
- **THEN** `knowledge_queries` contains both queries with their respective results and timestamps
- **AND** agent can reference previous retrieval results without re-querying the knowledge base

### Requirement: Agent References Summary First
When answering questions about the knowledge base, the agent SHALL first reference `summary.md` to determine the relevant scope and subdirectories before reading specific documents. The agent SHALL use `get_knowledge_summary` for overview questions and `query_knowledge_base` for specific queries.

#### Scenario: Overview question uses summary
- **GIVEN** user asks "What projects do you have information about?"
- **WHEN** agent processes the question
- **THEN** agent calls `get_knowledge_summary()` instead of `query_knowledge_base()`
- **AND** response includes information from `summary.md` about available projects

#### Scenario: Specific question uses document reading
- **GIVEN** user asks "What is snow load for Matlúch House?"
- **WHEN** agent processes the question
- **THEN** agent calls `query_knowledge_base(query="snow load Matlúch House")`
- **AND** response includes specific file contents with load values
- **AND** response references the source document path

#### Scenario: Two-step retrieval for complex queries
- **GIVEN** user asks "What materials are used in roof designs for family houses?"
- **WHEN** agent processes the question
- **THEN** agent first calls `get_knowledge_summary()` to identify family house projects
- **AND** agent then calls `query_knowledge_base(query="roof materials", filtering to family house subdirectories)`
- **AND** response combines overview from summary with specific material information from files



## Design

## Context

The agent codebase is in a skeleton state where only `OpenAIModel` configuration is active. State management (`YourState`), dependency injection (`StateDeps`), `Agent` instance, tools, and result validators are commented out. Domain knowledge about truss and roof engineering exists in `hidden/Trusses AI English` but is not accessible to the agent.

Current constraints:
- Agent code must be uncommented and extended to support state and tools
- Knowledge base must be gitignored
- Simple approach: direct file reading, no complex retrieval infrastructure
- No external dependencies required

## Goals / Non-Goals

**Goals:**

1. Move `hidden/Trusses AI English` to `agent/knowledge/trusses-ai-english/` and gitignore the entire `agent/knowledge/` directory
2. Create a `summary.md` in the knowledge base that provides an overview of available information and subdirectory contents
3. Uncomment and implement agent state, dependencies, agent instance, tools, and result validators in `agent/src/agent.py`
4. Implement direct document reading using Python's file I/O: the agent can read individual markdown files from the knowledge base
5. Create an agent tool that reads documents by first consulting `summary.md` to identify relevant subdirectories, then reading specific files
6. Add a frontend tool to ask "what do you know?" which returns summary information
7. Track knowledge base queries in agent state for conversation context

**Non-Goals:**

- No RAG, vector database, or semantic search (using direct file reading only)
- No embeddings or HuggingFace models
- No external dependencies or infrastructure
- No support for real-time updates to knowledge base (static documents only)
- No changes to CopilotKit API or frontend beyond adding "what do you know?" tool
- No automatic knowledge base refresh or monitoring
- No multi-language support (English documents only)

## Decisions

### Decision 1: Knowledge Base Location

**Choice:** Store knowledge base at `agent/knowledge/trusses-ai-english/` and gitignore `agent/knowledge/`

**Rationale:**
- Placing knowledge under `agent/` keeps domain data with the agent that uses it
- Gitignoring the entire `knowledge/` directory prevents accidental commits of documentation
- The location is explicit and discoverable for developers

**Alternatives considered:**
- Store in project root as `knowledge/`: Rejected because it mixes agent-specific data with project structure
- Store in `hidden/` and add to gitignore: Rejected because `hidden/` is already gitignored and contains unrelated files
- Use external storage (S3, database): Rejected because it adds infrastructure complexity beyond scope

### Decision 2: Document Reading Strategy

**Choice:** Use Python's standard file I/O (`open()`, `pathlib`) to read markdown files directly

**Rationale:**
- No external dependencies required (Python standard library)
- Simple and predictable behavior: read specific files based on file paths
- Suitable for expected document count (33 subdirectories with ~3 markdown files each)
- Agent uses `summary.md` to determine which files are relevant to a query

**Implementation algorithm:**
1. For knowledge summary requests: read `summary.md` and return its contents
2. For specific questions:
   a. Read `summary.md` to identify relevant subdirectories based on keywords in the query
   b. List markdown files in relevant subdirectories using `pathlib.Path.glob("*.md")`
   c. Read file contents using standard Python file I/O
   d. Return file contents with source file path references
3. For queries that don't match any subdirectory, read a sampling of documents from multiple subdirectories and let the agent determine relevance

**Alternatives considered:**
- RAG with LlamaIndex embeddings: Rejected as too complex for current needs
- Vector database search: Rejected because it adds external service dependency and operational overhead
- Simple grep across all files: Rejected because it doesn't provide file path context

### Decision 3: Agent Tool Design

**Choice:** Create two tools: `query_knowledge_base` (for agent use) and `get_knowledge_summary` (for frontend exposure)

**Rationale:**
- Separation of concerns: `query_knowledge_base` for specific document lookups, `get_knowledge_summary` for overview
- `query_knowledge_base` is agent-only: agent decides when to call it based on user questions
- `get_knowledge_summary` is a frontend tool: users can explicitly ask "what do you know?"
- Both tools use the same file reading mechanism

**Tool signatures:**
```python
@agent.tool
async def query_knowledge_base(ctx: RunContext[StateDeps], query: str) -> str:
    """Query truss and roof engineering knowledge base by reading relevant documents.

    Args:
        ctx: Agent context with state
        query: The user's question or topic to search for

    Returns:
        Relevant document contents with source file references
    """

@agent.tool
async def get_knowledge_summary(ctx: RunContext[StateDeps]) -> str:
    """Get an overview of what information is available in the knowledge base.

    Args:
        ctx: Agent context with state

    Returns:
        Summary of knowledge base contents organized by subdirectory
    """
```

**Alternatives considered:**
- Single combined tool: Rejected because it conflates overview queries with specific lookups
- No summary tool, rely on agent to read summary.md directly: Rejected because frontend users cannot easily discover what's available

### Decision 4: State Management

**Choice:** Add `knowledge_queries` and `last_knowledge_result` to agent state

**State definition:**
```python
class KnowledgeQuery(BaseModel):
    query: str
    result: str
    timestamp: str

class YourState(BaseModel):
    user_input: str = ""
    ai_response: str = ""
    knowledge_queries: List[KnowledgeQuery] = []
    last_knowledge_result: Optional[str] = None
```

**Rationale:**
- Tracking queries provides conversation context and allows agent to reference previous searches
- `last_knowledge_result` enables agent to refer to the most recent retrieval without re-querying
- List structure allows for conversation history that could be used for follow-up questions

**Alternatives considered:**
- No state tracking: Rejected because it loses conversation context
- Full conversation history with document citations: Rejected as overly complex for initial implementation

### Decision 5: summary.md Format

**Choice:** Structured markdown with sections for overall overview, per-subdirectory summary, and quick reference table

**Format structure:**
```markdown
# Trusses AI English Knowledge Base

## Overview
[Brief description of what this knowledge base contains]

## Subdirectory Summary
| Subdirectory | Description | Key Topics |
|--------------|-------------|------------|
| 001IK26A - Matlúch_House | Family house project with storage space | Roof load, truss supports, storage requirements |
| 002IK26A - Matlúch_Garage | Garage project | Truss design, load calculations |
| ... | ... | ... |

## Detailed Subdirectory Information

### 001IK26A - Matlúch_House
[Detailed summary of contents: truss designs, load calculations, materials]

### 002IK26A - Matlúch_Garage
[Detailed summary of contents]
...
```

**Rationale:**
- Table format allows quick scanning by agent
- Detailed sections provide context for file reading decisions
- Structured format is parseable by agent for intelligent file selection

**Alternatives considered:**
- Plain text unstructured summary: Rejected because it makes programmatic access difficult
- JSON format: Rejected because markdown is more readable for humans and agent

## Risks / Trade-offs

### Risk 1: Document Read Performance

**Risk:** Reading many files sequentially could be slow for queries that span multiple subdirectories

**Mitigation:**
- Agent uses `summary.md` to narrow down to relevant subdirectories before reading files
- Limit number of files read per query (default: read from 1-3 subdirectories maximum)
- Read files only when tool is called, not at startup
- Add timeout protection for file operations

### Risk 2: File Not Found Errors

**Risk:** Files referenced in `summary.md` may be moved, renamed, or deleted

**Mitigation:**
- Tool handles `FileNotFoundError` gracefully and logs a warning
- If a file is not found, tool continues with available files and informs agent
- When updating `summary.md`, verify all referenced files exist

### Risk 3: Stale Knowledge Base

**Risk:** Knowledge base may become outdated without explicit refresh mechanism

**Mitigation:**
- Document expectation that knowledge base is static and manually updated
- Add comment in `summary.md` with "Last updated: [date]" to encourage maintenance
- Non-goal: automatic refresh is explicitly out of scope

### Risk 4: Large File Contents

**Risk:** Some markdown files may be large and could consume significant context

**Mitigation:**
- Return full file contents (files are expected to be < 10KB each based on manual inspection)
- If a file is too large, tool returns a truncation message with file path
- Agent can request specific files to be read if needed

### Trade-off 1: Direct Reading vs. RAG

**Trade-off:** Direct file reading is simpler but requires agent to identify which files to read

**Decision:** Direct file reading chosen because:
- No external dependencies or infrastructure
- Simpler to implement and debug
- Agent uses `summary.md` for intelligent file selection
- Sufficient for expected document count (~100 markdown files)

**Future consideration:** If document count grows significantly or queries become too complex, migrate to RAG with embeddings

### Trade-off 2: Query Precision vs. Flexibility

**Trade-off:** Using keyword matching from `summary.md` to select subdirectories may miss relevant files

**Decision:** Keyword matching chosen because:
- Provides good precision for engineering queries (specific project names, load types, etc.)
- Agent can request additional files if initial results are insufficient
- Simpler than implementing full semantic search

**Future consideration:** Add fuzzy matching or file content previewing if keyword matching proves inadequate

## Migration Plan

### Implementation Steps

1. Create directory structure:
   ```bash
   mkdir -p agent/knowledge
   mv "hidden/Trusses AI English" agent/knowledge/trusses-ai-english/
   echo "agent/knowledge/" >> .gitignore
   ```

2. Generate `agent/knowledge/trusses-ai-english/summary.md` by scanning subdirectories and extracting metadata from markdown files and `translation-notes.txt`

3. Update `.gitignore` to include `agent/knowledge/` (verify entry exists)

4. Uncomment and implement in `agent/src/agent.py`:
   - `YourState` with knowledge tracking fields
   - `StateDeps` class
   - `Agent` instance with appropriate system prompt
   - `query_knowledge_base` tool
   - `get_knowledge_summary` tool
   - Result validator (optional, for response filtering)

5. Update `agent/src/main.py` to work with the uncommented code (no changes needed, imports already match)

6. Add frontend tool for `get_knowledge_summary` in `src/app/page.tsx`

7. Test file reading:
   - Query for load calculations from specific projects returns file contents
   - Query "what do you know?" returns summary
   - Verify subdirectory selection (e.g., query about "Matlúch_House" reads files from that subdirectory)

8. Run lint and typecheck: `cd agent && python -m ruff check . && python -m mypy .`

### Rollback Strategy

If implementation causes issues:
1. Delete implemented tools from `agent/src/agent.py`
2. Re-comment out state, dependencies, agent instance, and result validators
3. Remove `agent/knowledge/` from `.gitignore`
4. Move `agent/knowledge/trusses-ai-english/` back to `hidden/Trusses AI English`
5. Revert frontend tool addition in `src/app/page.tsx`

The rollback restores the agent to its skeleton state and removes all document reading functionality.

## Open Questions

None. All technical decisions are specified and implementation is straightforward using Python standard library.

## Current Task Context

## Current Task
- 1.1 Create `agent/knowledge/` directory and move `hidden/Trusses AI English` to `agent/knowledge/trusses-ai-english/`
