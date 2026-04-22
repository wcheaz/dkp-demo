## Context

This project (`dkp-demo`) is a Next.js frontend + Python agent application that was scaffolded from a sister project (`my-ag-ui-app`) with all Kubernetes manifests and deploy scripts carried over as templates. Every manifest and script still contains `{{PROJECT_NAME}}` and `{{REGISTRY_HOST}}` placeholders and has never been run against a real cluster. There is no running Kubernetes environment for testing anywhere in this project's lifecycle.

The reference project has a working Multipass + MicroK8s setup with these exact specs: Ubuntu VM (4 CPU / 7.7 GB RAM / 19.3 GB disk), MicroK8s with dns/ingress/registry/storage add-ons, Docker inside the VM, and a `deploy-all.sh` orchestrator that builds images on the host, transfers them via tar into the VM, and pushes to the MicroK8s registry at `localhost:32000`.

**Current state of this project:**
- `k8s/*.yaml` — 6 files, all templated with `{{PLACEHOLDER}}` tokens
- `scripts/deploy/` — 11 scripts, mostly carried over from reference, all templated
- `scripts/kubernetes-deployment-setup.sh` — deployment helper, templated
- `Dockerfile` — frontend Dockerfile exposes port 3000
- `docker-compose.yml` — maps port 3001:3001 (mismatch with Dockerfile)
- `agent/Dockerfile` — Python agent Dockerfile, exposes port 8000
- No VM, no cluster, no validated deployment path

## Goals / Non-Goals

**Goals:**
- Provide a single command (`scripts/deploy/setup-vm.sh`) that creates a fully configured Multipass VM with MicroK8s ready to accept deployments.
- Provide a single command (`deploy-all.sh`) that builds, transfers, pushes, deploys, and verifies the entire application stack end-to-end.
- Resolve the Dockerfile port mismatch (3000 vs 3001) so manifests and Docker builds are consistent.
- Make all placeholder replacement deterministic and one-shot — once rendered, no `{{}}` tokens remain anywhere.
- Enable a Ralph loop to execute the full pipeline autonomously by making each step independently verifiable with clear exit codes.

**Non-Goals:**
- Production or cloud Kubernetes deployment (this is testing-only).
- Helm charts, Kustomize, or any templating engine beyond sed replacement.
- TLS/HTTPS on the ingress (HTTP-only for local testing).
- CI/CD integration (manual or Ralph-loop execution only).
- Multi-node cluster (single-node MicroK8s is sufficient for testing).
- Persistent storage beyond what MicroK8s hostpath provides.

## Decisions

### D1: Image build happens on the host, not inside the VM

**Decision**: Build Docker images on the host machine, save to tar, transfer via `multipass transfer`, load in VM Docker, tag for registry, push.

**Rationale**: The reference project uses this exact pattern successfully. Building inside the VM would require copying the entire source tree into the VM (large, slow) and installing build dependencies (Node.js, npm, Python, uv) inside the VM. Building on the host reuses the existing development environment and Docker cache.

**Alternative considered**: Build inside the VM — rejected because it requires duplicating the full build toolchain inside the VM and transferring the source tree (~1 GB with node_modules).

### D2: Port 3000 for the frontend (keep Dockerfile as-is)

**Decision**: Keep the frontend Dockerfile at port 3000 and fix `docker-compose.yml` to use `3000:3000` instead of `3001:3001`.

**Rationale**: The k8s manifests reference `containerPort: 3000` and the service `targetPort: 3000`. The Dockerfile's `HEALTHCHECK` and `EXPOSE` are both set to 3000. The standalone Next.js server defaults to 3000 via the `PORT` env var. Changing the Dockerfile would require changes in 5+ places; fixing docker-compose.yml is a one-line change.

**Alternative considered**: Change Dockerfile to 3001 — rejected because it breaks alignment with k8s manifests, the health check, and the standalone server default for no benefit.

### D3: Placeholder replacement via sed, not a templating engine

**Decision**: Use `sed -i` to replace `{{PROJECT_NAME}}`, `{{REGISTRY_HOST}}`, and `{{APP_HOSTNAME}}` in all files. Perform this as a dedicated step in `deploy-all.sh` before any kubectl operations.

**Rationale**: There are only 3 placeholder tokens across ~10 files. A full templating engine (envsubst, Helm, Kustomize) is overkill for this scope. sed is available on every Linux host and produces predictable, reviewable output. The replacement is done once; the rendered files are committed to the working tree so the agent can inspect them.

