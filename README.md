# AG-UI App Template

A PydanticAI + CopilotKit application template.

This is a generic, customizable application template providing only the core infrastructure:
- CopilotKit frontend UI
- PydanticAI agent framework
- Deployment pipeline (Docker + Kubernetes)

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- OpenAI API Key (or DeepSeek API Key)
- `uv` (Python package manager) - optional but recommended

### Installation

1. Install dependencies:
```bash
# Using pnpm (recommended)
pnpm install

# Using npm
npm install
```

This will automatically install both Node.js and Python dependencies.

2. Configure environment:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# For OpenAI:
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# For DeepSeek (OpenAI-compatible):
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

3. Start development:
```bash
# Using pnpm
pnpm dev

# Using npm
npm run dev
```

This will start both the Next.js UI (http://localhost:3000) and the PydanticAI agent (http://localhost:3000) concurrently.

## Project Structure

```
{{PROJECT_NAME}}/
├── src/                    # Next.js frontend
│   ├── app/               # Next.js app directory
│   │   ├── page.tsx      # Main CopilotKit page
│   │   └── layout.tsx    # App layout
│   ├── components/       # React components
│   │   └── your-component.tsx  # Your main component (customize this)
│   └── lib/              # Utility functions and types
│       └── types.ts      # TypeScript types
├── agent/                # PydanticAI backend
│   ├── src/
│   │   ├── agent.py      # Main agent logic (customize this)
│   │   └── main.py       # Agent server entry point
│   ├── rag/              # RAG implementation (optional)
│   └── pyproject.toml   # Python dependencies
├── k8s/                  # Kubernetes deployment configs
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── deploy_scripts/      # Deployment automation scripts
│   └── deploy-all.sh    # Full deployment script
└── package.json         # Node.js dependencies
```

## Customization

### Frontend Customization

**Main UI**: `src/app/page.tsx`
- Update the sidebar title and initial message
- Customize the suggestions
- Modify the file upload functionality
- Add/remove frontend tools

**Main Component**: `src/components/your-component.tsx`
- Replace this with your specific application UI
- Implement your domain-specific display logic
- Add export functionality as needed

**State Management**: `src/lib/types.ts`
- Define your application state structure
- Ensure it aligns with your agent's state

### Backend Customization

**Agent Logic**: `agent/src/agent.py`
- Update the system prompt
- Define your tools and functions
- Implement domain-specific logic
- Add state management as needed

**Model Configuration**: Edit environment variables in `.env`
- Change the AI model
- Adjust API settings
- Configure other agent parameters

### Deployment Customization

**Docker**: `Dockerfile` and `docker-compose.yml`
- Adjust container configurations
- Add dependencies as needed

**Kubernetes**: `k8s/*.yaml`
- Update resource limits
- Configure ingress settings
- Add environment variables and secrets

## Available Scripts

- `dev` - Start both UI and agent servers in development mode
- `dev:debug` - Start with debug logging enabled
- `dev:ui` - Start only the Next.js UI server
- `dev:agent` - Start only the PydanticAI agent server
- `build` - Build the Next.js application for production
- `start` - Start the production server
- `lint` - Run ESLint for code linting
- `install:agent` - Install Python dependencies for the agent

## Deployment

### Local Development

The development servers run on:
- UI: http://localhost:3000
- Agent: http://localhost:3000 (integrated)

### Kubernetes Configuration

Before deploying to Kubernetes, you must replace the placeholder values in the manifest files:

- `{{PROJECT_NAME}}` — Your project identifier (e.g., `my-app`)
- `{{APP_HOSTNAME}}` — Your application hostname (e.g., `app.example.com`)
- `{{REGISTRY_HOST}}` — Your container registry (e.g., `localhost:32000` or `registry.example.com`)

These placeholders appear in: `k8s/deployment.yaml`, `k8s/service.yaml`, `k8s/ingress.yaml`, `k8s/agent-deployment.yaml`, `k8s/secrets.yaml`, and deployment scripts.

The project includes automated deployment scripts using Multipass and Microk8s:

```bash
# Full deployment (recommended)
./deploy_scripts/deploy-all.sh

# Individual deployment steps
./deploy_scripts/build-docker-image.sh
./deploy_scripts/tag-docker-image.sh
./deploy_scripts/setup-microk8s-registry.sh
./deploy_scripts/push-docker-image.sh
./deploy_scripts/deploy-to-k8s.sh
```

See the deployment scripts in `deploy_scripts/` and `scripts/` for detailed deployment instructions and troubleshooting.

## Architecture

### Frontend Stack
- **Next.js 16** - React framework
- **CopilotKit** - AI integration framework
- **React 19** - UI library
- **Tailwind CSS** - Styling

### Backend Stack
- **PydanticAI** - AI agent framework
- **FastAPI** (via Starlette) - Web framework
- **OpenAI API** - AI model provider (or compatible)

### Deployment Stack
- **Docker** - Containerization
- **Kubernetes (Microk8s)** - Orchestration
- **Multipass** - VM management

## Next Steps

1. **Customize the agent** in `agent/src/agent.py`
2. **Update the UI** in `src/app/page.tsx` and `src/components/your-component.tsx`
3. **Configure state** in `src/lib/types.ts` and `agent/src/agent.py`
4. **Test and iterate** with your specific domain logic
5. **Deploy** using the provided scripts when ready

## Troubleshooting

### Agent Connection Issues
If you see "I'm having trouble connecting to my tools":
1. Ensure the PydanticAI agent is running on port 3000
2. Check your API key is set correctly in `.env`
3. Verify both servers started successfully

### Python Dependencies
If you encounter Python import errors:
```bash
cd agent
uv sync
uv run src/main.py
```

### File Upload Issues
If file uploads aren't working:
1. Check file size limits (max 2MB)
2. Ensure file formats are supported (.txt, .csv, .xlsx, .xls, .xml)
3. Verify browser console for errors

## Documentation

- [PydanticAI Documentation](https://ai.pydantic.dev)
- [CopilotKit Documentation](https://docs.copilotkit.ai)
- [Next.js Documentation](https://nextjs.org/docs)

## License

This project is licensed under the MIT License.

## Acknowledgments

This project was originally forked from [my-ag-ui-app](https://github.com/nichochar/my-ag-ui-app) and has been genericized into a reusable template. Domain-specific logic has been commented out as reference examples, with placeholders replacing hardcoded project values for easy customization.