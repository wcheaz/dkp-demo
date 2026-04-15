# Genericization Tasks

This document provides an ordered execution plan for genericizing the project template. Each task represents one coherent increment of work with explicit verification criteria.

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

## Task 2: Backup Agent Implementation Files

**Objective**: Create backups of all agent-related source files before modification.

**Actions**:
1. Create directory structure in `.backup/agent/`
2. Copy `agent/src/agent.py` to `.backup/agent/src/agent.py`
3. Copy `agent/src/agent_template.py` to `.backup/agent/src/agent_template.py`
4. Copy `agent/src/main.py` to `.backup/agent/src/main.py`
5. Copy `agent/pyproject.toml` to `.backup/agent/pyproject.toml`
6. Verify all backups exist and are readable

**Done when**:
- All 4 agent files have corresponding backups
- Backup files match original files (use `diff` to verify)

**Verify by**:
```bash
diff agent/src/agent.py .backup/agent/src/agent.py && \
diff agent/src/agent_template.py .backup/agent/src/agent_template.py && \
diff agent/src/main.py .backup/agent/src/main.py && \
diff agent/pyproject.toml .backup/agent/pyproject.toml && \
echo "All agent backups verified"
```

**Stop and hand off if**:
- Any file cannot be copied (permissions, disk space, etc.)
- Backup directory creation fails

---

## Task 3: Backup Frontend Source Files

**Objective**: Create backups of all frontend source files before modification.

**Actions**:
1. Create directory structure in `.backup/src/`
2. Copy `src/components/procurement-codes.tsx` to `.backup/src/components/procurement-codes.tsx`
3. Copy `src/components/your-component.tsx` to `.backup/src/components/your-component.tsx`
4. Copy `src/lib/types.ts` to `.backup/src/lib/types.ts`
5. Copy `src/app/page.tsx` to `.backup/src/app/page.tsx`
6. Verify all backups exist and are readable

**Done when**:
- All 4 frontend files have corresponding backups
- Backup files match original files (use `diff` to verify)

**Verify by**:
```bash
diff src/components/procurement-codes.tsx .backup/src/components/procurement-codes.tsx && \
diff src/components/your-component.tsx .backup/src/components/your-component.tsx && \
diff src/lib/types.ts .backup/src/lib/types.ts && \
diff src/app/page.tsx .backup/src/app/page.tsx && \
echo "All frontend backups verified"
```

**Stop and hand off if**:
- Any file cannot be copied
- Backup directory creation fails

---

## Task 4: Backup Kubernetes Manifests

**Objective**: Create backups of all Kubernetes manifest files before modification.

**Actions**:
1. Create directory structure in `.backup/k8s/`
2. Copy `k8s/deployment.yaml` to `.backup/k8s/deployment.yaml`
3. Copy `k8s/service.yaml` to `.backup/k8s/service.yaml`
4. Copy `k8s/ingress.yaml` to `.backup/k8s/ingress.yaml`
5. Copy `k8s/agent-deployment.yaml` to `.backup/k8s/agent-deployment.yaml`
6. Copy `k8s/secrets.yaml` to `.backup/k8s/secrets.yaml`
7. Verify all backups exist and are readable

**Done when**:
- All 5 Kubernetes manifest files have corresponding backups
- Backup files match original files (use `diff` to verify)

**Verify by**:
```bash
diff k8s/deployment.yaml .backup/k8s/deployment.yaml && \
diff k8s/service.yaml .backup/k8s/service.yaml && \
diff k8s/ingress.yaml .backup/k8s/ingress.yaml && \
diff k8s/agent-deployment.yaml .backup/k8s/agent-deployment.yaml && \
diff k8s/secrets.yaml .backup/k8s/secrets.yaml && \
echo "All Kubernetes backups verified"
```

**Note**: Do NOT backup `k8s/test-termination-deployment.yaml` as it will remain unchanged.

**Stop and hand off if**:
- Any file cannot be copied

