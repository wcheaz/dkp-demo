## 1. Foundation — Imports, Constants, and Model

- [ ] **1.1 Write imports, constants, and environment loading to agent.py**
  - Scope: `agent/src/agent.py`
  - Change: File is created (or replaced) with all import statements, `KNOWLEDGE_BASE_DIR` constant, and `load_dotenv()` call between `# --- AGENT_SPEC: BEGIN IMPORTS ---` / `# --- AGENT_SPEC: END IMPORTS ---` sentinels.
  - Done when:
    - `agent/src/agent.py` exists and contains `# --- AGENT_SPEC: BEGIN IMPORTS ---`
    - `rg "KNOWLEDGE_BASE_DIR" agent/src/agent.py` returns a match
    - `rg "from pydantic_ai import Agent" agent/src/agent.py` returns a match
    - `rg "from dotenv import load_dotenv" agent/src/agent.py` returns a match
  - Stop and hand off if: `agent/src/agent.py` is locked or not writable.

- [ ] **1.2 Write DeepSeekModel class to agent.py**
  - Scope: `agent/src/agent.py`
  - Change: `DeepSeekModel` class (subclassing `OpenAIModel`) with `_ensure_thinking_parts()`, `request()`, and `request_stream()` is written between `# --- AGENT_SPEC: BEGIN MODEL_CLASS ---` / `# --- AGENT_SPEC: END MODEL_CLASS ---` sentinels.
  - Done when:
    - `rg "class DeepSeekModel" agent/src/agent.py` returns a match
    - `rg "_ensure_thinking_parts" agent/src/agent.py` returns a match
    - `python -c "from src.agent import DeepSeekModel"` exits 0 when run from `agent/`
  - Stop and hand off if: `OpenAIModel` or `ThinkingPart` imports are not available in the installed pydantic-ai version.

- [ ] **1.3 Write model instantiation to agent.py**
  - Scope: `agent/src/agent.py`
  - Change: Module-level `model = DeepSeekModel(...)` with `DeepSeekProvider` is written between `# --- AGENT_SPEC: BEGIN MODEL_INSTANCE ---` / `# --- AGENT_SPEC: END MODEL_INSTANCE ---` sentinels.
  - Done when:
    - `rg "^model = DeepSeekModel" agent/src/agent.py` returns a match
    - `rg "DeepSeekProvider" agent/src/agent.py` returns a match
  - Stop and hand off if: `DeepSeekProvider` is not importable from `pydantic_ai.providers.deepseek`.

## 2. Data Models

- [ ] **2.1 Write Pydantic data models to agent.py**
  - Scope: `agent/src/agent.py`
  - Change: `KnowledgeQuery`, `DesignParameters`, `DesignEntry`, `YourState`, and `StateDeps` classes are written between `# --- AGENT_SPEC: BEGIN DATA_MODELS ---` / `# --- AGENT_SPEC: END DATA_MODELS ---` sentinels.
  - Done when:
    - `rg "class KnowledgeQuery" agent/src/agent.py` returns a match
    - `rg "class DesignParameters" agent/src/agent.py` returns a match
    - `rg "class DesignEntry" agent/src/agent.py` returns a match
    - `rg "class YourState" agent/src/agent.py` returns a match
    - `rg "class StateDeps" agent/src/agent.py` returns a match
    - `python -c "from src.agent import YourState, StateDeps, DesignParameters, DesignEntry, KnowledgeQuery"` exits 0 when run from `agent/`
  - Stop and hand off if: Pydantic `BaseModel` is not importable.

## 3. Agent Instance and System Prompt

- [ ] **3.1 Write agent instantiation with full system prompt to agent.py**
  - Scope: `agent/src/agent.py`
  - Change: `agent = Agent(model, deps_type=StateDeps, system_prompt=(...))` with the complete system prompt string is written between `# --- AGENT_SPEC: BEGIN AGENT_INSTANCE ---` / `# --- AGENT_SPEC: END AGENT_INSTANCE ---` sentinels.
  - Done when:
    - `rg "^agent = Agent" agent/src/agent.py` returns a match
    - `rg "ABSOLUTE RULE" agent/src/agent.py` returns a match
    - `rg "COLLECTION LOOP INSTRUCTIONS" agent/src/agent.py` returns a match
    - `rg "OUTPUT STYLE" agent/src/agent.py` returns a match
    - `python -c "from src.agent import agent; assert agent.deps_type is not None"` exits 0 when run from `agent/`
  - Stop and hand off if: Agent constructor signature has changed in the installed pydantic-ai version.

## 4. Backend Tools

