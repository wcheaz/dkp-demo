# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

# Genericize Project for Reusability

## Problem Statement

The current codebase contains project-specific references, hardcoded values, and domain-specific logic that limit its reusability as a template. The project was imported from another project and still contains references to "dkp-demo," "procurement," and specific deployment infrastructure (multipass VMs, microk8s clusters).

This makes the project difficult to reuse as a clean template for new projects because:
- Project names and identifiers are hardcoded throughout Kubernetes manifests
- Domain-specific logic (procurement codes) exists in components
- Agent implementation contains procurement-specific code
- Deployment scripts reference specific VM and cluster names
- Configuration files contain specific service names and hostnames

## Intended Value

This change will transform the project into a clean, generic template that can be easily adapted for new use cases. It will:
- Remove all hardcoded project-specific references from deployment configurations
- Comment out domain-specific implementation logic while preserving it as reference examples
- Provide clear documentation on how to customize the template for new projects
- Maintain a working baseline that can be restored if needed
- Make the project suitable for open-source distribution or internal template reuse

## Scope

**In Scope:**
1. Create temporary backups of all files that will be modified (stored in `.backup/` directory, easily deletable)
2. Comment out project-specific agent implementation logic in `agent/src/agent.py` and `agent/src/agent_template.py`
3. Comment out the `src/components/procurement-codes.tsx` component entirely
4. Remove `procurement_codes` references from `src/lib/types.ts` (comment out the type definition)
5. Genericize Kubernetes deployment YAMLs by replacing hardcoded values with placeholders:
   - Replace "dkp-demo" with generic placeholders in deployment, service, ingress, and secrets manifests
   - Replace "dkp-demo.local" hostname with generic placeholder in ingress
   - Add comments explaining what values need to be customized
6. Genericize deployment scripts:
   - Replace hardcoded VM_NAME default "dkp-demo-k8s" with generic placeholder
   - Add comments about multipass/microk8s-specific configuration
   - Note that these scripts are environment-specific and may need adaptation
7. Update `agent/pyproject.toml` to remove "Procurement Agent" description, replace with generic description
8. Remove imports of `procurement-codes.tsx` from `src/app/page.tsx` (comment out with explanation)

**Out of Scope (Explicit Non-Goals):**
- Do NOT modify the README.md (this documentation is already generic enough)
- Do NOT modify package.json name or version (these can remain as-is for npm purposes)
- Do NOT modify Dockerfile or docker-compose.yml configurations (these are already generic enough)
- Do NOT remove or modify the `agent/rag/` directory (leave as-is, can be used as example)
- Do NOT modify environment variable examples in `.env.example` (these are generic)
- Do NOT modify test deployment YAML (`k8s/test-termination-deployment.yaml`) - leave as-is for testing
- Do NOT modify the actual deletion of files - only commenting out code, not deleting files
- Do NOT modify any node_modules or build artifacts

## Operational Impact

- **Development**: No impact - code changes are only comments and string replacements
- **Deployment**: Deployments will require configuration updates (by design - this is the point)
- **Testing**: Tests should continue to pass as we're only commenting out code, not changing behavior
- **Documentation**: Documentation may need updates to reflect the generic nature of the template

## Rollout Strategy

This is a one-time refactoring change with no staged rollout. The approach:

1. Create backup directory `.backup/` containing all original files before modification
2. Process files in order from least to most critical
3. After each major transformation step, verify the code can still be parsed (TypeScript/Python syntax checks)
4. Final verification: ensure project structure is intact and backups are complete

## Human Handoff Items

After this change is complete, the following will require human decision/action:

1. **Project Name Configuration**: When reusing this template, developers must decide on project naming conventions and update:
   - Kubernetes manifest metadata (names, labels)
   - Ingress hostname
   - Image repository names
   - VM/cluster names in deployment scripts

2. **Agent Implementation**: Developers must implement their specific agent logic by:
   - Uncommenting and adapting the agent code in `agent/src/agent.py`
   - Defining their own tools, state, and business logic
   - Updating `agent/pyproject.toml` with appropriate project description

3. **Component Implementation**: Developers must implement their specific UI components by:
   - Creating new components or adapting the commented-out examples
   - Updating `src/lib/types.ts` with their domain-specific state types
   - Integrating components into `src/app/page.tsx`

4. **Environment-Specific Deployment**: When deploying, developers must:
   - Adapt deployment scripts if not using multipass/microk8s
   - Configure secrets appropriately for their environment
   - Update ingress configuration for their domain/hostname

## Deferred Work

The following items are explicitly deferred to future changes:

