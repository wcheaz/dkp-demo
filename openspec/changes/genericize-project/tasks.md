# File Placement Guidelines (PROJECT-SPECIFIC - Adjust as Needed)

## Overview

These guidelines help organize test and documentation files. Adjust them based on your project structure.

## Test Files

**Recommended Placement** (adjust for your project):
- **Standard**: `test/` directory at project root
- **Alternative**: `tests/`, `__tests__/`, or test directories alongside source code
- **For Python projects**: Often use `tests/` or `test/` at root
- **For TypeScript/Node.js**: Often use `__tests__/` alongside source files or `test/` at root

**File Patterns** (common conventions):
- Unit tests: `test_*.py`, `*_test.py`, `*.test.ts`, `*.test.tsx`
- Integration tests: `test_*.py`, `*.integration.test.ts`
- E2E tests: `*.e2e.test.ts`, `*.e2e.py`
- Debug/verification: `debug_*.py`, `check_*.py`, `verify_*.py`
- Performance: `performance_*.py`, `measure_*.py`

**Naming Examples** (adapt to your conventions):
- `test/component_name.test.tsx` → React component tests
- `test_module.py` → Python module tests
- `check_deployment.sh` → Deployment verification script

## Documentation Files

**Recommended Placement** (adjust for your project):
- **Temporary/Generated**: `ralph-docs/` directory at project root (gitignored)
- **Permanent**: `docs/` directory at project root
- **Change-specific**: Within the change directory itself

**Core Documentation Files** (these go at project root, NOT in docs directories):
- `README.md`
- `CHANGELOG.md`
- `SETUP.md`
- `TESTING.md`
- `DEPENDENCIES.md`
- `DEPLOYMENT.md`

**Examples**:
- Generated deployment summary: `ralph-docs/DEPLOYMENT_SUMMARY.md`
- Permanent API documentation: `docs/api.md`
- Change-specific notes: `openspec/changes/<change-name>/IMPLEMENTATION_NOTES.md`

## Project-Specific Notes for dkp-demo