---

## Task 5: Backup Deployment Scripts

**Objective**: Create backup of deployment scripts before modification.

**Actions**:
1. Create directory structure in `.backup/deploy_scripts/`
2. Copy `deploy_scripts/common.sh` to `.backup/deploy_scripts/common.sh`
3. Verify backup exists and is readable

**Done when**:
- `deploy_scripts/common.sh` has a corresponding backup
- Backup file matches original file (use `diff` to verify)

**Verify by**:
```bash
diff deploy_scripts/common.sh .backup/deploy_scripts/common.sh && \
echo "Deployment script backup verified"
```

**Stop and hand off if**:
- File cannot be copied

---

## Task 6: Comment Out Agent Implementation in agent.py

**Objective**: Comment out all implementation logic in `agent/src/agent.py` while preserving imports.

**Actions**:
1. Add comprehensive header comment explaining the genericization
2. Comment out the entire `YourState` class definition (lines 18-23)
3. Comment out the entire `StateDeps` class definition (lines 27-31)
4. Comment out the agent creation line (line 35-37)
5. Comment out the `your_tool` function (lines 41-54)
6. Comment out the `validate_result` function (lines 58-62)
7. Keep all imports (lines 1-6) unchanged
8. Keep model configuration (lines 11-14) unchanged
9. Add inline comments explaining each commented section

**Done when**:
- All implementation code is commented out
- All imports remain uncommented
- Model configuration remains uncommented
- Header comment is present at the top
- Python syntax is valid

**Verify by**:
```bash
cd agent && python -m py_compile src/agent.py
```

Expected: No output (successful compilation)

**Stop and hand off if**:
- Python syntax check fails
- File cannot be written

---

## Task 7: Comment Out Agent Implementation in agent_template.py

**Objective**: Comment out all implementation logic in `agent/src/agent_template.py` while preserving imports.

**Actions**:
1. Add comprehensive header comment explaining the genericization
2. Comment out the entire `YourState` class definition
3. Comment out the entire `StateDeps` class definition
4. Comment out the agent creation line
5. Comment out the `your_tool` function
6. Comment out the `validate_result` function
7. Keep all imports unchanged
8. Keep model configuration unchanged
9. Add inline comments explaining each commented section

**Done when**:
- All implementation code is commented out
- All imports remain uncommented
- Model configuration remains uncommented
- Header comment is present at the top
- Python syntax is valid

**Verify by**:
```bash
cd agent && python -m py_compile src/agent_template.py
```

Expected: No output (successful compilation)

**Stop and hand off if**:
- Python syntax check fails
- File cannot be written

---

## Task 8: Comment Out Procurement Codes Component

**Objective**: Comment out the entire `src/components/procurement-codes.tsx` component.

**Actions**:
1. Add comprehensive header comment explaining:
   - What the component does (displays and exports procurement codes)
   - How it integrates with state
   - Dependencies (xlsx library)
   - How to adapt for other data types
2. Comment out the `ProcurementCodesProps` interface (lines 4-7)
3. Comment out the entire `ProcurementCodes` function (lines 9-133)
4. Keep the file intact (do not delete)

**Done when**:
- Entire component code is commented out
- Header comment explains component purpose and usage
- TypeScript syntax is valid

**Verify by**:
```bash
npx tsc --noEmit
```

Expected: No TypeScript errors

**Stop and hand off if**:
- TypeScript compilation fails
- File cannot be written

---

## Task 9: Comment Out Procurement Types in types.ts

**Objective**: Comment out procurement-specific type definitions in `src/lib/types.ts`.