- [ ] **4.1 Write generate_quote tool to agent.py**
  - Scope: `agent/src/agent.py`
  - Change: The `generate_quote` async tool function with deterministic CZK-to-EUR pricing formula and roof-type factors is written between `# --- AGENT_SPEC: BEGIN TOOL_QUOTE ---` / `# --- AGENT_SPEC: END TOOL_QUOTE ---` sentinels.
  - Done when:
    - `rg "async def generate_quote" agent/src/agent.py` returns a match
    - `rg "roof_type_factors" agent/src/agent.py` returns a match
    - `rg "total_eur = round\(total_czk / 25\)" agent/src/agent.py` returns a match
    - `python -c "from src.agent import generate_quote"` exits 0 when run from `agent/`
  - Stop and hand off if: `re` module import is missing from the imports section.

- [ ] **4.2 Write query_knowledge_base tool to agent.py**
  - Scope: `agent/src/agent.py`
  - Change: The `query_knowledge_base` async tool function with keyword-scoring search across `KNOWLEDGE_BASE_DIR` subdirectories is written between `# --- AGENT_SPEC: BEGIN TOOL_KB ---` / `# --- AGENT_SPEC: END TOOL_KB ---` sentinels.
  - Done when:
    - `rg "async def query_knowledge_base" agent/src/agent.py` returns a match
    - `rg "scored\.sort\(key=lambda" agent/src/agent.py` returns a match
    - `python -c "from src.agent import query_knowledge_base"` exits 0 when run from `agent/`
  - Stop and hand off if: `KNOWLEDGE_BASE_DIR` constant is not defined in the file.

- [ ] **4.3 Write get_knowledge_summary tool to agent.py**
  - Scope: `agent/src/agent.py`
  - Change: The `get_knowledge_summary` async tool function that reads `summary.md` is written between `# --- AGENT_SPEC: BEGIN TOOL_SUMMARY ---` / `# --- AGENT_SPEC: END TOOL_SUMMARY ---` sentinels.
  - Done when:
    - `rg "async def get_knowledge_summary" agent/src/agent.py` returns a match
    - `python -c "from src.agent import get_knowledge_summary"` exits 0 when run from `agent/`
  - Stop and hand off if: tool decorator conflicts with existing registered tool names.

## 5. ASGI Entry Point

- [ ] **5.1 Write ASGI app entry point to main.py**
  - Scope: `agent/src/main.py`
  - Change: `main.py` is created (or replaced) with Logfire configuration, AG-UI app creation via `agent.to_ag_ui()`, `/api/health` route, and uvicorn runner.
  - Done when:
    - `rg "agent\.to_ag_ui" agent/src/main.py` returns a match
    - `rg "/api/health" agent/src/main.py` returns a match
    - `rg "logfire\.configure" agent/src/main.py` returns a match
    - `python -c "from src.main import app"` exits 0 when run from `agent/`
  - Stop and hand off if: `agent.to_ag_ui` method does not exist in the installed pydantic-ai version.

## 6. Integrated Verification

- [ ] **6.1 Verify full agent module imports and all tools are registered**
  - Scope: `agent/src/agent.py`, `agent/src/main.py`
  - Change: No code changes. Confirms the assembled file imports cleanly and all three backend tools are registered on the agent.
  - Done when:
    - `python -c "from src.agent import agent; names = [t.name for t in agent.tool_functions]; assert 'generate_quote' in names; assert 'query_knowledge_base' in names; assert 'get_knowledge_summary' in names"` exits 0 when run from `agent/`
    - `python -c "from src.agent import DeepSeekModel, model, YourState, StateDeps, KnowledgeQuery, DesignParameters, DesignEntry, agent, generate_quote, query_knowledge_base, get_knowledge_summary"` exits 0 when run from `agent/`
    - `python -c "from src.main import app, health_check"` exits 0 when run from `agent/`
  - Stop and hand off if: any import fails — re-examine the corresponding sentinel section for syntax or dependency errors.

## 7. Idempotent Reset

- [ ] **7.1 Uncheck all task checkboxes in tasks.md for re-run**
  - Scope: `openspec/changes/pydantic-agent-opsx-spec/tasks.md`
  - Change: Replace every `- [x]` with `- [ ]` in this file, enabling the spec to be re-applied from a clean state.
  - Done when:
    - `rg "\- \[x\]" openspec/changes/pydantic-agent-opsx-spec/tasks.md` returns no matches
    - `rg "\- \[ \]" openspec/changes/pydantic-agent-opsx-spec/tasks.md` returns at least 10 matches
  - Stop and hand off if: `tasks.md` file is not writable or does not exist.