1. **Create a setup wizard or initialization script** that prompts users for project-specific values and automatically generates the customized files
2. **Create a documentation guide** that walks through the customization process step-by-step
3. **Add validation scripts** that check for remaining hardcoded project-specific values before deployment
4. **Create example configurations** for common deployment scenarios (e.g., AWS EKS, GKE, minikube)
5. **Extract common deployment logic** into reusable, parameterized scripts that work across environments

## Success Criteria

The change is complete when:
- [ ] All modified files have backups in `.backup/` directory
- [ ] `agent/src/agent.py` and `agent/src/agent_template.py` have implementation commented out with clear explanatory comments
- [ ] `src/components/procurement-codes.tsx` is entirely commented out with explanatory comments
- [ ] `src/lib/types.ts` has `procurement_codes` type commented out with explanatory comments
- [ ] `src/app/page.tsx` has procurement-codes imports commented out with explanatory comments
- [ ] All Kubernetes YAML files have generic placeholders replacing "dkp-demo" with explanatory comments
- [ ] `k8s/ingress.yaml` has generic hostname placeholder with explanatory comment
- [ ] `agent/pyproject.toml` has generic description
- [ ] `deploy_scripts/common.sh` has generic VM_NAME default with explanatory comment
- [ ] Project builds without TypeScript errors
- [ ] Agent Python files parse without syntax errors
- [ ] Backup directory contains all original versions of modified files
- [ ] README.md is unchanged
- [ ] package.json is unchanged
- [ ] Dockerfile and docker-compose.yml are unchanged

## Specifications

specs/spec.md
# Genericization Specification

## Overview

This specification defines the required behaviors for genericizing the project template. The goal is to remove project-specific hardcoded values while preserving implementation as reference examples.

## Requirements

### REQ-1: Backup Creation

The system MUST create a complete backup of all files before modification.

**MUST**:
- Create `.backup/` directory at project root before any modifications
- Preserve original directory structure in backup
- Back up all files that will be modified
- Use exact file paths in backup (e.g., `.backup/src/components/procurement-codes.tsx`)

**SHALL NOT**:
- Modify any file without first backing it up
- Create backups in a location that conflicts with project structure
- Skip backing up any file that will be modified

**Verification**:
- Check `.backup/` directory exists
- Verify all modified files have corresponding backups
- Confirm backup files match original content (use diff or checksum)

**Failure Scenarios**:
- If backup creation fails: Stop immediately and report error
- If backup directory already exists: Verify contents match current files, overwrite if confirmed, or fail with error
- If file cannot be copied: Report specific file and error, stop transformation

### REQ-2: Agent Implementation Commenting

The system MUST comment out all agent implementation logic while preserving imports.

**MUST**:
- Comment out all tool functions (`@agent.tool` decorated functions)
- Comment out StateDeps class definition
- Comment out agent creation (the `agent = Agent(...)` line)
- Comment out result_validator function
- Keep all imports unchanged and active
- Keep model configuration unchanged and active
- Add comprehensive header comment explaining why code is commented out
- Add inline comments explaining each commented section

**SHALL**:
- Add comment block before each major section explaining its purpose
- Include guidance on how to adapt the code for new projects
- Maintain the exact structure of the code for easy uncommenting

**SHALL NOT**:
- Delete any implementation code
- Comment out imports or model configuration
- Modify any uncommented code

**Verification**:
- `python -m py_compile agent/src/agent.py` succeeds without syntax errors
- `python -m py_compile agent/src/agent_template.py` succeeds without syntax errors
- All tool functions are commented out
- Agent creation line is commented out
- All imports remain uncommented

**Example Header Comment Format**:
```python
# ============================================================================
# REFERENCE IMPLEMENTATION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# The following code implements a [domain-specific] agent with business logic.
# It has been commented out to create a generic template.
#
# Current Logic:
# - [Brief description of what the agent does]
# - [Key tools/functions implemented]
#
# To adapt for your project:
# 1. [Step 1 guidance]
# 2. [Step 2 guidance]
# 3. [Step 3 guidance]
# ============================================================================
```

### REQ-3: Component Commenting

The system MUST comment out the procurement-codes.tsx component entirely.

**MUST**:
- Comment out the entire `ProcurementCodes` component function
- Comment out the `ProcurementCodesProps` interface
- Add comprehensive header comment explaining:
  - What the component does
  - How it integrates with state
  - Dependencies it uses
  - How to adapt it for other data types
- Keep file intact (do not delete or rename)

**SHALL NOT**:
- Delete the component file
- Modify any other component (your-component.tsx must remain unchanged)

**Verification**:
- `npx tsc --noEmit` succeeds without TypeScript errors
- `src/components/procurement-codes.tsx` file exists
- All code in the file is commented out except comments
- Component function and interface are commented out

### REQ-4: Type Definition Commenting

The system MUST comment out procurement-specific type definitions.

