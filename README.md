# dkp-demo

A truss and roof engineering AI assistant powered by PydanticAI and CopilotKit. The agent has access to a knowledge base of 33 construction projects designed by medop strechy s.r.o. and can answer technical questions about truss designs, load calculations, materials, and engineering specifications. The frontend includes a design gallery where the AI agent can create and modify design entries with images and prompt text.

## Features

- **Knowledge Base Queries** — Ask general or specific questions about truss/roof engineering projects and receive sourced answers from 33 project documents.
- **Design Gallery** — The agent automatically creates design entries for each response. Users can click images to enlarge them in a modal overlay.
- **Design Modification** — The agent can modify existing design entries (image and/or prompt text) via the `modify_design_entry` tool.
- **File Upload** — Attach CSV, Excel, text, or XML files to messages as context for the agent.
- **Kubernetes Deployment** — Full Docker + Kubernetes (MicroK8s) deployment pipeline included.

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- `uv` (Python package manager) — optional but recommended
- OpenAI API key (or compatible endpoint like DeepSeek)

### Installation

1. Install Node.js dependencies:

   ```bash
   npm install
   ```

   This automatically runs `npm run install:agent` via the `postinstall` hook, which sets up the Python agent environment.

2. Configure environment:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set at minimum:

   ```bash
   OPENAI_API_KEY=sk-your-key
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4
   ```

3. Populate the knowledge base (required for document queries):
   The agent reads documents from `agent/knowledge/trusses-ai-english/`. This directory must contain a `summary.md` and project subdirectories with markdown files. The `agent/knowledge/` directory is gitignored — populate it separately.

### Development

```bash
npm run dev
```

Starts both the Next.js UI and PydanticAI agent concurrently:

- **UI**: <http://localhost:3000>
- **Agent**: <http://localhost:3000> (integrated via AG-UI protocol)

Individual services:

```bash
npm run dev:ui      # Next.js UI only
npm run dev:agent   # PydanticAI agent only
npm run dev:debug   # Both with debug logging
```

### Production Build

```bash
npm run build
npm run start
```

### Docker

```bash
docker-compose up --build
```

Services:

- **Frontend**: <http://localhost:3001>
- **Agent**: <http://localhost:8000>

## Architecture

### System Overview

```text
Browser
  └── Next.js (CopilotKit)
        ├── CopilotKit runtime → proxies to AG-UI agent
        ├── Frontend tools (add_design_entry, modify_design_entry, setThemeColor)
        └── Shared state (AgentState via useCoAgent)
              │
              ▼
        PydanticAI Agent (FastAPI/Starlette)
              ├── Backend tools: query_knowledge_base, get_knowledge_summary
              ├── OpenAI-compatible LLM (configurable model/endpoint)
              └── File-based knowledge base (agent/knowledge/trusses-ai-english/)
```

### Frontend Stack

| Layer          | Technology                                                                   | Purpose                                            |
| -------------- | ---------------------------------------------------------------------------- | -------------------------------------------------- |
| Framework      | Next.js 16 (App Router, Turbopack)                                           | Server-side rendering, API routing                 |
| AI Integration | CopilotKit (`@copilotkit/react-core`, `@copilotkit/react-ui`)                | Chat sidebar, frontend tools, shared state         |
| UI             | React 19, Tailwind CSS 4                                                     | Component rendering, styling                       |
| File Parsing   | PapaParse, SheetJS (xlsx)                                                    | CSV and Excel file upload handling                 |

**Key frontend files:**

- `src/app/layout.tsx` — Root layout wrapping the app in `<CopilotKit>` provider.
- `src/app/page.tsx` — Main page with `CopilotSidebar`, `YourMainContent`, and `CustomInput`. Registers frontend tools (`add_design_entry`, `modify_design_entry`, `setThemeColor`) via `useFrontendTool`.
- `src/components/design-component.tsx` — Renders the scrollable design gallery with image modal enlargement.
- `src/components/add-design-button.tsx` — Dev-only button to append test design entries.
- `src/lib/types.ts` — TypeScript types: `AgentState` (shared state), `DesignEntry` (id, imageUrl, promptText).

### Backend Stack

