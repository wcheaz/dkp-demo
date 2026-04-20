# spec-driven-local Schema - Genericization for dkp-demo

## Summary

The `spec-driven-local` schema has been analyzed and updated to be more flexible and appropriate for the dkp-demo project.

## Changes Made

### 1. Updated templates/tasks.md

**Location**: `openspec/schemas/spec-driven-local/templates/tasks.md`

**Changes**:
- Converted "File Placement Rules (CRITICAL)" to "File Placement Guidelines (PROJECT-SPECIFIC - Adjust as Needed)"
- Changed mandatory requirements ("MUST be placed", "FORBIDDEN locations") to recommendations
- Added multiple placement options for different project structures
- Added examples for Python, TypeScript, and Node.js projects
- Added project-specific notes for dkp-demo
- Emphasized that guidelines should be adapted based on project needs

**Rationale**:
- The original rules were too prescriptive and specific to the previous project
- dkp-demo doesn't currently have test/ or ralph-docs/ directories
- Providing multiple options allows flexibility for different project structures
- Guidelines should be adaptable, not rigid rules

### 2. Updated schema.yaml

**Location**: `openspec/schemas/spec-driven-local/schema.yaml`

**Changes**:
- Updated instruction text to emphasize that templates/tasks.md contains generic guidelines
- Removed reference to specific "rules for test files and documentation files"
- Added note that guidelines should be adapted for specific project structure

**Rationale**:
- Clarifies that file placement is context-dependent
- Encourages adaptation to project needs
- Removes implication of rigid requirements

## Analysis of Templates

### templates/proposal.md
**Status**: ✅ Already Generic
- Contains only placeholder comments and section headers
- No project-specific content
- No changes needed

### templates/design.md
**Status**: ✅ Already Generic
- Contains only placeholder comments and section headers
- No project-specific content
- No changes needed

### templates/spec.md
**Status**: ✅ Already Generic
- Contains only placeholder comments and section headers
- No project-specific content
- No changes needed

### templates/tasks.md
**Status**: ✅ Updated
- Was too prescriptive for the previous project
- Now provides flexible guidelines with multiple options
- Includes project-specific context for dkp-demo

## Current State

The spec-driven-local schema is now suitable for use with dkp-demo:

- **Proposal template**: Generic, ready for use
- **Design template**: Generic, ready for use
- **Spec template**: Generic, ready for use
- **Tasks template**: Flexible, with adaptable guidelines
- **Schema configuration**: Updated to reflect flexible approach

## Recommendations for dkp-demo

### Test Structure (When Ready)

When you add a test suite to dkp-demo, choose a structure:

**Option 1: Root test/ directory**
```
dkp-demo/
├── test/
│   ├── test_frontend.py      # Frontend tests
│   ├── test_backend.py       # Agent tests
│   └── test_deployment.py    # Deployment verification
```

**Option 2: tests/ directory (Python convention)**
```
dkp-demo/
├── tests/
│   ├── test_frontend.py
│   ├── test_backend.py
│   └── test_deployment.py
```

**Option 3: Inline test directories**
```
dkp-demo/
├── src/
│   └── __tests__/        # Frontend tests
├── agent/
│   └── tests/            # Backend tests
└── test/                 # Integration/deployment tests
```

### Documentation Structure

**Permanent documentation**: Use `docs/` directory
```
dkp-demo/
├── docs/
│   ├── api.md             # API documentation
│   ├── deployment.md       # Deployment guide
│   └── development.md     # Developer guide
```

**Temporary/generated documentation**: Use `ralph-docs/` directory (already gitignored)
```
dkp-demo/
├── ralph-docs/           # Generated docs (not committed)
│   ├── DEPLOYMENT_SUMMARY.md
│   └── VERIFICATION_RESULTS.md
```

## How to Use spec-driven-local

The spec-driven-local schema can be used as the default for new changes:

### Option 1: Set as default in config.yaml

Edit `openspec/config.yaml`:
```yaml
schema: spec-driven-local
```

### Option 2: Use explicitly for each change

When creating a new change:
```bash
openspec new <change-name> --schema spec-driven-local
```

### Option 3: Override default temporarily

```bash
openspec new <change-name> --schema spec-driven-local
```

## Comparison with Genericize-Project Proposal

The spec-driven-local schema takes a different approach than the genericize-project proposal:

### spec-driven-local approach:
- **Template-driven**: Uses structured templates for consistency
- **Standardized**: Same format for all changes
- **Lightweight**: Minimal guidance in templates
- **File placement**: Flexible guidelines (after update)
- **Best for**: Routine changes following established patterns

### genericize-project approach:
- **Detailed**: Comprehensive documentation in each phase
- **Ralph-optimized**: Explicit verification and "done when" criteria
- **Heavyweight**: More guidance, more artifacts
- **Verification-focused**: Strong emphasis on rollback and validation
- **Best for**: Complex, high-risk, or novel changes

## Recommendation

For dkp-demo, consider:

1. **Use spec-driven-local for routine changes**:
   - Bug fixes
   - Small features
   - Documentation updates
   - Configuration changes

2. **Use detailed proposals for complex changes**:
   - Architectural changes
   - Major new features
   - Breaking changes
   - Migrations or refactorings

3. **Combine approaches when useful**:
   - Use spec-driven-local templates
   - Add explicit verification steps in tasks.md
   - Include rollback instructions in design.md

## Verification

To verify the genericized spec-driven-local schema:

1. **Create a test change**:
   ```bash
   openspec new test-change
   ```

2. **Check the generated tasks.md**:
   - File placement guidelines are present
   - Guidelines are flexible (not "MUST", "FORBIDDEN")
   - dkp-demo specific notes are included

3. **Implement a task**:
   - Verify task checkboxes are recognized
   - Test file creation follows chosen structure
   - Documentation placement works as expected

4. **Complete the change**:
   ```bash
   openspec apply test-change
   ```

## Files Modified

1. `openspec/schemas/spec-driven-local/templates/tasks.md` - Updated to flexible guidelines
2. `openspec/schemas/spec-driven-local/schema.yaml` - Updated instruction text

## Files Analyzed (No Changes Needed)

1. `openspec/schemas/spec-driven-local/templates/proposal.md` - Already generic
2. `openspec/schemas/spec-driven-local/templates/design.md` - Already generic
3. `openspec/schemas/spec-driven-local/templates/spec.md` - Already generic

## Next Steps

1. **Test the schema** by creating a small change
2. **Choose a test structure** for dkp-demo when ready
3. **Update these guidelines** once test structure is decided
4. **Consider customizing** templates if specific patterns emerge
5. **Document your conventions** in openspec/config.yaml if you choose a specific approach