**MUST**:
- Comment out `procurement_codes` field from AgentState type
- Keep `your_data` field unchanged and active
- Add explanatory comment about how to define project-specific types
- Maintain the file structure

**SHALL NOT**:
- Delete the file
- Modify `your_data` field
- Modify `YourDataType` type

**Verification**:
- `npx tsc --noEmit` succeeds without TypeScript errors
- `procurement_codes` field is commented out in AgentState
- `your_data` field remains uncommented

### REQ-5: Page Integration Commenting

The system MUST comment out imports of procurement-codes component.

**MUST**:
- Comment out the import statement for `procurement-codes.tsx`
- Add explanatory comment about component integration
- Do NOT modify the usage of `YourComponent`
- Keep all other imports unchanged

**SHALL NOT**:
- Modify component usage logic
- Comment out other imports
- Delete the import statement (must comment it out, not remove)

**Verification**:
- `npx tsc --noEmit` succeeds without TypeScript errors
- Import of `procurement-codes.tsx` is commented out
- `YourComponent` usage remains unchanged

### REQ-6: Kubernetes Manifest Genericization

The system MUST replace hardcoded project names with placeholders in Kubernetes manifests.

**MUST**:
- Replace all instances of "dkp-demo" with `{{PROJECT_NAME}}`
- Replace "dkp-demo.local" with `{{APP_HOSTNAME}}`
- Replace "localhost:32000" with `{{REGISTRY_HOST}}`
- Add configuration comments at the top of each file
- Add inline comments for each replaced value
- Process files:
  - `k8s/deployment.yaml`
  - `k8s/service.yaml`
  - `k8s/ingress.yaml`
  - `k8s/agent-deployment.yaml`
  - `k8s/secrets.yaml`

**SHALL NOT**:
- Modify `k8s/test-termination-deployment.yaml` (leave unchanged)
- Modify YAML structure or indentation
- Change non-project-specific values (ports, resource limits, etc.)

**Verification**:
- YAML files are valid (check with `yamllint` if available)
- No instances of "dkp-demo" remain in the modified files
- All placeholders use the correct format (`{{PLACEHOLDER_NAME}}`)
- Configuration comments are present at the top of each file

**Placeholder Mapping**:
| Original Value | Placeholder | Location |
|--------------|-------------|----------|
| dkp-demo | {{PROJECT_NAME}} | metadata.name, labels, selectors |
| dkp-demo.local | {{APP_HOSTNAME}} | ingress.host |
| localhost:32000 | {{REGISTRY_HOST}} | image references |

**Example Configuration Comment**:
```yaml
# {{PROJECT_NAME}} Kubernetes Configuration
# ========================================
#
# CONFIGURATION REQUIRED:
# ========================
# Before deploying, replace the following placeholders:
#
# {{PROJECT_NAME}}: Your project identifier (e.g., "my-app")
# {{APP_HOSTNAME}}: Your application hostname (e.g., "app.example.com")
# {{REGISTRY_HOST}}: Your container registry (e.g., "registry.example.com")
#
# Example: for a project called "my-app":
# - Replace {{PROJECT_NAME}} with "my-app"
# - Replace {{APP_HOSTNAME}} with "myapp.local"
# - Replace {{REGISTRY_HOST}} with "registry.example.com"
#
```

### REQ-7: Deployment Scripts Genericization

The system MUST replace hardcoded VM name with generic placeholder.

**MUST**:
- Replace default VM_NAME "dkp-demo-k8s" with "{{PROJECT_NAME}}-k8s"
- Add explanatory comment about environment-specific deployment
- Keep all script logic unchanged
- Add comment noting multipass/microk8s specificity

**SHALL NOT**:
- Modify script functionality
- Change error handling or logging
- Modify any other hardcoded values unless they are project-specific

**Verification**:
- Script syntax is valid (shellcheck if available)
- VM_NAME default value is "{{PROJECT_NAME}}-k8s"
- Explanatory comment is present
- Script functionality remains intact

### REQ-8: Agent Package Configuration Genericization

The system MUST replace project-specific description with generic description.

**MUST**:
- Replace description "Procurement Agent" with "Generic PydanticAI Agent Template"
- Keep all dependencies unchanged
- Keep version number unchanged
- Keep all other fields unchanged

**SHALL NOT**:
- Modify dependencies
- Change version number
- Modify any other configuration fields

**Verification**:
- `agent/pyproject.toml` is valid TOML
- Description is "Generic PydanticAI Agent Template"
- All dependencies remain unchanged

### REQ-9: Files to Leave Unchanged

The system MUST NOT modify specific files that are already generic.

