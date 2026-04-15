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
- **Change-specific**: Within the change directory

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

## 1. <!-- Task Group Name -->

- [ ] 1.1 <!-- Task description with detailed actions, "Done when" criteria, "Verify by" command(s), and "Stop and hand off if" conditions. Follow OPENSPEC-RALPH-BP.md: one coherent slice, explicit done signals, objective verification, stop on blockers. -->

- [ ] 1.2 <!-- Task description with detailed actions, "Done when" criteria, "Verify by" command(s), and "Stop and hand off if" conditions. Follow OPENSPEC-RALPH-BP.md: one coherent slice, explicit done signals, objective verification, stop on blockers. -->

## 2. <!-- Task Group Name -->

- [ ] 2.1 <!-- Task description with detailed actions, "Done when" criteria, "Verify by" command(s), and "Stop and hand off if" conditions. Follow OPENSPEC-RALPH-BP.md: one coherent slice, explicit done signals, objective verification, stop on blockers. -->

- [ ] 2.2 <!-- Task description with detailed actions, "Done when" criteria, "Verify by" command(s), and "Stop and hand off if" conditions. Follow OPENSPEC-RALPH-BP.md: one coherent slice, explicit done signals, objective verification, stop on blockers. -->
