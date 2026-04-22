# File Placement Rules Fix for Ralph Loops

## Problem

When running Ralph loops to complete OpenSpec changes, test files were being created in the root directory instead of the `test/` directory as specified in `openspec/project.md`. The configuration in `openspec/config.yaml` was not being respected by the AI during task implementation.

## Root Cause

The `openspec/config.yaml` file contained detailed rules for file placement (lines 9, 24-31), but these rules were not being included in the context provided to the AI when implementing tasks. The OpenSpec CLI only provided context files defined in the schema (proposal, specs, design, tasks), but did not include the `config.yaml` file.

## Solution

A multi-layered approach was implemented to ensure file placement rules are always available:

### 1. Created a Local Schema

- Forked the `spec-driven` schema to `spec-driven-local` using:
  ```bash
  openspec schema fork spec-driven spec-driven-local
  ```

- Modified the local schema at `openspec/schemas/spec-driven-local/schema.yaml` to:
  - Add a `context` section in the apply configuration to include `../../config.yaml`
  - Add an instruction emphasizing the importance of following file placement rules

### 2. Updated Tasks Template

- Modified `openspec/schemas/spec-driven-local/templates/tasks.md` to include file placement rules at the top of every new tasks.md file
- This ensures that all future changes will have the rules embedded in their task files

### 3. Updated Existing Change

- Updated `openspec/changes/fix-deploy-all-script-issues/.openspec.yaml` to use the new `spec-driven-local` schema
- Added file placement rules to the top of the existing `tasks.md` file

### 4. Updated Workflows and Skills

- Modified `.kilocode/workflows/opsx-apply.md` to explicitly read `openspec/config.yaml`
- Modified `.kilocode/skills/openspec-apply-change/SKILL.md` with the same instruction
- This ensures that both the workflow and skill versions will read the configuration

## File Placement Rules

The following rules are now enforced:

### Test Files
- **Placement**: All test files MUST be placed in the `test/` directory at project root
- **Forbidden locations**: DO NOT create test files in the change directory, agent/ directory, or project root
- **File patterns**: test*.py, debug*.py, check*.py, measure*.py, performance*.py, verify*.py, validate*.py
- **Naming conventions**: Use appropriate prefixes (test_, debug_, check_, measure_, performance_, verify_, validate_)
- **Example**: Task "Write unit tests for component extraction" → Create: test/test_component_extraction.py

### Documentation Files
- **Placement**: All .md documentation files MUST be placed in the `ralph-docs/` directory at project root
- **Forbidden locations**: DO NOT create .md documentation files in the project root (except core files: README.md, CHANGELOG.md, SETUP.md, TESTING.md, DEPENDENCIES.md, deploy_log.md)
- **Examples**: Task "Create deployment summary" → Create: ralph-docs/DEPLOYMENT_SUMMARY.md

## Verification

To verify the fix is working:

1. Create a new change:
   ```bash
   openspec new <change-name>
   ```

2. Check that the change uses the local schema by examining the `.openspec.yaml` file in the change directory

3. When implementing tasks, verify that:
   - The tasks.md file includes the file placement rules at the top
   - Test files are created in the `test/` directory
   - Documentation files are created in the `ralph-docs/` directory

## Future Changes

For any new changes created after this fix:
- The `spec-driven-local` schema will be used by default (can be configured in `openspec/config.yaml`)
- All new `tasks.md` files will automatically include the file placement rules
- The AI will have access to the configuration rules through multiple channels (schema, workflow, skill, and tasks.md)

## Files Modified

1. `openspec/schemas/spec-driven-local/schema.yaml` - New local schema with context configuration
2. `openspec/schemas/spec-driven-local/templates/tasks.md` - Updated template with file placement rules
3. `openspec/changes/fix-deploy-all-script-issues/.openspec.yaml` - Updated to use local schema
4. `openspec/changes/fix-deploy-all-script-issues/tasks.md` - Added file placement rules
5. `.kilocode/workflows/opsx-apply.md` - Added instruction to read config.yaml
6. `.kilocode/skills/openspec-apply-change/SKILL.md` - Added instruction to read config.yaml

## Notes

- The local schema approach ensures that project-specific rules are always available without modifying the global OpenSpec installation
- Multiple layers of defense (schema, workflow, skill, and tasks.md) ensure the rules are followed even if one mechanism fails
- The fix is backward compatible and doesn't break existing changes
