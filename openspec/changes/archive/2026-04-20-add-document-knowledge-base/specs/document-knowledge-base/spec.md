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
