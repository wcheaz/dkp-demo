## Context

The agent is a single-file PydanticAI application (`agent/src/agent.py`, 521 lines) backed by an ASGI entry point (`agent/src/main.py`, 24 lines). It uses a DeepSeek LLM model, defines three backend tools (`generate_quote`, `query_knowledge_base`, `get_knowledge_summary`), and exposes an AG-UI endpoint for the CopilotKit frontend. The knowledge base at `agent/knowledge/trusses-ai-english/` contains 33 project subdirectories with markdown documents. The goal is to encode this agent as an OpenSpec spec whose tasks, when applied via `opsx-apply`, reproduce the agent idempotently — and reset themselves afterward so the spec can be rerun.

## Goals / Non-Goals

**Goals:**
- Encode every structural component of the agent as a discrete, idempotent task in the spec
- Each task must be verifiable by a focused check (file exists, import resolves, function signature matches, tool is registered)
- A final task unchecks all task checkboxes so the spec can be reapplied without manual reset
- Preserve exact behavioral parity with the existing `agent/src/agent.py` and `agent/src/main.py`

**Non-Goals:**
- Modifying the frontend tools (`generate_design`, `modify_design_entry`, `update_design_parameters`, `reset_design`) — those remain in Next.js
- Adding new agent capabilities beyond what exists
- Testing the LLM conversation flow end-to-end (that requires a live API key and model access)
- Changing the Docker deployment configuration

## Decisions

### D1: Task ordering follows dependency graph

Tasks are ordered so that each task's code can be imported without missing dependencies:

1. Imports and constants (`KNOWLEDGE_BASE_DIR`, `load_dotenv`)
2. `DeepSeekModel` class (subclasses `OpenAIModel`)
3. Model instantiation (`model = DeepSeekModel(...)`)
4. Data models (`KnowledgeQuery`, `DesignParameters`, `DesignEntry`, `YourState`, `StateDeps`)
5. Agent instantiation with system prompt
6. Backend tools (`generate_quote`, `query_knowledge_base`, `get_knowledge_summary`)
7. ASGI entry point (`main.py`)
8. Reset task (unchecks all checkboxes)

**Rationale:** Python files are import-sensitive to declaration order. Since all code lands in two files, tasks must produce code in the correct sequence. Each task appends or replaces a delimited section within the file.

**Alternative considered:** One task per file with separate modules. Rejected because the existing agent is a single file and splitting it would change the import structure and break `main.py`'s `from src.agent import ...`.

### D2: Idempotency via section markers

Each task writes code between uniquely-named sentinel comments (e.g., `# --- BEGIN IMPORTS ---` / `# --- END IMPORTS ---`). On re-run, the task replaces the content between its markers. If markers already exist with correct content, the task is a no-op.

**Rationale:** Simple, grep-verifiable, no external state tracking needed.

**Alternative considered:** Checksum comparison. Rejected — adds complexity for no practical benefit since the sentinel approach is sufficient and directly observable.

### D3: Reset task rewrites `tasks.md` with all checkboxes unchecked

The final task reads `tasks.md`, replaces every `- [x]` with `- [ ]`, and writes the file back. This is a pure file transformation with no code side effects.

**Rationale:** The only reliable way to reset OpenSpec task state is to modify the `tasks.md` file directly. The task must NOT uncheck itself during execution — it only unchecks after the `opsx-apply` session completes (the file rewrite is the last action).

**Alternative considered:** A separate script. Rejected — keeping it as a task in the same `tasks.md` ensures the reset always travels with the spec.

### D4: Verification uses `python -c` import checks and `rg` structural assertions

Each task's `Done when` clause verifies:
- The relevant class/function can be imported: `python -c "from src.agent import ClassName"` from `agent/`
- Structural markers exist: `rg "BEGIN <SECTION>" agent/src/agent.py`

**Rationale:** These checks are fast, deterministic, and do not require a running server or API key.

### D5: Single target files — `agent/src/agent.py` and `agent/src/main.py`

All tasks write to exactly these two files. No new files are created.

**Rationale:** Matches the existing project structure. Avoids import path changes.

## Risks / Trade-offs

- **[Sentinel marker collision]** → Mitigation: markers use a unique prefix `# --- AGENT_SPEC:` to avoid colliding with existing comments. If the file is manually edited and markers are removed, the task will re-insert them.
- **[Reset task unchecks itself]** → Mitigation: the reset task is the last task in the list. When `opsx-apply` finishes processing it, the file is already rewritten. On the next run, all tasks (including reset) start unchecked — which is the desired state.
- **[File overwrite on first run]** → Mitigation: the first task creates `agent.py` from scratch (or replaces the existing file). Since the spec's purpose is to recreate the agent, this is intentional. The original file is already in git.
- **[No runtime verification]** → Accepted trade-off. Verifying that the agent actually responds to LLM calls requires a live DeepSeek API key and is outside the scope of an idempotent spec.
