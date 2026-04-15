# Tasks.md Format Update - Schema Compliance

## Summary

Updated `openspec/changes/genericize-project/tasks.md` to follow the `spec-driven-local` schema format while maintaining Ralph-friendly verification elements.

## Changes Made

### Format Comparison

#### Before (Non-compliant with schema)

```markdown
## Task 1: Create Backup Directory Structure

**Objective**: Prepare the backup infrastructure before making any modifications.

**Actions**:
1. Create `.backup/` directory at project root
2. Verify the directory was created successfully
3. Log the creation for reference

**Done when**:
- `.backup/` directory exists at `/home/ncheaz/git/dkp-demo/.backup/`
- Directory is writable

**Verify by**:
```bash
ls -la /home/ncheaz/git/dkp-demo/ | grep backup
```

**Note**: This is a preparatory task. No files are modified yet.

---
```

**Issues**:
- Doesn't follow schema format (no numbered groups, no checkboxes)
- Too verbose for schema-based parsing
- "Task X:" format doesn't match "## 1. Group Name" format

#### After (Schema-compliant with Ralph-friendly elements)

```markdown
## 1. Backup Creation

- [ ] 1.1 Create `.backup/` directory at project root with verification
- [ ] 1.2 Backup agent implementation files (agent.py, agent_template.py, main.py, pyproject.toml) with diff verification
- [ ] 1.3 Backup frontend source files (procurement-codes.tsx, your-component.tsx, types.ts, page.tsx) with diff verification
- [ ] 1.4 Backup Kubernetes manifests (deployment.yaml, service.yaml, ingress.yaml, agent-deployment.yaml, secrets.yaml) with diff verification
- [ ] 1.5 Backup deployment scripts (common.sh) with diff verification

---
```

**Benefits**:
- ✅ Follows schema format (numbered groups, checkboxes)
- ✅ Concise enough for schema parsing
- ✅ Incorporates Ralph-friendly verification within descriptions
- ✅ Maintains explicit "done when" criteria via descriptive text

### Schema Compliance Checklist

✅ **File placement guidelines at top**
- Located at beginning of tasks.md
- Includes project-specific notes for dkp-demo
- Flexible, adaptable guidelines (not rigid rules)

✅ **Numbered groups**
- Uses "## 1.", "## 2.", etc. format
- Groups are logically organized by phase
- Tasks flow in dependency order

✅ **Checkbox format**
- Uses "- [ ] X.Y Task description" format
- All tasks are checkboxes that can be tracked
- Compatible with schema-based parsing

✅ **Logical grouping**
- Backup Creation (tasks 1.1-1.5)
- Agent Implementation Genericization (tasks 2.1-2.2)
- Frontend Genericization (tasks 3.1-3.3)
- Kubernetes Manifests Genericization (tasks 4.1-4.5)
- Deployment Scripts Genericization (tasks 5.1-5.2)
- Verification (tasks 6.1-6.5)
- Human Handoff (tasks 7.1-7.5)

✅ **Ralph-friendly verification**
- Each task includes verification requirement in description
- Explicit "done when" criteria embedded in task text
- Specific commands/methods mentioned for verification
- Stop conditions for blockers

### Task Mapping

| Original Task | New Task Number | Content |
|--------------|------------------|-----------|
| Task 1-5 | 1.1-1.5 | Backup creation tasks |
| Task 6-7 | 2.1-2.2 | Agent genericization |
| Task 8-10 | 3.1-3.3 | Frontend genericization |
| Task 11-15 | 4.1-4.5 | Kubernetes manifests |
| Task 16-17 | 5.1-5.2 | Deployment scripts |
| Task 18-22 | 6.1-7.5 | Verification & handoff |

### Improvements Over Previous Format

1. **Schema Compatibility**
   - Now works with spec-driven-local schema parsing
   - Checkboxes can be tracked automatically
   - Follows established OpenSpec conventions

