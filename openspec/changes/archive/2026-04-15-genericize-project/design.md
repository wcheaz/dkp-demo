# Genericization Design

## Overview

This design document specifies the approach for genericizing the project template. The goal is to remove project-specific hardcoded values while preserving the code structure as reference examples.

## Design Principles

1. **Preserve over Delete**: Never delete implementation code. Comment it out with detailed explanations so future developers can understand and adapt it.

2. **Clear Placeholders**: Use obvious placeholder names like `{{PROJECT_NAME}}`, `{{APP_NAME}}`, `{{HOSTNAME}}` that clearly indicate where customization is needed.

3. **Comprehensive Comments**: Every commented-out block should include:
   - What the code does (current logic)
   - Why it was commented out (context for future reference)
   - How to adapt it for a new project (guidance)

4. **Backup Strategy**: All modifications must have complete backups in `.backup/` directory with original file paths preserved.

5. **Minimal Changes**: Only modify what is necessary to make the template generic. Don't "over-clean" - keep working configurations where possible.

## File Modification Strategy

### 1. Backup Creation

**Location**: `.backup/` directory at project root

**Structure**: Preserve original directory structure
```
.backup/
├── agent/
│   ├── src/
│   │   ├── agent.py
│   │   ├── agent_template.py
│   │   └── main.py
│   └── pyproject.toml
├── src/
│   ├── components/
│   │   ├── procurement-codes.tsx
│   │   └── your-component.tsx
│   ├── lib/
│   │   └── types.ts
│   └── app/
│       └── page.tsx
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── agent-deployment.yaml
│   └── secrets.yaml
└── deploy_scripts/
    └── common.sh
```

**Implementation**: Before modifying any file, create a backup:
```bash
mkdir -p .backup/$(dirname "$FILE")
cp "$FILE" ".backup/$FILE"
```

### 2. Agent Implementation Genericization

**Files**: `agent/src/agent.py`, `agent/src/agent_template.py`

**Approach**:
- Comment out the entire implementation (all tool definitions, state classes, agent creation)
- Keep imports as-is (these are generic dependencies)
- Add a clear comment block at the top explaining this is reference code
- Example comment format:
```python
# ============================================================================
# REFERENCE IMPLEMENTATION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# The following code implements a procurement agent with specific business logic.
# It has been commented out to create a generic template.
#
# To adapt for your project:
# 1. Define your state class with domain-specific fields
# 2. Create tools that implement your business logic
# 3. Configure the agent with appropriate system prompt and model
# 4. Uncomment and adapt the code below
# ============================================================================
```

**What to comment**:
- StateDeps class definition
- agent creation
- All tool functions (@agent.tool decorators)
- result_validator function

**What to keep**:
- All imports (pydantic_ai, OpenAIModel, etc.)
- Model configuration (this is generic)
- Empty placeholder comments indicating where to implement

### 3. Component Genericization

**File**: `src/components/procurement-codes.tsx`

**Approach**:
- Comment out the entire component (export function and all logic)
- Add comprehensive header comment explaining:
  - What this component does (displays and exports procurement codes)
  - How it integrates with state (uses procurement_codes field)
  - Dependencies (xlsx library for Excel export)
  - How to adapt it for other data types

**Implementation**:
```typescript
// ============================================================================
// REFERENCE COMPONENT - COMMENTED OUT FOR GENERICIZATION
// ============================================================================
// This component displays previously generated procurement codes with export
// functionality (TXT, CSV, Excel). It serves as a reference implementation for
// creating similar data display/export components.
//
// Current Logic:
// - Receives AgentState with procurement_codes array
// - Renders list of code/description pairs
// - Provides download buttons for TXT, CSV, and Excel formats
// - Allows individual item deletion
//
// Dependencies:
// - xlsx library: utils.json_to_sheet, utils.sheet_to_csv, writeFile
// - AgentState from @/lib/types
//
// To adapt for your project:
// 1. Define your data type (e.g., interface YourDataType)
// 2. Update the component props to match your state structure
// 3. Implement your display logic (map over your data)
// 4. Add export functionality if needed (can reuse the xlsx utilities)
// 5. Update styling to match your UI requirements
// ============================================================================
```

### 4. Type Definitions Genericization

**File**: `src/lib/types.ts`

