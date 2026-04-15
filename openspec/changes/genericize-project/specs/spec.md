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