**Actions**:
1. Keep `YourDataType` type unchanged (already generic)
2. Comment out the `procurement_codes` field in `AgentState` type (this field doesn't currently exist, but add a comment about it)
3. Add explanatory comment about defining project-specific types
4. Add example of how to add procurement-specific types when needed

**Done when**:
- `YourDataType` remains unchanged
- Explanatory comment about procurement_codes is present
- Example type definition is commented out for reference
- TypeScript syntax is valid

**Verify by**:
```bash
npx tsc --noEmit
```

Expected: No TypeScript errors

**Stop and hand off if**:
- TypeScript compilation fails
- File cannot be written

---

## Task 10: Comment Out Procurement Component Import in page.tsx

**Objective**: Comment out the import of `procurement-codes.tsx` in `src/app/page.tsx`.

**Actions**:
1. Comment out the import statement for `procurement-codes.tsx` (note: this import may not exist in the current file, check first)
2. Add explanatory comment about component integration
3. Add guidance on how to import custom components
4. Do NOT modify the usage of `YourComponent`

**Done when**:
- Import of `procurement-codes.tsx` is commented out (if it exists)
- Explanatory comment is present
- `YourComponent` usage remains unchanged
- TypeScript syntax is valid

**Verify by**:
```bash
npx tsc --noEmit
```

Expected: No TypeScript errors

**Stop and hand off if**:
- TypeScript compilation fails
- File cannot be written

---

## Task 11: Genericize Kubernetes Deployment Manifest

**Objective**: Replace hardcoded "dkp-demo" with `{{PROJECT_NAME}}` in `k8s/deployment.yaml`.

**Actions**:
1. Add configuration comment at the top explaining required replacements
2. Replace "dkp-demo" with `{{PROJECT_NAME}}` in metadata.name (line 4)
3. Replace "dkp-demo" with `{{PROJECT_NAME}}` in selector matchLabels (line 10)
4. Replace "dkp-demo" with `{{PROJECT_NAME}}` in template labels (line 14)
5. Replace "dkp-demo" with `{{PROJECT_NAME}}` in container name (line 17)
6. Replace "localhost:32000" with `{{REGISTRY_HOST}}` in image reference (line 18)
7. Replace "dkp-demo" with `{{PROJECT_NAME}}` in secretRef name (line 26)
8. Replace "dkp-demo" with `{{PROJECT_NAME}}` in configMapRef name (line 28)
9. Add inline comments for each replaced value

**Done when**:
- No instances of "dkp-demo" remain in the file
- All instances are replaced with `{{PROJECT_NAME}}` or `{{REGISTRY_HOST}}`
- Configuration comment is present at the top
- YAML syntax is valid

**Verify by**:
```bash
grep -q "dkp-demo" k8s/deployment.yaml && echo "FAILED: dkp-demo still present" || echo "SUCCESS: All dkp-demo replaced"
```

Expected: "SUCCESS: All dkp-demo replaced"

**Stop and hand off if**:
- YAML syntax is invalid
- File cannot be written

---

## Task 12: Genericize Kubernetes Service Manifest

**Objective**: Replace hardcoded "dkp-demo" with `{{PROJECT_NAME}}` in `k8s/service.yaml`.

**Actions**:
1. Add configuration comment at the top explaining required replacements
2. Replace "dkp-demo" with `{{PROJECT_NAME}}` in metadata.name (line 17)
3. Replace "dkp-demo" with `{{PROJECT_NAME}}` in selector app (line 24)
4. Replace "dkp-demo" with `{{PROJECT_NAME}}` in metadata labels app (line 20)
5. Add inline comments for each replaced value

**Done when**:
- No instances of "dkp-demo" remain in the file
- All instances are replaced with `{{PROJECT_NAME}}`
- Configuration comment is present at the top
- YAML syntax is valid

**Verify by**:
```bash
grep -q "dkp-demo" k8s/service.yaml && echo "FAILED: dkp-demo still present" || echo "SUCCESS: All dkp-demo replaced"
```

Expected: "SUCCESS: All dkp-demo replaced"

**Stop and hand off if**:
- YAML syntax is invalid
- File cannot be written

---

## Task 13: Genericize Kubernetes Ingress Manifest

**Objective**: Replace hardcoded values with placeholders in `k8s/ingress.yaml`.

**Actions**:
1. Add configuration comment at the top explaining required replacements
2. Replace "dkp-demo" with `{{PROJECT_NAME}}` in the header comment (line 1)
3. Replace "dkp-demo" with `{{PROJECT_NAME}}" in metadata.name (line 18)
4. Replace "dkp-demo" with `{{PROJECT_NAME}}" in metadata labels app (line 21)
5. Replace "dkp-demo.local" with `{{APP_HOSTNAME}}` in host (line 36)
6. Replace "dkp-demo" with `{{PROJECT_NAME}}" in service name (line 43)
7. Add inline comments for each replaced value

**Done when**:
- No instances of "dkp-demo" or "dkp-demo.local" remain in the file
- All instances are replaced with `{{PROJECT_NAME}}` or `{{APP_HOSTNAME}}`
- Configuration comment is present at the top
- YAML syntax is valid

**Verify by**:
```bash
grep -qE "dkp-demo|dkp-demo\.local" k8s/ingress.yaml && echo "FAILED: dkp-demo still present" || echo "SUCCESS: All placeholders replaced"
```

Expected: "SUCCESS: All placeholders replaced"

**Stop and hand off if**:
- YAML syntax is invalid
- File cannot be written

---

## Task 14: Genericize Kubernetes Agent Deployment Manifest

**Objective**: Replace hardcoded "dkp-demo" with `{{PROJECT_NAME}}` in `k8s/agent-deployment.yaml`.

**Actions**:
1. Add configuration comment at the top explaining required replacements
2. Replace "localhost:32000" with `{{REGISTRY_HOST}}` in image reference (line 18)
3. Replace "dkp-demo" with `{{PROJECT_NAME}}" in secretRef name (line 23)
4. Replace "dkp-demo" with `{{PROJECT_NAME}}" in configMapRef name (line 25)
5. Add inline comments for each replaced value

**Note**: The agent deployment does not have "dkp-demo" in metadata or labels, only in references to secrets and configmaps.

**Done when**:
- No instances of "dkp-demo" or "localhost:32000" remain in the file
- All instances are replaced with `{{PROJECT_NAME}}` or `{{REGISTRY_HOST}}`
- Configuration comment is present at the top
- YAML syntax is valid

**Verify by**:
```bash
grep -qE "dkp-demo|localhost:32000" k8s/agent-deployment.yaml && echo "FAILED: placeholders still present" || echo "SUCCESS: All placeholders replaced"
```

Expected: "SUCCESS: All placeholders replaced"

**Stop and hand off if**:
- YAML syntax is invalid
- File cannot be written

---

## Task 15: Genericize Kubernetes Secrets Manifest

**Objective**: Replace hardcoded "dkp-demo" with `{{PROJECT_NAME}}` in `k8s/secrets.yaml`.

**Actions**:
1. Add configuration comment at the top explaining required replacements
2. Replace "dkp-demo" with `{{PROJECT_NAME}}" in secret metadata.name (line 4)
3. Replace "dkp-demo" with `{{PROJECT_NAME}}" in secret labels app (line 7)
4. Replace "dkp-demo" with `{{PROJECT_NAME}}" in ConfigMap metadata.name (line 20)
5. Replace "dkp-demo" with `{{PROJECT_NAME}}" in ConfigMap labels app (line 23)
6. Replace "dkp-demo-k8s" with "{{PROJECT_NAME}}-k8s" in setup-secrets.sh reference (line 237)
7. Add inline comments for each replaced value

**Done when**:
- No instances of "dkp-demo" remain in the file
- All instances are replaced with `{{PROJECT_NAME}}`
- Configuration comment is present at the top
- YAML syntax is valid

**Verify by**:
```bash
grep -q "dkp-demo" k8s/secrets.yaml && echo "FAILED: dkp-demo still present" || echo "SUCCESS: All dkp-demo replaced"
```

Expected: "SUCCESS: All dkp-demo replaced"

**Stop and hand off if**:
- YAML syntax is invalid
- File cannot be written

---

## Task 16: Genericize Deployment Script VM Name

**Objective**: Replace hardcoded VM name with generic placeholder in `deploy_scripts/common.sh`.

**Actions**:
1. Replace default VM_NAME "dkp-demo-k8s" with "{{PROJECT_NAME}}-k8s" (line 26)
2. Add explanatory comment about environment-specific deployment
3. Add comment noting multipass/microk8s specificity
4. Keep all script logic unchanged

**Done when**:
- VM_NAME default value is "{{PROJECT_NAME}}-k8s"
- Explanatory comment is present
- Shell syntax is valid

**Verify by**:
```bash
grep "VM_NAME.*{{PROJECT_NAME}}-k8s" deploy_scripts/common.sh && echo "SUCCESS: VM_NAME genericized" || echo "FAILED: VM_NAME not genericized"
```

Expected: "SUCCESS: VM_NAME genericized"

**Stop and hand off if**:
- Shell syntax is invalid
- File cannot be written

---

## Task 17: Genericize Agent Package Description

**Objective**: Replace project-specific description with generic description in `agent/pyproject.toml`.

**Actions**:
1. Replace description "Procurement Agent" with "Generic PydanticAI Agent Template" (line 5)
2. Keep all dependencies unchanged
3. Keep version number unchanged
4. Keep all other fields unchanged

**Done when**:
- Description is "Generic PydanticAI Agent Template"
- All dependencies remain unchanged
- TOML syntax is valid

**Verify by**:
```bash
grep "description.*Generic PydanticAI Agent Template" agent/pyproject.toml && echo "SUCCESS: Description genericized" || echo "FAILED: Description not genericized"
```

Expected: "SUCCESS: Description genericized"

**Stop and hand off if**:
- TOML syntax is invalid
- File cannot be written

---

## Task 18: Verify All TypeScript Files Compile

**Objective**: Run final TypeScript compilation check to ensure all frontend changes are syntactically valid.

**Actions**:
1. Run `npx tsc --noEmit` from project root
2. Check for any TypeScript errors
3. Report any errors found

**Done when**:
- TypeScript compilation succeeds with no errors

**Verify by**:
```bash
npx tsc --noEmit && echo "SUCCESS: All TypeScript files compile" || echo "FAILED: TypeScript errors present"
```

Expected: "SUCCESS: All TypeScript files compile"

**Stop and hand off if**:
- TypeScript compilation fails
  - Report the specific file and error
  - Suggest restoring from backup and re-examining the transformation

---

## Task 19: Verify All Python Files Compile

**Objective**: Run final Python compilation check to ensure all agent changes are syntactically valid.

**Actions**:
1. Run `python -m py_compile agent/src/agent.py`
2. Run `python -m py_compile agent/src/agent_template.py`
3. Check for any Python syntax errors
4. Report any errors found

**Done when**:
- Both Python files compile successfully with no syntax errors

**Verify by**:
```bash
cd agent && python -m py_compile src/agent.py && python -m py_compile src/agent_template.py && echo "SUCCESS: All Python files compile" || echo "FAILED: Python syntax errors present"
```

Expected: "SUCCESS: All Python files compile"

**Stop and hand off if**:
- Python compilation fails
  - Report the specific file and error
  - Suggest restoring from backup and re-examining the transformation

---

## Task 20: Verify All Backups Exist and Match

**Objective**: Final verification that all modified files have complete backups.

**Actions**:
1. Verify all backed up files exist
2. Run diff for each modified file against its backup
3. Confirm all backups match original files
4. Generate summary report

**Done when**:
- All modified files have corresponding backups
- All backup files match original files
- Summary report is generated

**Verify by**:
```bash
echo "=== Backup Verification ===" && \
diff agent/src/agent.py .backup/agent/src/agent.py && \
diff agent/src/agent_template.py .backup/agent/src/agent_template.py && \
diff agent/src/main.py .backup/agent/src/main.py && \
diff agent/pyproject.toml .backup/agent/pyproject.toml && \
diff src/components/procurement-codes.tsx .backup/src/components/procurement-codes.tsx && \
diff src/components/your-component.tsx .backup/src/components/your-component.tsx && \
diff src/lib/types.ts .backup/src/lib/types.ts && \
diff src/app/page.tsx .backup/src/app/page.tsx && \
diff k8s/deployment.yaml .backup/k8s/deployment.yaml && \
diff k8s/service.yaml .backup/k8s/service.yaml && \
diff k8s/ingress.yaml .backup/k8s/ingress.yaml && \
diff k8s/agent-deployment.yaml .backup/k8s/agent-deployment.yaml && \
diff k8s/secrets.yaml .backup/k8s/secrets.yaml && \
diff deploy_scripts/common.sh .backup/deploy_scripts/common.sh && \
echo "SUCCESS: All backups verified and match originals"
```

Expected: "SUCCESS: All backups verified and match originals"

**Note**: All diffs should fail (showing differences) because files have been modified. This confirms the backups are the original versions.

**Stop and hand off if**:
- Any backup file is missing
- Any backup file is corrupted or unreadable

---

## Task 21: Verify Unchanged Files Remain Unchanged

**Objective**: Confirm that files marked as unchanged have not been modified.

**Actions**:
1. Compare `README.md` with backup (should not have a backup, but verify it's unchanged from git)
2. Compare `package.json` with backup (should not have a backup, but verify it's unchanged from git)
3. Compare `Dockerfile` with backup (should not have a backup, but verify it's unchanged from git)
4. Compare `docker-compose.yml` with backup (should not have a backup, but verify it's unchanged from git)
5. Compare `.env.example` with backup (should not have a backup, but verify it's unchanged from git)
6. Compare `k8s/test-termination-deployment.yaml` with backup (should not have a backup, but verify it's unchanged from git)

**Done when**:
- All files marked as unchanged are verified as unchanged
- Summary report is generated

**Verify by**:
```bash
echo "=== Unchanged Files Verification ===" && \
git status --porcelain README.md package.json Dockerfile docker-compose.yml .env.example k8s/test-termination-deployment.yaml && \
echo "If no files are listed above, all unchanged files are confirmed"
```

Expected: No files listed (all are unchanged)

**Stop and hand off if**:
- Any unchanged file has been modified
  - Report which file was modified
  - Suggest restoring from git

---

## Task 22: Generate Final Summary Report

**Objective**: Generate a comprehensive summary of the genericization process.

**Actions**:
1. Count total files modified
2. Count total files backed up
3. List all placeholders introduced (with counts)
4. Verify all syntax checks passed
5. Generate summary document in `.backup/GENERICIZATION_SUMMARY.md`

**Done when**:
- Summary report is generated
- All transformations are documented

**Verify by**:
```bash
cat .backup/GENERICIZATION_SUMMARY.md
```

Expected: Comprehensive summary document with:
- Files modified count
- Files backed up count
- Placeholder replacements count
- Syntax check results
- Rollback instructions

**Stop and hand off if**:
- Summary report cannot be generated
- File cannot be written

---

## Human Handoff Tasks

These tasks are documented for human action but are NOT part of the automated loop:

- [ ] Review the genericized template for completeness
- [ ] Test the template by creating placeholders with actual values
- [ ] Update project documentation to reflect the genericized nature
- [ ] Consider creating a setup script for automatic placeholder replacement
- [ ] Archive the change in OpenSpec if satisfied with results

## Rollback Instructions

If you need to restore the original files:

**Restore specific file**:
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

## Notes

- All tasks must be completed in order
- Each task must pass its verification before proceeding
- Stop on any verification failure and hand off to human
- Do NOT skip verification steps
- Report all errors with specific file and line number when possible
