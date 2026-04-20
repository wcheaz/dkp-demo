# Setup Script Consideration for Placeholder Replacement

## Status: DEFERRED

This document evaluates the feasibility and design of an automated setup script to replace placeholders with project-specific values after genericization.

## Problem Statement

The genericization process introduced three placeholder tokens across multiple files:

| Placeholder | Description | Example Value | Occurrences | Files Affected |
|---|---|---|---|---|
| `{{PROJECT_NAME}}` | Project identifier used in metadata, labels, selectors, VM names | `my-app` | 51 | 9 files (5 YAML, 3 shell, 1 deploy script) |
| `{{APP_HOSTNAME}}` | Domain/hostname for ingress routing | `myapp.local` | 1 | 1 file (ingress.yaml) |
| `{{REGISTRY_HOST}}` | Container registry address for image pulls | `localhost:32000` | 12 | 3 files (2 YAML, 1 shell) |

Manually replacing these across 10+ files is error-prone and tedious. A setup script would automate this process.

## Proposed Solution: `setup.sh`

An interactive shell script at project root that:

1. Prompts the user for three values (with defaults and validation)
2. Performs a global find-and-replace across all affected files
3. Validates the result (syntax checks)
4. Optionally initializes a git branch for the new project

### Script Interface

```bash
# Interactive mode
./setup.sh

# Non-interactive mode (CI/CD friendly)
./setup.sh --project-name my-app --app-hostname myapp.local --registry-host localhost:32000

# Dry-run mode (preview changes without modifying files)
./setup.sh --dry-run --project-name my-app
```

### User Prompts

```
=== Project Setup ===
Enter project name (lowercase, hyphens allowed) [my-project]: my-app
Enter app hostname (domain for ingress) [my-app.local]: app.example.com
Enter container registry host [localhost:32000]: registry.example.com

Replacing placeholders in 10 files...
  ✓ k8s/deployment.yaml (8 replacements)
  ✓ k8s/service.yaml (3 replacements)
  ✓ k8s/ingress.yaml (4 replacements)
  ✓ k8s/agent-deployment.yaml (4 replacements)
  ✓ k8s/secrets.yaml (6 replacements)
  ✓ deploy_scripts/common.sh (1 replacement)
  ✓ scripts/kubernetes-deployment-setup.sh (6 replacements)

Validating...
  ✓ YAML syntax valid
  ✓ Shell syntax valid

Setup complete. Run 'git diff' to review changes.
```

## Detailed Requirements

### REQ-1: Input Validation

- Project name: Must be a valid Kubernetes resource name (lowercase, alphanumeric, hyphens, no leading/trailing hyphens, max 63 chars)
- App hostname: Must be a valid hostname or IP address
- Registry host: Must be a valid `host:port` combination or full registry URL

### REQ-2: File Scope

The script MUST only modify files that contain `{{PLACEHOLDER}}` tokens:

- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `k8s/ingress.yaml`
- `k8s/agent-deployment.yaml`
- `k8s/secrets.yaml`
- `k8s/setup-secrets.sh`
- `deploy_scripts/common.sh`
- `scripts/kubernetes-deployment-setup.sh`
- `scripts/setup-vm-docker.sh`

Files that do NOT contain placeholders MUST NOT be touched (e.g., `Dockerfile`, `docker-compose.yml`, `package.json`, `README.md`).

### REQ-3: Backup Before Replacement

The script MUST create a backup of each file before modification (e.g., `k8s/deployment.yaml.bak`), or rely on the existing `.backup/` directory.

### REQ-4: Idempotency

Running the script multiple times with the same values MUST produce identical results. If placeholders have already been replaced, the script should detect this and warn the user.

### REQ-5: Dry-Run Mode

The `--dry-run` flag MUST show exactly what changes would be made without modifying any files.

### REQ-6: Validation After Replacement

After replacement, the script MUST validate:
- All YAML files parse correctly
- All shell scripts pass `bash -n` syntax check
- No remaining `{{` tokens exist in modified files

## Benefits

1. **Reduces onboarding friction**: New users can customize the template in seconds instead of manually editing 10+ files
2. **Eliminates human error**: Automated replacement ensures no placeholders are missed
3. **Enables CI/CD integration**: Non-interactive mode allows programmatic project initialization
4. **Self-documenting**: The prompts and validation serve as documentation for required configuration
5. **Consistent formatting**: Ensures all values are applied uniformly across the project

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Regex replacement could corrupt file content | Use simple string replacement (`sed` with literal strings, not regex); validate after replacement |
| User provides invalid values | Validate inputs before any file modifications |
| Running script twice corrupts already-replaced values | Detect remaining placeholders before running; warn if none found |
| Shell portability issues across macOS/Linux | Use POSIX-compatible constructs; test on both platforms |

## Estimated Effort

- **Implementation**: 2-3 hours (moderate complexity)
- **Testing**: 1-2 hours (edge cases, validation)
- **Documentation**: 30 minutes (inline comments, README update)
- **Total**: ~4-6 hours

## Alternative Approaches Considered

### 1. Environment Variable Substitution (envsubst)

Use `envsubst` with environment variables instead of `{{PLACEHOLDER}}` tokens.

**Pros**: Standard tool, Kubernetes-native (can use in Helm/Kustomize)
**Cons**: Requires envsubst installed; conflicts with shell variable syntax in scripts; would require restructuring how placeholders are used

### 2. Helm Chart / Kustomize Conversion

Convert Kubernetes manifests to Helm templates or Kustomize overlays.

**Pros**: Industry standard for Kubernetes configuration management
**Cons**: Significant restructuring; overkill for this template; adds learning curve for template consumers

### 3. Cookiecutter / Project Scaffolding Tool

Use Python Cookiecutter or similar scaffolding tool.

**Pros**: Well-established pattern for project templates
**Cons**: Adds Python dependency; more complex setup; overkill for simple string replacement

### 4. Simple `sed` One-Liner (No Script)

Provide documentation with `sed` commands users can copy-paste.

**Pros**: No new files; users understand exactly what happens
**Cons**: Error-prone; no validation; requires manual execution per file

## Recommendation

**Proceed with the `setup.sh` approach** (Option 0). It strikes the right balance between automation and simplicity. The script should be a single portable shell script with no external dependencies beyond standard POSIX tools.

The script should be placed at the project root as `setup.sh` and should be the first thing new users run after cloning the template.

## Implementation Checklist

- [ ] Create `setup.sh` with argument parsing (interactive and non-interactive modes)
- [ ] Implement input validation functions
- [ ] Implement file discovery (find all files with `{{` placeholders)
- [ ] Implement backup mechanism
- [ ] Implement replacement logic with `sed`
- [ ] Implement dry-run mode
- [ ] Implement post-replacement validation
- [ ] Add `--dry-run` flag
- [ ] Add `--restore` flag to revert from backups
- [ ] Test on macOS and Linux
- [ ] Update README.md with setup instructions
- [ ] Add `setup.sh` to version control