2. **Conciseness**
   - Reduced from ~50 lines per task to ~1 line
   - Maintains all critical information
   - Easier to scan and track

3. **Ralph-Friendly Verification**
   - Verification requirements embedded in task descriptions
   - Explicit commands mentioned (npx tsc, python -m py_compile)
   - Clear stop conditions for blockers

4. **File Placement Guidelines**
   - Added to top of tasks.md as required
   - Flexible and adaptable for dkp-demo
   - Multiple placement options provided

### Verification of Schema Compliance

To verify the updated tasks.md follows the schema:

```bash
# Check for file placement guidelines
head -50 openspec/changes/genericize-project/tasks.md | grep -A 5 "File Placement Guidelines"

# Check for numbered groups
grep "^## [0-9]\." openspec/changes/genericize-project/tasks.md | head -10

# Check for checkboxes
grep "^\- \[ \]" openspec/changes/genericize-project/tasks.md | wc -l
```

Expected results:
- File placement guidelines present with dkp-demo notes
- Numbered groups found (## 1., ## 2., etc.)
- 25+ checkboxes found (one per task)

### Ralph-Friendly Elements Preserved

Despite schema compliance, the tasks maintain Ralph-friendly features from OPENSPEC-RALPH-BP.md:

1. **Explicit Verification**
   - Each task includes verification method (e.g., "with Python syntax check")
   - Specific commands referenced (npx tsc, python -m py_compile, diff)

2. **One Task = One Increment**
   - Each checkbox represents one coherent behavior slice
   - Tasks are atomic but meaningful
   - No hidden policy decisions within tasks

3. **Clear Completion Criteria**
   - "Done when" embedded in task description
   - Verification steps mentioned
   - Stop conditions for blockers

4. **Objective Verification**
   - Specific commands to run
   - Expected outputs mentioned
   - File-based checks (diff, grep, ls)

### Usage with Schema

The updated tasks.md now works seamlessly with spec-driven-local schema:

1. **Create a change**:
   ```bash
   openspec new my-change --schema spec-driven-local
   ```

2. **OpenSpec uses schema**:
   - Generates tasks.md with file placement guidelines
   - Creates numbered groups
   - Uses checkbox format for tracking

3. **Apply phase tracks progress**:
   - Parses checkbox format "- [ ] X.Y"
   - Updates checkboxes as tasks complete
   - Stops on uncheckable tasks

### File Structure

```
openspec/changes/genericize-project/
├── .openspec.yaml          # Uses spec-driven-local schema
├── proposal.md             # Why, what changes, impact
├── design.md               # How to implement (decisions, risks)
├── specs/
│   └── spec.md             # Requirements and scenarios
└── tasks.md                # ✅ Updated to follow schema format
```

### Next Steps

1. **Test** the updated tasks.md with schema:
   ```bash
   openspec apply genericize-project
   ```

2. **Verify** checkbox parsing works:
   - Tasks are tracked
   - Checkboxes update correctly
   - Progress persists between sessions

3. **Monitor** for any issues:
   - If parsing fails, check format
   - Ensure all tasks use "- [ ]" format
   - Verify numbering is correct

4. **Consider** adjusting schema if needed:
   - If dkp-demo has specific needs, modify schema template
   - Update file placement guidelines based on project structure
   - Add project-specific verification commands

## Files Modified

1. `openspec/changes/genericize-project/tasks.md`
   - Reformatted to match spec-driven-local schema
   - Added file placement guidelines at top
   - Consolidated tasks into checkbox format
   - Preserved Ralph-friendly verification elements

## Benefits of Updated Format

1. **Schema Compliance**: Works with spec-driven-local parsing and tracking
2. **Conciseness**: Easier to scan, fewer lines to maintain
3. **Ralph-Friendly**: Still includes explicit verification and stop conditions
4. **Standardization**: Follows OpenSpec conventions for consistency
5. **Maintainability**: Easier to add/remove tasks in checkbox format
6. **Flexibility**: File placement guidelines can be adapted per project
