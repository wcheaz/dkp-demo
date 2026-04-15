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