| Layer           | Technology            | Purpose                                                           |
| --------------- | --------------------- | ----------------------------------------------------------------- |
| Agent Framework | PydanticAI            | Tool registration, system prompts, result validation              |
| Web Server      | Starlette/Uvicorn     | HTTP server, AG-UI protocol endpoint                              |
| Observability   | Logfire               | Request tracing, instrumentation                                  |
| LLM             | OpenAI-compatible API | Chat completions (OpenAI, DeepSeek, etc.)                         |

**Key backend files:**

- `agent/src/main.py` — Entry point. Creates the AG-UI app from the agent with `StateDeps(state=YourState())`, adds a `/api/health` endpoint, and runs Uvicorn.
- `agent/src/agent.py` — Core agent logic:
  - `YourState` (Pydantic model): shared state with `user_input`, `ai_response`, `designs`, `knowledge_queries`, `last_knowledge_result`.
  - `StateDeps`: dependency injection wrapper around `YourState`.
  - Agent configured with OpenAI model, system prompt, and two backend tools.
  - `query_knowledge_base` tool: keyword-matches subdirectories via `summary.md`, reads markdown files from up to 3 matched subdirectories, returns content with source paths.
  - `get_knowledge_summary` tool: returns the full `summary.md` content.
  - `add_design_entry`: commented-out backend version (frontend tool used instead).

### Agent ↔ Frontend Communication

1. **CopilotKit runtime** proxies chat messages to the PydanticAI agent via the AG-UI protocol.
1. **Shared state** (`AgentState`) is synchronized bidirectionally through `useCoAgent`:
   - Frontend reads `state.designs` to render the gallery.
   - Frontend tools (`add_design_entry`, `modify_design_entry`) write to state via `setState`.
   - Agent state (`knowledge_queries`, `last_knowledge_result`) tracks backend query history.
1. **Frontend tools** are registered in the browser but callable by the agent — the agent decides when to call them, and the handler runs client-side to update React state.

### Knowledge Base

- **Location**: `agent/knowledge/trusses-ai-english/` (gitignored)
- **Structure**: 33 project subdirectories (e.g., `001IK26A - Matlúch_House/`), each containing markdown files extracted from engineering PDFs.
- **Summary**: `summary.md` at the root provides an overview table of all subdirectories, descriptions, and key topics.
- **Query flow**: Agent reads `summary.md` to identify relevant subdirectories by keyword matching, then reads markdown files from matched directories.

### Deployment

#### Kubernetes (MicroK8s)

Before deploying, replace placeholders in `k8s/*.yaml`:

- `{{PROJECT_NAME}}` — project identifier
- `{{APP_HOSTNAME}}` — application hostname
- `{{REGISTRY_HOST}}` — container registry host

```bash
./scripts/deploy/build-docker-image.sh
./scripts/deploy/tag-docker-image.sh
./scripts/deploy/setup-microk8s-registry.sh
./scripts/deploy/push-docker-image.sh
./scripts/deploy/deploy-to-k8s.sh
```

Additional helper scripts:

```bash
./scripts/deploy/common.sh                # Shared variables and utilities sourced by other scripts
./scripts/deploy/setup-k8s-secrets.sh     # Configure Kubernetes secrets
./scripts/deploy/setup-secrets.sh         # Generate and apply secrets YAML
./scripts/deploy/export_agent.sh          # Export agent artifacts for deployment
./scripts/deploy/cleanup-resources.sh     # Remove deployed resources and clean up
```

K8s manifests in `k8s/`:

- `deployment.yaml`, `service.yaml`, `ingress.yaml` — frontend
- `agent-deployment.yaml`, `agent-service.yaml` — agent
- `secrets.yaml` — secrets manifest (generated by `scripts/deploy/setup-secrets.sh`)

### Available Scripts

| Script                  | Description                           |
| ----------------------- | ------------------------------------- |
| `npm run dev`           | Start UI + agent concurrently         |
| `npm run dev:debug`     | Start with debug logging              |
| `npm run dev:ui`        | Next.js UI only                       |
| `npm run dev:agent`     | PydanticAI agent only                 |
| `npm run build`         | Build Next.js for production          |
| `npm run start`         | Start production server               |
| `npm run lint`          | ESLint                                |
| `npm run install:agent` | Install Python agent dependencies     |
