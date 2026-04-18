## 1. Directory Structure and File Movement

- [x] 1.1 Create `agent/knowledge/` directory and move `hidden/Trusses AI English` to `agent/knowledge/trusses-ai-english/`
  **Done when:** Directory `agent/knowledge/trusses-ai-english/` exists and contains all 33 subdirectories from the original location

- [x] 1.2 Add `agent/knowledge/` to `.gitignore`
  **Done when:** File `.gitignore` contains the line `agent/knowledge/`

## 2. Knowledge Base Summary Generation

- [x] 2.1 Scan subdirectories and generate `agent/knowledge/trusses-ai-english/summary.md` with overview section, summary table, and detailed sections
  **Done when:** File `agent/knowledge/trusses-ai-english/summary.md` exists with all required sections: overview, 33-row summary table, and detailed sections for each subdirectory with "Last updated" field

## 3. Agent State, Dependencies, and Instance

- [x] 3.1 Uncomment and implement `KnowledgeQuery` BaseModel in `agent/src/agent.py` for tracking knowledge base interactions
  **Done when:** `KnowledgeQuery` class is defined with fields: `query: str`, `result: str`, and `timestamp: str`

- [x] 3.2 Uncomment and implement `YourState` class in `agent/src/agent.py` with `knowledge_queries` and `last_knowledge_result` fields
  **Done when:** `YourState` class is uncommented with fields: `user_input: str = ""`, `ai_response: str = ""`, `knowledge_queries: List[KnowledgeQuery] = []`, and `last_knowledge_result: Optional[str] = None`

- [ ] 3.3 Uncomment and implement `StateDeps` class in `agent/src/agent.py` to wrap `YourState`
  **Done when:** `StateDeps` class is uncommented with `__init__(self, state: YourState)` method that stores the state

- [ ] 3.4 Uncomment and implement the `Agent` instance in `agent/src/agent.py` with appropriate system prompt and `deps_type=StateDeps`
  **Done when:** `agent` variable is uncommented and instantiated with `model`, `deps_type=StateDeps`, and system prompt that references the knowledge base

## 4. Document Reading Tool Implementation

- [ ] 4.1 Implement file reading logic and `query_knowledge_base` tool in `agent/src/agent.py` using Python's standard library (`pathlib`, `open`)
  **Done when:** Tool is decorated with `@agent.tool`, has signature `async def query_knowledge_base(ctx: RunContext[StateDeps], query: str) -> str`, reads `summary.md` to identify subdirectories, reads markdown files from those subdirectories, handles `FileNotFoundError` gracefully, and returns document contents with source file paths

- [ ] 4.2 Update agent state on each `query_knowledge_base` call in `agent/src/agent.py`
  **Done when:** Tool appends `KnowledgeQuery` entry to `ctx.deps.state.knowledge_queries` and sets `ctx.deps.state.last_knowledge_result` with the retrieval result

## 5. Knowledge Summary Tool Implementation

- [ ] 5.1 Implement `get_knowledge_summary` tool in `agent/src/agent.py` that reads `summary.md`
  **Done when:** Tool is decorated with `@agent.tool`, has signature `async def get_knowledge_summary(ctx: RunContext[StateDeps]) -> str`, and returns the full content of `agent/knowledge/trusses-ai-english/summary.md`

## 6. Entry Point and Frontend Integration

- [ ] 6.1 Verify `agent/src/main.py` imports work with uncommented code (imports should already match)
  **Done when:** File `agent/src/main.py` has no import errors and can be executed

- [ ] 6.2 Add `get_knowledge_summary` as a frontend tool in `src/app/page.tsx` using `useFrontendTool`
  **Done when:** `useFrontendTool` hook is added with name `get_knowledge_summary`, parameters empty, and handler returns a message invoking the agent tool

## 7. Verification and Testing

- [ ] 7.1 Run agent server and verify document reading works (e.g., query for "permanent roof load" returns file contents)
  **Done when:** Agent server starts without errors and query returns relevant file contents with source file paths

- [ ] 7.2 Run frontend server and verify "what do you know?" question returns knowledge summary
  **Done when:** Frontend chat responds with overview of knowledge base and list of subdirectories

- [ ] 7.3 Run lint and typecheck on agent code: `cd agent && python -m ruff check . && python -m mypy .`
  **Done when:** Both commands exit with zero exit code and no errors reported