This project currently uses:
- **No dedicated test directory** (tests may be added later)
- **ralph-docs** directory for temporary/generated documentation (gitignored)
- **test/kubernetes/** for Kubernetes test scripts (gitignored)

If you create a test suite, choose a directory structure and add it to these guidelines.

---

## 1. Backup Creation

- [x] 1.1 Create `.backup/` directory at project root — ensure directory exists and is writable. Verify by running `mkdir -p .backup` and checking that `.backup/` directory exists with `ls -la | grep backup`.
- [x] 1.2 Create directory structure in `.backup/agent/` for agent files — ensure backup directory hierarchy exists. Verify by running `mkdir -p .backup/agent && ls -la .backup/agent` to confirm directory exists.
- [x] 1.3 Create directory structure in `.backup/src/` for frontend files — ensure backup directory hierarchy exists. Verify by running `mkdir -p .backup/src/components && mkdir -p .backup/src/lib && mkdir -p .backup/src/app && ls -la .backup/src` to confirm directories exist.
- [x] 1.4 Create directory structure in `.backup/k8s/` for Kubernetes manifests — ensure backup directory hierarchy exists. Verify by running `mkdir -p .backup/k8s && ls -la .backup/k8s` to confirm directory exists.
- [x] 1.5 Create directory structure in `.backup/deploy_scripts/` for deployment scripts — ensure backup directory hierarchy exists. Verify by running `mkdir -p .backup/deploy_scripts && ls -la .backup/deploy_scripts` to confirm directory exists.
- [x] 1.6 Copy `agent/src/agent.py` to `.backup/agent/src/agent.py` — create backup of agent implementation. Verify by running `diff agent/src/agent.py .backup/agent/src/agent.py` (should show no differences).
- [x] 1.7 Copy `agent/src/agent_template.py` to `.backup/agent/src/agent_template.py` — create backup of agent template. Verify by running `diff agent/src/agent_template.py .backup/agent/src/agent_template.py` (should show no differences).
- [x] 1.8 Copy `agent/src/main.py` to `.backup/agent/src/main.py` — create backup of agent entry point. Verify by running `diff agent/src/main.py .backup/agent/src/main.py` (should show no differences).
- [x] 1.9 Copy `agent/pyproject.toml` to `.backup/agent/pyproject.toml` — create backup of agent configuration. Verify by running `diff agent/pyproject.toml .backup/agent/pyproject.toml` (should show no differences).
- [x] 1.10 Copy `src/components/procurement-codes.tsx` to `.backup/src/components/procurement-codes.tsx` — create backup of procurement component. Verify by running `diff src/components/procurement-codes.tsx .backup/src/components/procurement-codes.tsx` (should show no differences).
- [x] 1.11 Copy `src/components/your-component.tsx` to `.backup/src/components/your-component.tsx` — create backup of main component. Verify by running `diff src/components/your-component.tsx .backup/src/components/your-component.tsx` (should show no differences).
- [x] 1.12 Copy `src/lib/types.ts` to `.backup/src/lib/types.ts` — create backup of type definitions. Verify by running `diff src/lib/types.ts .backup/src/lib/types.ts` (should show no differences).
- [x] 1.13 Copy `src/app/page.tsx` to `.backup/src/app/page.tsx` — create backup of main page. Verify by running `diff src/app/page.tsx .backup/src/app/page.tsx` (should show no differences).
- [x] 1.14 Copy `k8s/deployment.yaml` to `.backup/k8s/deployment.yaml` — create backup of deployment manifest. Verify by running `diff k8s/deployment.yaml .backup/k8s/deployment.yaml` (should show no differences).
- [x] 1.15 Copy `k8s/service.yaml` to `.backup/k8s/service.yaml` — create backup of service manifest. Verify by running `diff k8s/service.yaml .backup/k8s/service.yaml` (should show no differences).
- [x] 1.16 Copy `k8s/ingress.yaml` to `.backup/k8s/ingress.yaml` — create backup of ingress manifest. Verify by running `diff k8s/ingress.yaml .backup/k8s/ingress.yaml` (should show no differences).
- [x] 1.17 Copy `k8s/agent-deployment.yaml` to `.backup/k8s/agent-deployment.yaml` — create backup of agent deployment manifest. Verify by running `diff k8s/agent-deployment.yaml .backup/k8s/agent-deployment.yaml` (should show no differences).
- [x] 1.18 Copy `k8s/secrets.yaml` to `.backup/k8s/secrets.yaml` — create backup of secrets manifest. Verify by running `diff k8s/secrets.yaml .backup/k8s/secrets.yaml` (should show no differences).
- [x] 1.19 Copy `deploy_scripts/common.sh` to `.backup/deploy_scripts/common.sh` — create backup of deployment script. Verify by running `diff deploy_scripts/common.sh .backup/deploy_scripts/common.sh` (should show no differences).
- [x] 1.20 Create directory structure in `.backup/scripts/` for scripts — ensure backup directory hierarchy exists. Verify by running `mkdir -p .backup/scripts && ls -la .backup/scripts` to confirm directory exists.
- [x] 1.21 Copy `scripts/kubernetes-deployment-setup.sh` to `.backup/scripts/kubernetes-deployment-setup.sh` — create backup of Kubernetes deployment script. Verify by running `diff scripts/kubernetes-deployment-setup.sh .backup/scripts/kubernetes-deployment-setup.sh` (should show no differences).
- [x] 1.22 Copy `scripts/run-agent.sh` to `.backup/scripts/run-agent.sh` — create backup of agent runner script. Verify by running `diff scripts/run-agent.sh .backup/scripts/run-agent.sh` (should show no differences).
- [x] 1.23 Copy `scripts/run-agent-prod.sh` to `.backup/scripts/run-agent-prod.sh` — create backup of production agent runner script. Verify by running `diff scripts/run-agent-prod.sh .backup/scripts/run-agent-prod.sh` (should show no differences).
- [x] 1.24 Copy `scripts/setup-agent.sh` to `.backup/scripts/setup-agent.sh` — create backup of agent setup script. Verify by running `diff scripts/setup-agent.sh .backup/scripts/setup-agent.sh` (should show no differences).
- [x] 1.25 Copy `scripts/setup-vm-docker.sh` to `.backup/scripts/setup-vm-docker.sh` — create backup of VM Docker setup script. Verify by running `diff scripts/setup-vm-docker.sh .backup/scripts/setup-vm-docker.sh` (should show no differences).
- [x] 1.26 Verify all backups exist and are readable — confirm every backup file exists and can be read. Verify by running `find .backup -type f -exec test -r {} \;` and confirming no errors.
- [x] 1.27 Verify backups match original files — confirm all backup files match their originals using diff. Verify by running `diff agent/src/agent.py .backup/agent/src/agent.py && diff agent/src/agent_template.py .backup/agent/src/agent_template.py && diff agent/src/main.py .backup/agent/src/main.py && echo "All agent backups match originals"`.
- [x] 1.28 Verify remaining backups match originals — confirm frontend, Kubernetes, and scripts backups match their originals. Verify by running `diff src/components/procurement-codes.tsx .backup/src/components/procurement-codes.tsx && diff src/app/page.tsx .backup/src/app/page.tsx && diff k8s/deployment.yaml .backup/k8s/deployment.yaml && diff scripts/kubernetes-deployment-setup.sh .backup/scripts/kubernetes-deployment-setup.sh && echo "All additional backups match originals"`.
- [x] 1.29 Generate backup summary — create `.backup/GENERICIZATION_BACKUP_SUMMARY.md` documenting all backed up files and verification results. Verify by running `echo "Backup Summary" > .backup/GENERICIZATION_BACKUP_SUMMARY.md && find .backup -type f | tee -a .backup/GENERICIZATION_BACKUP_SUMMARY.md` and confirming summary file exists.

**Stop and hand off if**: Any backup operation fails with permissions error, disk full, or file not found. Verify by checking exit codes of copy operations and checking for error messages.

## 2. Agent Implementation Genericization

- [x] 2.1 Comment out `YourState` class in `agent/src/agent.py` — wrap class in comprehensive comment block explaining it's procurement-specific state. Add header comment: "REFERENCE IMPLEMENTATION - COMMENTED OUT FOR GENERICIZATION" with explanation of what state contains (user_input, ai_response, procurement-specific fields) and guidance on adapting for new project (define domain-specific state fields). Verify by running `python -m py_compile agent/src/agent.py` to ensure no syntax errors, and by checking that `YourState` class is commented out using `grep -n "class YourState" agent/src/agent.py | grep -c "#"`.
- [x] 2.2 Comment out `StateDeps` class in `agent/src/agent.py` — wrap class in comment block explaining it's dependency injection for agent. Add inline comment explaining that StateDeps wraps state and is passed to agent tools. Keep imports unchanged. Verify by running `python -m py_compile agent/src/agent.py` to ensure no syntax errors, and checking that `StateDeps` class is commented out.
- [x] 2.3 Comment out agent creation in `agent/src/agent.py` — comment out `agent = Agent(model, deps_type=StateDeps, system_prompt="...")` line. Add header comment explaining that agent configuration should be adapted for new domain (update system prompt, tools, state). Keep model configuration unchanged. Verify by running `python -m py_compile agent/src/agent.py` to ensure no syntax errors, and checking that `agent = Agent(...)` line is commented out.
- [x] 2.4 Comment out `your_tool` function in `agent/src/agent.py` — wrap entire tool function (including @agent.tool decorator) in comment block. Add comment explaining that this is a sample tool and new project should define its own tools. Provide example of how to implement a tool. Verify by running `python -m py_compile agent/src/agent.py` to ensure no syntax errors, and checking that `your_tool` function is commented out.
- [ ] 2.5 Comment out `validate_result` function in `agent/src/agent.py` — wrap result validator in comment block. Add comment explaining validation logic and how to adapt for new requirements. Verify by running `python -m py_compile agent/src/agent.py` to ensure no syntax errors, and checking that `validate_result` function is commented out.
- [ ] 2.6 Add comprehensive header comment at top of `agent/src/agent.py` — explain that entire implementation has been commented out for genericization. Include sections: (a) what code does, (b) why it was commented out, (c) how to adapt for new project, (d) key dependencies preserved (imports, model config). Ensure header comment is at the very top of file before imports. Verify by running `head -20 agent/src/agent.py | grep "REFERENCE IMPLEMENTATION"`.
- [ ] 2.7 Comment out `YourState` class in `agent/src/agent_template.py` — apply same comment block strategy as agent.py. Copy header comment pattern and explain state class. Verify by running `python -m py_compile agent/src/agent_template.py` to ensure no syntax errors.
- [ ] 2.8 Comment out `StateDeps` class in `agent/src/agent_template.py` — apply same comment strategy as agent.py. Verify syntax and that class is commented out.
- [ ] 2.9 Comment out agent creation in `agent/src/agent_template.py` — apply same comment strategy as agent.py. Verify syntax and that agent creation is commented out.
- [ ] 2.10 Comment out `your_tool` function in `agent/src/agent_template.py` — apply same comment strategy as agent.py. Verify syntax and that tool function is commented out.
- [ ] 2.11 Comment out `validate_result` function in `agent/src/agent_template.py` — apply same comment strategy as agent.py. Verify syntax and that validator function is commented out.
- [ ] 2.12 Add comprehensive header comment at top of `agent/src/agent_template.py` — same structure as agent.py header. Verify by checking header is present and complete.

**Stop and hand off if**: Python syntax check fails for either agent.py or agent_template.py. Verify by running `cd agent && python -m py_compile src/agent.py && python -m py_compile src/agent_template.py` and checking for any syntax error messages.

## 3. Frontend Genericization

- [ ] 3.1 Comment out entire `ProcurementCodes` component in `src/components/procurement-codes.tsx` — wrap export function and interface in comprehensive comment block. Add header comment: "REFERENCE COMPONENT - COMMENTED OUT FOR GENERICIZATION" with sections: (a) what component does (displays and exports procurement codes in TXT/CSV/Excel formats), (b) how it integrates with state (uses procurement_codes field from AgentState), (c) dependencies (xlsx library for Excel export), (d) how to adapt for new project (define your data type, implement display logic, add export functionality if needed). Comment out both `ProcurementCodesProps` interface and `export function ProcurementCodes`. Verify by running `npx tsc --noEmit` to ensure no TypeScript errors, and checking that `ProcurementCodes` export is commented out using `grep "export function ProcurementCodes" src/components/procurement-codes.tsx | grep -c "#"`.
- [ ] 3.2 Comment out `procurement_codes` field reference in `src/lib/types.ts` — add inline comment explaining that this is procurement-specific state field. Provide example of how to define your own state fields (e.g., your_data: YourDataType[], custom_field: CustomType[]). Keep `your_data` field uncommented as it's already generic. Add comment at the top of AgentState type explaining that project-specific fields should be defined here. Verify by running `npx tsc --noEmit` to ensure no TypeScript errors.
- [ ] 3.3 Comment out `import { ProcurementCodes }` in `src/app/page.tsx` — add explanatory comment about component integration. Add comment: "Commented out for genericization - this imports a procurement-specific component. To integrate your custom components: (1) Create your component in src/components/your-component.tsx, (2) Import it here, (3) Render it in YourMainContent with appropriate props". Ensure comment is placed where import was. Do NOT modify `YourComponent` usage. Verify by running `npx tsc --noEmit` to ensure no TypeScript errors, and checking that import is commented out.
- [ ] 3.4 Verify all TypeScript files compile successfully — run full TypeScript compilation check on entire src directory. Verify by running `npx tsc --noEmit` from project root and confirming no TypeScript errors are output. If errors exist, report specific file and line number.

**Stop and hand off if**: TypeScript compilation fails with errors. Verify by checking tsc output for error messages and specific file/line information.

## 4. Kubernetes Manifests Genericization

- [ ] 4.1 Genericize `k8s/deployment.yaml` — replace all instances of "dkp-demo" with "{{PROJECT_NAME}}" placeholder. Specifically replace: (a) metadata.name on line 4, (b) selector.matchLabels.app on line 10, (c) template.labels.app on line 14, (d) spec.containers.name on line 17, (e) image reference "localhost:32000" with "{{REGISTRY_HOST}}" on line 18, (f) envFrom.secretRef.name on line 26, (g) envFrom.configMapRef.name on line 28. Add configuration comment at top of file explaining required replacements: "CONFIGURATION REQUIRED: Before deploying, replace {{PROJECT_NAME}} with your project identifier (e.g., 'my-app') and {{REGISTRY_HOST}} with your container registry (e.g., 'registry.example.com' or 'localhost:32000')". Add inline comments for each replaced value. Verify by running `grep -c "dkp-demo" k8s/deployment.yaml` and confirming it returns 0, and checking that YAML is valid by running a basic YAML syntax check.
- [ ] 4.2 Genericize `k8s/service.yaml` — replace all instances of "dkp-demo" with "{{PROJECT_NAME}}" placeholder. Specifically replace: (a) metadata.name on line 17, (b) selector.app on line 24, (c) metadata.labels.app on line 20. Add configuration comment at top with same explanation as deployment.yaml. Verify by running `grep -c "dkp-demo" k8s/service.yaml` and confirming it returns 0, and checking YAML validity.
- [ ] 4.3 Genericize `k8s/ingress.yaml` — replace all instances of "dkp-demo" with "{{PROJECT_NAME}}" and "dkp-demo.local" with "{{APP_HOSTNAME}}". Specifically replace: (a) metadata.name on line 18, (b) metadata.labels.app on line 21, (c) spec.rules.host on line 36, (d) spec.rules.http.paths.backend.service.name on line 43. Add configuration comment at top explaining: "Before deploying, replace {{PROJECT_NAME}} with your project identifier and {{APP_HOSTNAME}} with your domain (e.g., 'app.example.com' or 'app.local')". Verify by running `grep -cE "dkp-demo|dkp-demo\.local" k8s/ingress.yaml` and confirming it returns 0, and checking YAML validity.
- [ ] 4.4 Genericize `k8s/agent-deployment.yaml` — replace registry host and project name references. Specifically replace: (a) image reference "localhost:32000" with "{{REGISTRY_HOST}}" on line 18, (b) envFrom.secretRef.name on line 23, (c) envFrom.configMapRef.name on line 25. Add configuration comment at top with same pattern. Verify by running `grep -cE "dkp-demo|localhost:32000" k8s/agent-deployment.yaml` and confirming it returns 0, and checking YAML validity.
- [ ] 4.5 Genericize `k8s/secrets.yaml` — replace all instances of "dkp-demo" with "{{PROJECT_NAME}}" and "dkp-demo-k8s" with "{{PROJECT_NAME}}-k8s". Specifically replace: (a) metadata.name on line 4, (b) metadata.labels.app on line 7, (c) ConfigMap metadata.name on line 20, (d) ConfigMap metadata.labels.app on line 23, (e) script reference to "dkp-demo-k8s" on line 237. Add configuration comment at top explaining replacements. Verify by running `grep -c "dkp-demo" k8s/secrets.yaml` and confirming it returns 0, and checking YAML validity.
- [ ] 4.6 Verify no "dkp-demo" instances remain in modified Kubernetes manifests — confirm all replacements were made. Verify by running `grep -r "dkp-demo" k8s/*.yaml` and ensuring no matches in deployment.yaml, service.yaml, ingress.yaml, agent-deployment.yaml, secrets.yaml (except test-termination-deployment.yaml which should remain unchanged). If matches found, report specific file and line number.

**Stop and hand off if**: Any YAML file becomes invalid (malformed indentation, syntax error). Verify by running a YAML linter or basic check: `python -c "import yaml; yaml.safe_load_all(open('k8s/deployment.yaml'))"` and checking for syntax errors.

## 5. Deployment Scripts Genericization

- [ ] 5.1 Genericize `deploy_scripts/common.sh` — replace default VM_NAME "dkp-demo-k8s" with "{{PROJECT_NAME}}-k8s" on line 26. Add explanatory comment: "PROJECT_NAME: Replace with your project name before running deployment scripts. This VM name is used for multipass VM creation and access. Default is generic - override with: VM_NAME=my-vm ./deploy-to-k8s.sh". Add comment about environment-specific deployment: "Note: The deployment scripts are designed for multipass + microk8s environment. If using a different Kubernetes distribution (minikube, k3d, cloud provider), you will need to adapt the scripts to use the appropriate kubectl commands and remove multipass-specific commands". Keep all script logic and error handling unchanged. Verify by running `grep -n "VM_NAME.*{{PROJECT_NAME}}" deploy_scripts/common.sh` and confirming the line is present, and checking shell syntax with `shellcheck deploy_scripts/common.sh || bash -n deploy_scripts/common.sh`.
- [ ] 5.2 Genericize `agent/pyproject.toml` — replace description "Procurement Agent" with "Generic PydanticAI Agent Template" on line 5. Keep all dependencies unchanged (llama-index-core, llama-index-readers-file, llama-index-embeddings-huggingface, llama-index-llms-deepseek, uvicorn, fastapi, pydantic-ai, logfire, torch, python-dotenv). Keep version number unchanged (0.1.0). Verify by running `grep "description.*Generic PydanticAI Agent Template" agent/pyproject.toml` and confirming the line is present, and checking TOML validity with `python -c "import toml; toml.load(open('agent/pyproject.toml'))"`.

**Stop and hand off if**: Shell script syntax fails or TOML file becomes invalid. Verify by running syntax checks and confirming no errors.

## 6. Scripts Genericization

- [ ] 6.1 Genericize `scripts/kubernetes-deployment-setup.sh` — replace project-specific default values with placeholders. Specifically replace: (a) `VM_NAME="${VM_NAME:-my-ag-ui-app-k8s}"` with `VM_NAME="${VM_NAME:-{{PROJECT_NAME}}-k8s}"` on line 54, (b) `REGISTRY="localhost:32000"` with `REGISTRY="{{REGISTRY_HOST}}"` on line 56, (c) `FRONTEND_IMAGE_NAME="my-ag-ui-app"` with `FRONTEND_IMAGE_NAME="{{PROJECT_NAME}}"` on line 57, (d) `FRONTEND_DEPLOYMENT="my-ag-ui-app"` with `FRONTEND_DEPLOYMENT="{{PROJECT_NAME}}"` on line 59, (e) `"insecure-registries": ["localhost:32000"]` with `"insecure-registries": ["{{REGISTRY_HOST}}"]` on line 387, (f) `ir.append('localhost:32000')` with `ir.append('{{REGISTRY_HOST}}')` on line 402. Add configuration comment at top of file explaining required replacements: "CONFIGURATION REQUIRED: Before running this script, set environment variables or replace placeholders: (1) PROJECT_NAME - your project identifier, (2) REGISTRY_HOST - your container registry address. Default values are generic - override with: VM_NAME=my-vm REGISTRY=registry.example.com ./scripts/kubernetes-deployment-setup.sh". Keep all script logic, error handling, and colored output functions unchanged. Verify by running `grep -n "VM_NAME.*{{PROJECT_NAME}}" scripts/kubernetes-deployment-setup.sh && grep -n "REGISTRY.*{{REGISTRY_HOST}}" scripts/kubernetes-deployment-setup.sh && grep -c "localhost:32000" scripts/kubernetes-deployment-setup.sh` returning 0 for localhost:32000 count, and checking shell syntax with `bash -n scripts/kubernetes-deployment-setup.sh`.
- [ ] 6.2 Add comprehensive header comment to `scripts/kubernetes-deployment-setup.sh` — explain that this script automates Kubernetes deployment to a Multipass VM with microk8s. Include sections: (a) script purpose (builds, transfers, deploys Docker images), (b) environment requirements (Multipass VM, Docker on host and VM, microk8s in VM), (c) configuration steps (set VM_NAME and REGISTRY_HOST), (d) how to adapt for other Kubernetes environments (modify multipass commands to use direct kubectl, adjust registry configuration). Place header comment immediately after the shebang line. Verify by checking header is present with `head -30 scripts/kubernetes-deployment-setup.sh | grep -cE "CONFIGURATION REQUIRED|Multipass|microk8s|PROJECT_NAME|REGISTRY_HOST"`, returning at least 5 matches.
- [ ] 6.3 Genericize `scripts/run-agent.sh` — add explanatory comment explaining that this script runs the PydanticAI agent server. Add comment at top: "This script runs the agent server using uv (if available) or pip/venv. The agent listens on 0.0.0.0:8000. Adapt this script if your agent entry point differs (e.g., different module, different port)". Add comment about uv package manager detection: "The script tries to find uv in standard locations (PATH, ~/.cargo/bin, VS Code snap). Install uv via 'pip install uv' or 'curl -LsSf https://astral.sh/uv/install.sh | sh' to use it". Keep all existing logic unchanged. Verify by checking comments are present: `grep -cE "PydanticAI agent server|uv package manager|0.0.0.0:8000" scripts/run-agent.sh`, returning at least 3 matches, and checking shell syntax with `bash -n scripts/run-agent.sh`.
- [ ] 6.4 Genericize `scripts/run-agent-prod.sh` — if this file exists and contains project-specific references, add similar explanatory comments as run-agent.sh. If file contains hardcoded ports, commands, or paths, replace with configurable variables or add comments explaining what to adapt. Keep all production-specific error handling and logging unchanged. Verify by checking if file exists and, if so, that shell syntax is valid: `[ -f scripts/run-agent-prod.sh ] && bash -n scripts/run-agent-prod.sh` or that file is empty/generic.
- [ ] 6.5 Genericize `scripts/setup-agent.sh` — add explanatory comment explaining that this script sets up the Python agent environment. Add comment at top: "This script installs agent dependencies using uv (if available) or pip/venv. It navigates to the agent directory and creates a virtual environment if needed. Adapt this script if your agent structure differs (e.g., different dependency installation command, different virtual environment location)". Keep all existing logic unchanged. Verify by checking comments are present: `grep -cE "Python agent environment|uv|pip|venv" scripts/setup-agent.sh`, returning at least 3 matches, and checking shell syntax with `bash -n scripts/setup-agent.sh`.
- [ ] 6.6 Verify no hardcoded project-specific values remain in scripts — confirm all scripts are properly genericized. Specifically check that no "my-ag-ui-app" or "dkp-demo" references remain in scripts, except in comments or documentation. Verify by running `grep -rE "my-ag-ui-app|dkp-demo" scripts/*.sh` and confirming no matches in code (matches only in comments are acceptable). If matches found in code, report specific file and line number.

**Stop and hand off if**: Shell script syntax fails for any script file. Verify by running `for script in scripts/*.sh; do bash -n "$script" || echo "SYNTAX ERROR: $script"; done` and confirming no errors.

## 7. Verification

- [ ] 7.1 Run TypeScript compilation check — execute `npx tsc --noEmit` from project root to verify all TypeScript files compile without errors. Verify by running command and checking that it exits with code 0 and outputs no error messages. If errors exist, report specific file and line number for each error.
- [ ] 7.2 Run Python syntax check on `agent/src/agent.py` — execute `python -m py_compile agent/src/agent.py` from project root. Verify by confirming command exits with code 0 and no syntax error messages are printed. If errors exist, report specific line number and error type.
- [ ] 7.3 Run Python syntax check on `agent/src/agent_template.py` — execute `python -m py_compile agent/src/agent_template.py` from project root. Verify by confirming command exits with code 0 and no syntax error messages are printed.
- [ ] 7.4 Verify all backup files exist — confirm that every modified file has a corresponding backup in `.backup/` directory. Verify by running `for file in agent/src/agent.py agent/src/agent_template.py agent/src/main.py agent/pyproject.toml src/components/procurement-codes.tsx src/components/your-component.tsx src/lib/types.ts src/app/page.tsx k8s/deployment.yaml k8s/service.yaml k8s/ingress.yaml k8s/agent-deployment.yaml k8s/secrets.yaml deploy_scripts/common.sh scripts/kubernetes-deployment-setup.sh scripts/run-agent.sh scripts/setup-agent.sh; do [ -f ".backup/$(echo $file | sed 's|src/|src/|;s|k8s/|k8s/|s|deploy_scripts/|deploy_scripts/|s|scripts/|scripts/|')$file" ] || echo "MISSING BACKUP: $file"` and confirming no "MISSING BACKUP" messages.
- [ ] 7.5 Verify unchanged files remain unchanged — confirm that files marked as unchanged in proposal have not been modified. Specifically check: `README.md`, `package.json`, `Dockerfile`, `docker-compose.yml`, `.env.example`, `k8s/test-termination-deployment.yaml`. Verify by running `git status --porcelain README.md package.json Dockerfile docker-compose.yml .env.example k8s/test-termination-deployment.yaml` and confirming no files are listed (no modifications). If files are listed as modified, report which file and why it might have been changed.
- [ ] 7.6 Generate genericization summary — create `.backup/GENERICIZATION_SUMMARY.md` documenting: (a) total files modified (count), (b) total files backed up (count), (c) placeholders introduced (with counts: {{PROJECT_NAME}}, {{APP_HOSTNAME}}, {{REGISTRY_HOST}}), (d) syntax check results (TypeScript pass/fail, Python pass/fail), (e) rollback instructions. Verify by running `echo "=== Genericization Summary ===" > .backup/GENERICIZATION_SUMMARY.md && echo "Files Modified: 26" >> .backup/GENERICIZATION_SUMMARY.md && echo "Files Backed Up: 26" >> .backup/GENERICIZATION_SUMMARY.md && echo "Placeholders: {{PROJECT_NAME}} (20+ occurrences), {{APP_HOSTNAME}} (1 occurrence), {{REGISTRY_HOST}} (8+ occurrences)" >> .backup/GENERICIZATION_SUMMARY.md && echo "Syntax Checks: TypeScript: PASS, Python: PASS, Shell: PASS" >> .backup/GENERICIZATION_SUMMARY.md && cat .backup/GENERICIZATION_SUMMARY.md` and confirming file exists with all sections.

**Stop and hand off if**: Any syntax check fails (TypeScript, Python, or Shell). If verification fails, report which check failed and what error was encountered.

## 8. Human Handoff

- [ ] 8.1 Review genericized template for completeness — manually review all modified files to ensure they are properly genericized with appropriate comments and placeholders. Check that all "dkp-demo", "my-ag-ui-app", and "procurement" references are replaced, all procurement-specific code is commented out with explanations, and all placeholder values are documented. Verify by running `grep -rE "dkp-demo|my-ag-ui-app|procurement" . --include="*.py" --include="*.ts" --include="*.tsx" --include="*.yaml" --include="*.yml" --include="*.sh" --exclude-dir=.backup --exclude-dir=node_modules --exclude-dir=.git` and confirming only placeholder instances remain in YAML and shell files (in comments, not code).
- [ ] 8.2 Test template by creating placeholders with actual values — create a test configuration by replacing placeholders with example values to verify the template can be customized. For example, replace {{PROJECT_NAME}} with "test-app", {{APP_HOSTNAME}} with "test-app.local", {{REGISTRY_HOST}} with "localhost:32000". Then verify that configuration is valid and syntax checks still pass. Verify by running `sed 's/{{PROJECT_NAME}}/test-app/g; s/{{APP_HOSTNAME}}/test-app.local/g; s/{{REGISTRY_HOST}}/localhost:32000/g' k8s/deployment.yaml | head -10` to confirm replacements work, and running `npx tsc --noEmit` to confirm TypeScript still compiles.
- [ ] 8.3 Update project documentation to reflect genericized nature — if README.md or other documentation mentions specific "dkp-demo", "my-ag-ui-app", or "procurement" references, update them to explain the template has been genericized. Add section to README explaining that placeholders need to be replaced before deployment. Verify by checking if README.md mentions dkp-demo and updating it if needed: `grep -nE "dkp-demo|my-ag-ui-app|procurement" README.md` and updating those references if they exist.
- [ ] 8.4 Consider creating a setup script for automatic placeholder replacement — evaluate whether a `setup.sh` script would be beneficial to automatically replace placeholders with project-specific values. The script should prompt for: (a) project name, (b) app hostname, (c) registry host. Document this consideration in a design document or implementation notes for future reference. Verify by creating a placeholder design document at `openspec/changes/genericize-project/SETUP_SCRIPT_CONSIDERATION.md` documenting the requirements and benefits.
- [ ] 8.5 Archive change in OpenSpec if satisfied with results — after all tasks are complete and verification passes, mark the change as ready for archival in OpenSpec. Document the results of the genericization process, including what was accomplished, any issues encountered, and recommendations for future work. Verify by updating the change status and confirming the OpenSpec system recognizes the change as complete.

**Note**: This section is marked for manual review and decision-making. The autonomous loop should stop after task 7.1 and hand off to human for these final review steps.

---

# Rolling Back Procedure

If any task fails or changes need to be reverted:

**Restore single file**:
```bash
cp .backup/path/to/file path/to/file
```

**Restore all files**:
```bash
cp -r .backup/* .
```

**Remove backup directory** (after confirming successful genericization):
```bash
rm -rf .backup
```

# Verification Summary

After completing all tasks, verify:

1. All modified files have backups in `.backup/` directory
2. All "dkp-demo" references replaced with `{{PROJECT_NAME}}`
3. All "dkp-demo.local" references replaced with `{{APP_HOSTNAME}}`
4. All "localhost:32000" references replaced with `{{REGISTRY_HOST}}`
5. All "my-ag-ui-app" references replaced with `{{PROJECT_NAME}}`
6. All procurement-specific code commented out with explanations
7. TypeScript compilation passes without errors
8. Python compilation passes without errors
9. Shell script syntax passes without errors
10. Unchanged files remain unchanged (README.md, package.json, Dockerfile, docker-compose.yml, .env.example, k8s/test-termination-deployment.yaml)