**MUST NOT MODIFY**:
- `README.md` (already generic enough)
- `package.json` (name and version can remain as-is)
- `Dockerfile` (already generic)
- `docker-compose.yml` (already generic)
- `.env.example` (already generic)
- `k8s/test-termination-deployment.yaml` (for testing purposes)
- `agent/rag/` directory (leave as-is for reference)

**Verification**:
- These files remain unchanged (verify with diff against backups)

## Scenarios

### Scenario 1: Fresh Genericization

**Given**: A project with project-specific code and configurations

**When**: The genericization process runs

**Then**:
1. All specified files are backed up
2. All project-specific code is commented out
3. All hardcoded values are replaced with placeholders
4. All files are syntactically valid
5. The project structure is preserved

### Scenario 2: Partial Genericization Failure

**Given**: One file transformation fails (e.g., file cannot be written)

**When**: The genericization process encounters this failure

**Then**:
1. The process stops immediately
2. An error is reported with specific file and reason
3. All previously transformed files remain in their transformed state
4. Backups are available for rollback
5. No further transformations are attempted

### Scenario 3: Syntax Error in Transformed File

**Given**: A transformed file has a syntax error (e.g., invalid comment placement)

**When**: Verification runs (TypeScript/Python syntax check)

**Then**:
1. The verification fails
2. The error is reported with file and line number
3. The transformation is marked as failed
4. The file should be restored from backup and the transformation re-examined

### Scenario 4: Backup Already Exists

**Given**: The `.backup/` directory already exists from a previous genericization attempt

**When**: A new genericization attempt is made

**Then**:
1. The process verifies backup contents match current files
2. If they match, overwrite is allowed
3. If they don't match, the process fails with an error
4. No files are modified until backup verification passes

## Acceptance Criteria

The genericization is complete when:

1. **Backup Integrity**:
   - [ ] `.backup/` directory exists
   - [ ] All modified files have backups in `.backup/`
   - [ ] Backup files match original content

2. **Agent Implementation**:
   - [ ] `agent/src/agent.py` implementation is commented out
   - [ ] `agent/src/agent_template.py` implementation is commented out
   - [ ] All imports remain uncommented
   - [ ] Header comments are present and comprehensive
   - [ ] Python syntax is valid

3. **Components**:
   - [ ] `src/components/procurement-codes.tsx` is entirely commented out
   - [ ] Header comment explains component purpose and usage
   - [ ] TypeScript syntax is valid

4. **Type Definitions**:
   - [ ] `procurement_codes` field is commented out in `src/lib/types.ts`
   - [ ] `your_data` field remains uncommented
   - [ ] Explanatory comments are present

5. **Page Integration**:
   - [ ] `procurement-codes` import is commented out in `src/app/page.tsx`
   - [ ] Explanatory comment is present
   - [ ] TypeScript syntax is valid

6. **Kubernetes Manifests**:
   - [ ] All "dkp-demo" instances replaced with `{{PROJECT_NAME}}`
   - [ ] "dkp-demo.local" replaced with `{{APP_HOSTNAME}}`
   - [ ] "localhost:32000" replaced with `{{REGISTRY_HOST}}`
   - [ ] Configuration comments are present
   - [ ] YAML syntax is valid

7. **Deployment Scripts**:
   - [ ] VM_NAME default is "{{PROJECT_NAME}}-k8s"
   - [ ] Explanatory comments are present
   - [ ] Shell syntax is valid

8. **Agent Configuration**:
   - [ ] Description is "Generic PydanticAI Agent Template"
   - [ ] All dependencies are unchanged

9. **Unchanged Files**:
   - [ ] `README.md` is unchanged
   - [ ] `package.json` is unchanged
   - [ ] `Dockerfile` is unchanged
   - [ ] `docker-compose.yml` is unchanged
   - [ ] `.env.example` is unchanged
   - [ ] `k8s/test-termination-deployment.yaml` is unchanged

10. **Syntax Verification**:
    - [ ] `npx tsc --noEmit` succeeds without errors
    - [ ] `python -m py_compile agent/src/agent.py` succeeds
    - [ ] `python -m py_compile agent/src/agent_template.py` succeeds



## Design

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

## Current Task Context

## Current Task
- 2.1 Comment out `YourState` class in `agent/src/agent.py` — wrap class in comprehensive comment block explaining it's procurement-specific state. Add header comment: "REFERENCE IMPLEMENTATION - COMMENTED OUT FOR GENERICIZATION" with explanation of what state contains (user_input, ai_response, procurement-specific fields) and guidance on adapting for new project (define domain-specific state fields). Verify by running `python -m py_compile agent/src/agent.py` to ensure no syntax errors, and by checking that `YourState` class is commented out using `grep -n "class YourState" agent/src/agent.py | grep -c "#"`.
## Completed Tasks for Git Commit
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