**Alternative considered**: envsubst — rejected because the YAML files contain `$` characters in other contexts that would be misinterpreted.

### D4: deploy-all.sh is a flat shell script, not Make or a pipeline tool

**Decision**: `deploy-all.sh` is a single bash script that calls sub-scripts in `scripts/deploy/` in sequence, each with `set -e` error handling. It sources `scripts/deploy/common.sh` for shared logging and error functions.

**Rationale**: This matches the reference project's proven pattern. Shell scripts are the lowest common denominator — no additional tools required. The existing `scripts/deploy/common.sh` already provides structured logging and error handling. Each sub-script can also be run independently for debugging.

**Alternative considered**: Makefile — rejected because it adds a dependency and the reference project's shell approach already works.

### D5: Agent image transfer uses the same tar-based flow as the frontend

**Decision**: Both frontend and agent images use the identical build → save → transfer → load → tag → push flow.

**Rationale**: The agent image is large (~4 GB due to PyTorch) but the tar-based transfer is the only reliable way to get images into a Multipass VM's Docker daemon. The existing `scripts/kubernetes-deployment-setup.sh` already implements this pattern for both images. The only concern is disk space — the VM has 19.3 GB and we need ~5 GB for the agent tar + loaded image. The pipeline checks available disk space before proceeding.

**Alternative considered**: Build agent inside the VM — rejected because it requires transferring the `agent/` directory with its `.venv` and `uv.lock`, plus installing Docker build dependencies in the VM.

### D6: Secrets generated from .env at deploy time, not stored in git

**Decision**: `k8s/secrets.yaml` is generated by `k8s/setup-secrets.sh` reading from `.env` each time `deploy-all.sh` runs. The rendered `secrets.yaml` is added to `.gitignore`.

**Rationale**: Secrets must not be committed. The `.env` file already exists as the single source of truth for environment variables. Generating at deploy time ensures secrets always match the current `.env`. This matches the reference project's approach.

### D7: Verification integrated into deploy-all.sh, not a separate required step

**Decision**: The deploy pipeline runs a verification function at the end that polls pod readiness (5-minute timeout), checks agent health, and confirms ingress is reachable. This runs automatically but can be skipped with `--skip-verify` for faster iteration.

**Rationale**: Forcing a separate verification step creates a human handoff point that blocks Ralph loops. Integrating it into the pipeline makes the whole flow one-shot. The `--skip-verify` flag preserves the ability to iterate quickly during development.

## Risks / Trade-offs

**[Agent image size (~4 GB) causes slow transfers and disk pressure]** → Mitigation: The pipeline checks VM disk space before each image transfer. If disk is low, the pipeline runs `docker system prune` inside the VM. The VM's 19.3 GB disk is sufficient for one frontend + one agent image plus registry storage, but does not allow multiple image versions to accumulate.

**[Port mismatch between Dockerfile and docker-compose.yml]** → Mitigation: Resolved by D2 (fix docker-compose.yml to port 3000). This is a known, one-time fix.

**[No HTTPS — HTTP-only ingress]** → Mitigation: Acceptable for local testing. The ingress is configured with `ssl-redirect: "false"`. If HTTPS is needed later, cert-manager can be added as a MicroK8s add-on.

**[sed replacement could miss edge cases in YAML]** → Mitigation: The pipeline runs `kubectl apply --dry-run=server` against every rendered manifest before applying. This catches any YAML syntax errors introduced by the replacement.

**[MicroK8s snap installation can be slow or fail on constrained networks]** → Mitigation: The setup script retries the snap install up to 3 times with a 10-second delay. On failure, the script prints the snap install log and exits with a diagnostic message. No automatic network recovery is attempted — the operator must resolve network issues.

**[Single-node cluster has no HA guarantees]** → Mitigation: This is a testing environment only. Pod restarts are handled by the deployment controller, but node failures require manual VM restart.

## Migration Plan

1. **Render placeholders**: `deploy-all.sh` runs sed replacement as its first step, creating backup files (`.bak`) of all modified files.
2. **Deploy**: Pipeline builds images, transfers, pushes, applies manifests.
3. **Rollback**: If any step fails, `deploy-all.sh` restores `.bak` files and re-applies the previous deployment manifest (if one exists).
4. **Teardown**: `scripts/deploy/destroy-vm.sh` removes the entire VM. Re-running `setup-vm.sh` + `deploy-all.sh` restores from scratch.

## Open Questions

None — all design decisions are resolved based on the reference project's proven patterns.