**Approach**:
- Comment out the `procurement_codes` field from AgentState
- Keep `your_data` field as-is (it's already generic)
- Add explanatory comment about how to define project-specific types

**Implementation**:
```typescript
// Domain-specific state fields - uncomment and adapt for your project
// Example: procurement-specific state
// export type ProcurementCode = {
//   code: string;
//   description: string;
// };

// export type AgentState = {
//   your_data: YourDataType[];
//   procurement_codes?: ProcurementCode[];  // Commented out for genericization
// };

// Generic state (current)
export type AgentState = {
  your_data: YourDataType[];
  // procurement_codes?: ProcurementCode[];  // Remove this comment when adapting
}
```

### 5. Page Integration Genericization

**File**: `src/app/page.tsx`

**Approach**:
- Comment out the import of `procurement-codes.tsx`
- Add explanatory comment about component integration
- Do NOT modify the YourComponent usage (it's already generic)

**Implementation**:
```typescript
// Commented out for genericization - this imports a procurement-specific component
// import { ProcurementCodes } from "@/components/procurement-codes";

// To integrate your custom components:
// 1. Create your component in src/components/your-component.tsx
// 2. Import it here
// 3. Render it in YourMainContent with appropriate props
// Example:
// import { YourCustomComponent } from "@/components/your-custom-component";
```

### 6. Kubernetes Manifests Genericization

**Files**: `k8s/deployment.yaml`, `k8s/service.yaml`, `k8s/ingress.yaml`, `k8s/agent-deployment.yaml`, `k8s/secrets.yaml`

**Approach**:
- Replace all instances of "dkp-demo" with `{{PROJECT_NAME}}`
- Replace "dkp-demo.local" with `{{APP_HOSTNAME}}`
- Replace "localhost:32000" with `{{REGISTRY_HOST}}`
- Add configuration comments at the top of each file
- Add inline comments for each replaced value

**Placeholder Values**:
- `{{PROJECT_NAME}}`: Short identifier for the project (e.g., "my-app")
- `{{APP_NAME}}`: Application name (e.g., "My Application")
- `{{APP_HOSTNAME}}`: Domain/host for ingress (e.g., "app.example.com")
- `{{REGISTRY_HOST}}`: Container registry host (e.g., "registry.example.com" or "localhost:32000")

**Implementation Example** (ingress.yaml):
```yaml
# {{PROJECT_NAME}} Ingress Configuration
# ===================================
#
# CONFIGURATION REQUIRED:
# =========================
# Before deploying, replace the following placeholders:
#
# {{PROJECT_NAME}}: Your project identifier (e.g., "my-app")
# {{APP_HOSTNAME}}: Your application hostname (e.g., "app.example.com" or "app.local")
#
# Example: if your project is called "my-app" and runs at myapp.local:
# - Replace {{PROJECT_NAME}} with "my-app"
# - Replace {{APP_HOSTNAME}} with "myapp.local"
#
# Notes:
# - ingressClassName: nginx (using NGINX ingress controller)
# - rewrite-target: / (standard path rewriting)
# - SSE streaming support configured for agent communication
# - SSL redirect disabled for development (enable for production)
#
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{PROJECT_NAME}}-ingress  # Replace {{PROJECT_NAME}} with your project name
  namespace: default
  labels:
    app: {{PROJECT_NAME}}  # Replace {{PROJECT_NAME}} with your project name
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    # ... other annotations remain unchanged ...
spec:
  ingressClassName: nginx
  rules:
  - host: {{APP_HOSTNAME}}  # Replace {{APP_HOSTNAME}} with your domain
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {{PROJECT_NAME}}-service  # Replace {{PROJECT_NAME}} with your project name
            port:
              name: http
```

**Replacement Rules**:
- In metadata.name: `{{PROJECT_NAME}}-<resource-type>`
- In labels.app: `{{PROJECT_NAME}}`
- In selector.app: `{{PROJECT_NAME}}`
- In image references: `{{REGISTRY_HOST}}/{{PROJECT_NAME}}:latest`
- In service names: `{{PROJECT_NAME}}-service`
- In secret/configMap names: `{{PROJECT_NAME}}-secrets`, `{{PROJECT_NAME}}-config`

### 7. Deployment Scripts Genericization

**File**: `deploy_scripts/common.sh`

**Approach**:
- Replace default VM_NAME "dkp-demo-k8s" with generic default "{{PROJECT_NAME}}-k8s"
- Add explanatory comment about environment-specific deployment
- Do NOT modify the script logic or error handling (keep functionality intact)

**Implementation**:
```bash
# Global variables
# PROJECT_NAME: Replace with your project name before running deployment scripts
# This VM name is used for multipass VM creation and access
# Default is generic - override with: VM_NAME=my-vm ./deploy-to-k8s.sh
VM_NAME="${VM_NAME:-{{PROJECT_NAME}}-k8s}"

# Note: The deployment scripts are designed for multipass + microk8s environment.
# If using a different Kubernetes distribution (minikube, k3d, cloud provider),
# you will need to adapt the scripts to use the appropriate kubectl commands
# and remove multipass-specific commands.
```

### 8. Agent Package Configuration Genericization

**File**: `agent/pyproject.toml`

**Approach**:
- Replace description "Procurement Agent" with generic description
- Keep all dependencies unchanged (these are functional requirements, not project-specific)

**Implementation**:
```toml
[project]
name = "agent"
version = "0.1.0"
description = "Generic PydanticAI Agent Template"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    # ... dependencies remain unchanged ...
]
```

## Verification Strategy

After each major transformation step, verify:

1. **TypeScript Syntax**: Run `npx tsc --noEmit` to ensure no syntax errors
2. **Python Syntax**: Run `python -m py_compile agent/src/*.py` to ensure no syntax errors
3. **YAML Validity**: Run `yamllint k8s/*.yaml` if available, or manually check indentation
4. **Backup Integrity**: Verify all backed up files exist and match originals

## Rollback Procedure

If any transformation step fails:

1. Restore specific file from backup:
   ```bash
   cp .backup/path/to/file path/to/file
   ```

2. Restore all files at once:
   ```bash
   cp -r .backup/* .
   ```

3. Remove backup directory (after confirming successful genericization):
   ```bash
   rm -rf .backup
   ```

## Known Limitations

1. **Placeholder Resolution**: This change does NOT include a script to automatically replace placeholders. That's deferred to future work.

2. **Testing**: The genericized template will not work out-of-the-box without placeholder replacement. Tests will likely fail until placeholders are resolved.

3. **IDE Support**: Some IDEs may show errors in commented-out code. This is expected and acceptable.

4. **Deployment**: Direct deployment will fail until placeholders are replaced with actual values.

## Future Enhancements (Deferred)

1. Create a `setup.sh` script that prompts for project details and generates customized files
2. Add a `verify-template.sh` script that checks for remaining hardcoded values
3. Create multiple example configurations (AWS EKS, GKE, minikube, etc.)
4. Extract deployment logic into environment-agnostic scripts
5. Add a `customize.sh` interactive script for guided customization
