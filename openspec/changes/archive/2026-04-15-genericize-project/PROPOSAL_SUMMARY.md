# OpenSpec Genericization Proposal - Summary

## What Was Created

I've created a complete Ralph-friendly OpenSpec proposal package for genericizing your project template. The proposal is located at:

```
openspec/changes/genericize-project/
├── proposal.md          # Why this change exists, scope, non-goals
├── design.md            # Implementation approach and strategy
├── specs/
│   └── spec.md         # Required behaviors and scenarios
└── tasks.md            # Ordered execution plan (22 tasks)
```

## Proposal Overview

**Problem**: The codebase contains project-specific references (dkp-demo, procurement) that limit its reusability as a template.

**Solution**: Comment out domain-specific logic and replace hardcoded values with placeholders while preserving implementation as reference examples.

## Key Features of This Proposal

### Ralph-Friendly Design

Following the best practices from `hidden/OPENSPEC-RALPH-BP.md`:

✅ **Coherent increments**: Each task is one atomic behavior slice, not tiny mechanical subtasks

✅ **Explicit verification**: Every task has clear "Done when" and "Verify by" criteria

✅ **No hidden decisions**: The design settles all algorithms, placeholder format, and commenting strategy

✅ **Human handoffs documented**: Manual tasks are separated from autonomous execution

✅ **Fresh-session safe**: All critical guidance lives in artifacts, not chat history

### What Gets Genericized

**Removed/Commented Out**:
- Agent implementation logic (preserved as examples)
- Procurement-codes component (preserved as reference)
- Procurement types (preserved as examples)
- Hardcoded project names in Kubernetes manifests
- VM/cluster names in deployment scripts
- Project-specific descriptions in package files

**Replaced with Placeholders**:
- `{{PROJECT_NAME}}` - for project identifiers
- `{{APP_HOSTNAME}}` - for ingress hostnames
- `{{REGISTRY_HOST}}` - for container registry

**Left Unchanged**:
- README.md (already generic)
- package.json (can remain as-is)
- Docker configurations (already generic)
- Test deployment YAML (for testing)
- Environment examples (already generic)

### Backup Strategy

All modifications include complete backups in `.backup/` directory, making rollback easy:

```bash
# Restore specific file
cp .backup/path/to/file path/to/file

# Restore all files
cp -r .backup/* .

# Remove backups after confirming success
rm -rf .backup
```

## Task Breakdown

The proposal includes **22 tasks** organized into logical phases:

### Phase 1: Backup Creation (Tasks 1-5)
- Create backup directory structure
- Back up all files before modification

### Phase 2: Agent Genericization (Tasks 6-7)
- Comment out implementation in agent.py and agent_template.py
- Preserve imports and model configuration

### Phase 3: Frontend Genericization (Tasks 8-10)
- Comment out procurement-codes component
- Comment out procurement types
- Comment out component imports

### Phase 4: Kubernetes Genericization (Tasks 11-15)
- Replace hardcoded values with placeholders
- Add configuration comments
- Genericize all manifests except test deployment

### Phase 5: Script Genericization (Tasks 16-17)
- Genericize VM name in deployment scripts
- Update agent package description

### Phase 6: Verification (Tasks 18-22)
- TypeScript compilation check
- Python compilation check
- Backup verification
- Unchanged file verification
- Summary report generation

## How to Use This Proposal

### Option 1: Run with Ralph Loop

If you have Ralph configured, you can run this proposal autonomously:

```bash
# Using OpenSpec with Ralph (recommended)
ralph --change genericize-project
```

### Option 2: Manual Execution

Execute tasks one by one, verifying each step:

```bash
# Read the proposal
cat openspec/changes/genericize-project/proposal.md

# Follow the tasks in order
cat openspec/changes/genericize-project/tasks.md

# After completing all tasks, verify
npx tsc --noEmit
cd agent && python -m py_compile src/*.py
```

## Additional Items to Consider

Based on my exploration, I found these potential items you might want to genericize or comment out:

### 1. **Deployment Scripts** (k8s/setup-secrets.sh)
- Contains hardcoded references to "dkp-demo"
- Has multipass/microk8s-specific commands
- **Recommendation**: Add to the proposal if you use this script
- **Current Status**: Not in proposal (you didn't mention it)

### 2. **Environment-Specific Paths**
- The deployment scripts have paths like `/tmp/deploy-*.log`
- **Recommendation**: These are probably fine as-is (generic paths)
- **Current Status**: Not in proposal (already generic enough)

### 3. **Package Name**
- `package.json` name is "pydantic-ai-starter"
- **Recommendation**: This can remain as-is for npm purposes
- **Current Status**: Not in proposal (already acceptable)

### 4. **Docker Image Tags**
- Some references to `:latest` tags
- **Recommendation**: These are generic practices, not project-specific
- **Current Status**: Not in proposal (already generic)

### 5. **CopilotKit Configuration**
- Sidebar labels and suggestions in `src/app/page.tsx`
- **Recommendation**: These are generic placeholders
- **Current Status**: Not in proposal (already generic enough)

## Should I Add These to the Proposal?

Please let me know if you want me to add any of these items to the proposal:

1. **k8s/setup-secrets.sh** - Genericize this script (it has dkp-demo references and multipass commands)
2. **Other deployment scripts** - Check all scripts in `deploy_scripts/` for hardcoded values
3. **Additional Kubernetes manifests** - Any other YAML files I might have missed
4. **Environment configuration** - Any other env-specific configuration
5. **Documentation updates** - Update README to reflect genericized nature

## Next Steps

1. **Review the proposal**: Read through `proposal.md`, `design.md`, and `specs/spec.md`
2. **Approve or modify**: Let me know if you want any changes to the proposal
3. **Add additional items**: Tell me if you want to add any of the items above
4. **Execute**: Run the proposal manually or with Ralph loop
5. **Verify**: After completion, run syntax checks and test the template

## File Locations

All artifacts are in:
```
/home/ncheaz/git/dkp-demo/openspec/changes/genericize-project/
```

Review each file:
- `proposal.md` - Problem statement, scope, success criteria
- `design.md` - Implementation strategy, file-by-file approach
- `specs/spec.md` - Detailed requirements, scenarios, acceptance criteria
- `tasks.md` - 22 ordered tasks with verification steps

## Questions?

If you need clarification on any aspect of the proposal, ask! I can:
- Explain why certain decisions were made
- Modify the proposal to include additional items
- Reorganize tasks if needed
- Add more verification steps
- Provide implementation guidance for specific tasks
