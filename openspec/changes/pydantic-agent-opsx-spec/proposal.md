## Why

The pydantic-ai agent in `agent/src/agent.py` defines the entire LLM-backed truss engineering assistant — model configuration, data models, backend tools, system prompt, and ASGI wiring — in a single 521-line file. We need an OpenSpec spec that, when applied via `opsx-apply`, recreates this agent's behavior idempotently. This allows the agent to be re-provisioned from specs alone, supports repeatable demo deployments, and provides a reset mechanism so the spec can be rerun without side effects.

## What Changes

- Create a new OpenSpec spec that encodes the full agent implementation as executable tasks
- Each task creates or verifies a discrete slice of the agent: model/provider, data models, tools, system prompt, ASGI entry point
- All tasks are idempotent: re-running on an already-complete codebase is a no-op
- A final task unchecks all task checkboxes and resets the spec state, enabling infinite re-runs

## Capabilities

### New Capabilities

- `agent-model-and-app`: DeepSeek model/provider setup, ASGI app entry point via `agent.to_ag_ui()`, uvicorn configuration, health check route
- `agent-state-models`: Pydantic data models — `KnowledgeQuery`, `DesignParameters`, `DesignEntry`, `YourState`, `StateDeps` — with strict typing per PEP 8
- `agent-knowledge-tools`: Backend tools `query_knowledge_base` (keyword-scoring search across 33 project subdirectories) and `get_knowledge_summary` (returns summary.md index)
- `agent-pricing-tool`: Backend tool `generate_quote` with deterministic CZK-to-EUR pricing formula including roof-type factors
- `agent-system-prompt`: Full system prompt content, agent instantiation with `Agent()`, and tool registration wiring
- `agent-idempotent-reset`: Final task that unchecks all task checkboxes in the change's `tasks.md`, enabling repeated `opsx-apply` cycles

### Modified Capabilities

(None — this is a net-new spec)

## Impact

- **Files created/verified**: `agent/src/agent.py`, `agent/src/main.py`
- **Dependencies**: pydantic-ai, fastapi/uvicorn, logfire, python-dotenv, httpx, OpenAI-compatible API access (DeepSeek via `OPENAI_API_KEY`)
- **Knowledge base**: Read-only dependency on `agent/knowledge/trusses-ai-english/` directory (33 project subdirectories)
- **No API changes**: Frontend tools (`generate_design`, `modify_design_entry`, `update_design_parameters`, `reset_design`) remain registered in Next.js frontend — only backend tools and agent wiring are in scope
