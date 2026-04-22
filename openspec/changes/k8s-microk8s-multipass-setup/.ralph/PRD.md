# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

## Why

The project currently has no running Kubernetes cluster for testing. All k8s manifests (`k8s/*.yaml`) and deploy scripts (`scripts/deploy/*.sh`) exist as templates with `{{PROJECT_NAME}}` and `{{REGISTRY_HOST}}` placeholders but have never been validated against a live cluster. A local Kubernetes environment is needed to test container orchestration, service networking, ingress routing, and the full frontend-agent communication path under realistic conditions before any production deployment.

## What Changes

- Add a Multipass VM provisioning script that creates an Ubuntu VM with 4 CPU, 7.7 GB RAM, and 19.3 GB disk — matching the reference architecture from the sister project (`my-ag-ui-app`).
- Install and configure MicroK8s inside the VM with required add-ons: DNS, NGINX ingress, built-in registry (`localhost:32000`), and hostpath storage.
- Install Docker inside the VM for local image builds and registry push operations.
- Replace all `{{PROJECT_NAME}}` and `{{REGISTRY_HOST}}` placeholders in existing k8s manifests with concrete values (`dkp-demo` and `localhost:32000`).
- Replace all `{{PROJECT_NAME}}` and `{{REGISTRY_HOST}}` placeholders in deploy scripts (`scripts/deploy/common.sh`, `scripts/kubernetes-deployment-setup.sh`, `scripts/deploy/setup-secrets.sh`, `scripts/setup-vm-docker.sh`). Fix bug in `scripts/deploy/setup-k8s-secrets.sh` where it references non-existent `k8s/setup-secrets.sh` (should be `scripts/deploy/setup-secrets.sh`).
- Update the frontend Dockerfile port from 3000 to 3001 to match `docker-compose.yml`, or vice versa — resolve the port mismatch.
- Create a single end-to-end deploy script (`deploy-all.sh`) modeled on the reference project's orchestrator, chaining: cleanup → secrets → build → tag → registry setup → push → k8s apply → ingress → verify.
- Add a VM teardown/destroy script for clean re-provisioning.
- Validate the full stack: frontend reachable via ingress, agent health probe passing, SSE streaming functional through the agent service.

## Capabilities

### New Capabilities
- `vm-provisioning`: Multipass VM creation with fixed specs (4 CPU / 7.7 GB RAM / 19.3 GB disk), Docker installation, MicroK8s snap installation, add-on enablement (dns, ingress, registry, storage), and VM teardown.
- `k8s-manifest-rendering`: Replace all `{{PLACEHOLDER}}` tokens in k8s YAML manifests and deploy scripts with project-specific values, producing deployment-ready files without manual editing.
- `k8s-deploy-pipeline`: Orchestrated shell-based pipeline that builds Docker images, transfers them into the VM, tags and pushes to the MicroK8s registry, applies k8s manifests, and verifies pod readiness and ingress accessibility.
- `k8s-cluster-validation`: Post-deploy verification that all pods reach Running state, readiness probes pass, the agent health endpoint responds, and the frontend is reachable through the NGINX ingress.

### Modified Capabilities

(None — no existing specs are being modified.)

## Impact

- **Files modified**: All `k8s/*.yaml` files (placeholder replacement), `scripts/deploy/common.sh`, `scripts/kubernetes-deployment-setup.sh`, `scripts/deploy/setup-secrets.sh`, `scripts/setup-vm-docker.sh`, `scripts/deploy/setup-k8s-secrets.sh` (bug fix: correct path to setup-secrets.sh), `docker-compose.yml` (port alignment from 3001 to 3000).
- **New files**: `scripts/deploy/setup-vm.sh` (VM provisioning), `scripts/deploy/destroy-vm.sh` (teardown), `deploy-all.sh` (orchestrator).
- **Dependencies**: `multipass` CLI on the host machine, `docker` CLI on the host machine, internet access for snap installs and base image pulls.
- **Runtime requirements**: Host must have ~25 GB free disk for VM image, Docker layers, and container images. Host OS must support Multipass (Linux recommended).
- **Risk**: Port mismatch between Dockerfile (3000) and docker-compose.yml (3001) must be resolved before manifests will work. The agent image is large (~4 GB) due to PyTorch dependency, requiring adequate VM disk space and transfer time.

## Specifications

k8s-cluster-validation/spec.md
## ADDED Requirements

### Requirement: Frontend pod reaches Running state and passes readiness probe
After deployment, all frontend pods SHALL reach `Running` status with readiness probe passing within 5 minutes.

#### Scenario: Frontend pods ready after deployment
- **WHEN** the deployment pipeline completes
- **THEN** `multipass exec dkp-demo-k8s -- microk8s kubectl get pods -l app=dkp-demo` SHALL show all pods as `Running` with `1/1` ready
- **AND** no pods SHALL be in `CrashLoopBackOff`, `ImagePullBackOff`, or `Pending` state

### Requirement: Agent pod reaches Running state and passes health probe
After deployment, the agent pod SHALL reach `Running` status with both liveness and readiness probes passing within 5 minutes.

#### Scenario: Agent pod ready after deployment
- **WHEN** the deployment pipeline completes
- **THEN** `multipass exec dkp-demo-k8s -- microk8s kubectl get pods -l app=agent` SHALL show the pod as `Running` with `1/1` ready
- **AND** `multipass exec dkp-demo-k8s -- microk8s kubectl logs -l app=agent --tail=10` SHALL show successful uvicorn startup

### Requirement: Agent health endpoint responds
The agent's `/api/health` endpoint SHALL return HTTP 200 from within the cluster.

#### Scenario: Health check via pod port-forward or cluster access
- **WHEN** a request is made to the agent pod's `/api/health` endpoint on port 8000
- **THEN** the response SHALL have HTTP status 200

### Requirement: Frontend reachable through NGINX ingress
The frontend SHALL be accessible via the NGINX ingress at `dkp-demo.local` from the host machine after adding the VM IP to `/etc/hosts`.

#### Scenario: Frontend page loads through ingress
- **WHEN** the host's `/etc/hosts` contains `<VM_IP> dkp-demo.local`
- **AND** a request is made to `http://dkp-demo.local`
- **THEN** the response SHALL have HTTP status 200
- **AND** the response SHALL contain the Next.js application HTML

### Requirement: Frontend-to-agent communication functional
The frontend SHALL successfully communicate with the agent service through the Kubernetes internal network using the `AGENT_URL=http://agent-service:8000/` environment variable.

#### Scenario: Agent request from frontend
- **WHEN** a user interaction triggers an agent request from the frontend
- **THEN** the frontend SHALL successfully proxy the request to the agent service
- **AND** the agent SHALL return a valid response

### Requirement: SSE streaming through ingress
Server-Sent Events from the agent SHALL flow through the NGINX ingress without buffering, as configured by the ingress annotations (`proxy-buffering: off`, `proxy-read-timeout: 3600`).

#### Scenario: SSE stream delivers complete response
- **WHEN** an agent request produces a streaming response
- **THEN** the full SSE stream SHALL be delivered to the browser without premature termination
- **AND** the NGINX ingress SHALL NOT buffer the response

### Requirement: Verification script provides pass/fail summary
The system SHALL provide a verification step (integrated into `deploy-all.sh` or standalone in `test/`) that checks all of the above conditions and prints a clear pass/fail summary.

#### Scenario: All checks pass
- **WHEN** the verification step runs after a successful deployment
- **THEN** it SHALL print a summary showing each check as PASSED
- **AND** it SHALL exit with code 0

#### Scenario: One or more checks fail
- **WHEN** the verification step runs and a pod is not ready
- **THEN** it SHALL print a summary showing which check FAILED with diagnostic information
- **AND** it SHALL exit with non-zero code

k8s-deploy-pipeline/spec.md
## ADDED Requirements

### Requirement: Orchestrated deploy-all.sh pipeline
The system SHALL provide a `deploy-all.sh` script at the project root that executes the full deployment pipeline in sequence: cleanup, secrets setup, frontend image build, agent image build, registry setup, image tag, image push, k8s manifest apply, and deployment verification.

#### Scenario: Full deployment from clean state
- **WHEN** the user runs `./deploy-all.sh` and the VM is running with MicroK8s ready
- **THEN** the script SHALL execute each pipeline step in order
- **AND** the script SHALL exit with code 0 only if all steps succeed
- **AND** the script SHALL exit with non-zero code and stop immediately if any step fails

#### Scenario: Pipeline step failure triggers rollback
- **WHEN** a pipeline step fails (e.g., Docker build fails)
- **THEN** the script SHALL log which step failed and why
- **AND** the script SHALL attempt to restore the previous deployment state using the backup manifest
- **AND** the script SHALL exit with non-zero code

### Requirement: Frontend Docker image build and transfer
The pipeline SHALL build the frontend Docker image from the project root Dockerfile, save it to a tar file, transfer it to the VM, load it into the VM's Docker daemon, tag it for the registry, and push it to `localhost:32000/dkp-demo:latest`.

#### Scenario: Frontend image successfully pushed to registry
- **WHEN** the build and push steps complete
- **THEN** `multipass exec dkp-demo-k8s -- curl -s http://localhost:32000/v2/dkp-demo/tags/list` SHALL return a JSON response containing `"latest"`

### Requirement: Agent Docker image build and transfer
The pipeline SHALL build the agent Docker image from `./agent/Dockerfile`, save it to a tar file, transfer it to the VM, load it into the VM's Docker daemon, tag it for the registry, and push it to `localhost:32000/agent:latest`.

#### Scenario: Agent image successfully pushed to registry
- **WHEN** the build and push steps complete
- **THEN** `multipass exec dkp-demo-k8s -- curl -s http://localhost:32000/v2/agent/tags/list` SHALL return a JSON response containing `"latest"`

### Requirement: Kubernetes secrets created from .env file
The pipeline SHALL read the project `.env` file, base64-encode sensitive values, generate a `k8s/secrets.yaml` file, and apply it to the cluster. The pipeline SHALL fail if required environment variables (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `EMBEDDING_MODEL`) are missing.

#### Scenario: Secrets applied from .env file
- **WHEN** the secrets setup step runs and all required variables are present in `.env`
- **THEN** `multipass exec dkp-demo-k8s -- microk8s kubectl get secret dkp-demo-secrets` SHALL report the secret exists
- **AND** the ConfigMap `dkp-demo-config` SHALL contain `LLM_MAX_TOKENS` and `LLM_CONTEXT_WINDOW` keys

#### Scenario: Missing required environment variable
- **WHEN** the secrets setup step runs and `OPENAI_API_KEY` is missing from `.env`
- **THEN** the pipeline SHALL exit with non-zero code and log which variable is missing

### Requirement: Kubernetes manifests applied to cluster
The pipeline SHALL apply all rendered k8s manifests to the MicroK8s cluster in the correct order: secrets/configmap first, then services, then deployments, then ingress.

#### Scenario: All resources created in cluster
- **WHEN** the apply step completes
- **THEN** `multipass exec dkp-demo-k8s -- microk8s kubectl get deployments` SHALL list both `dkp-demo` and `agent` deployments
- **AND** `multipass exec dkp-demo-k8s -- microk8s kubectl get svc` SHALL list `dkp-demo-service` and `agent-service`
- **AND** `multipass exec dkp-demo-k8s -- microk8s kubectl get ingress` SHALL list `dkp-demo-ingress`

### Requirement: Docker insecure registry configuration in VM
The pipeline SHALL ensure Docker inside the VM is configured with `localhost:32000` as an insecure registry in `/etc/docker/daemon.json`, restarting the Docker daemon only if the configuration changes.

#### Scenario: Insecure registry already configured
- **WHEN** `/etc/docker/daemon.json` inside the VM already contains `localhost:32000` in `insecure-registries`
- **THEN** the script SHALL NOT restart the Docker daemon

k8s-manifest-rendering/spec.md
## ADDED Requirements

### Requirement: Replace PROJECT_NAME placeholder in all k8s manifests
The system SHALL replace every occurrence of `{{PROJECT_NAME}}` in `k8s/*.yaml` files with the concrete value `dkp-demo`, producing deployment-ready manifests without manual editing.

#### Scenario: Frontend deployment manifest rendered
- **WHEN** the manifest rendering step runs
- **THEN** `k8s/deployment.yaml` SHALL contain `name: dkp-demo` (not `{{PROJECT_NAME}}`)
- **AND** `k8s/deployment.yaml` SHALL reference `localhost:32000/dkp-demo:latest` as the container image
- **AND** `k8s/deployment.yaml` SHALL reference `dkp-demo-secrets` and `dkp-demo-config` in envFrom

#### Scenario: Secrets and ConfigMap manifest rendered
- **WHEN** the manifest rendering step runs
- **THEN** `k8s/secrets.yaml` SHALL contain `name: dkp-demo-secrets` and `name: dkp-demo-config`
- **AND** labels SHALL use `app: dkp-demo`

### Requirement: Replace REGISTRY_HOST placeholder in all k8s manifests
The system SHALL replace every occurrence of `{{REGISTRY_HOST}}` in `k8s/*.yaml` files with `localhost:32000`, the MicroK8s built-in registry address.

#### Scenario: Agent deployment manifest rendered
- **WHEN** the manifest rendering step runs
- **THEN** `k8s/agent-deployment.yaml` SHALL contain `image: localhost:32000/agent:latest`
- **AND** `k8s/agent-deployment.yaml` SHALL reference `dkp-demo-secrets` and `dkp-demo-config` in envFrom

### Requirement: Replace placeholders in deploy scripts
The system SHALL replace every occurrence of `{{PROJECT_NAME}}` and `{{REGISTRY_HOST}}` in deploy scripts (`scripts/deploy/common.sh`, `scripts/kubernetes-deployment-setup.sh`, `k8s/setup-secrets.sh`) with `dkp-demo` and `localhost:32000` respectively.

#### Scenario: common.sh rendered
- **WHEN** the manifest rendering step runs
- **THEN** `scripts/deploy/common.sh` SHALL contain `VM_NAME="${VM_NAME:-dkp-demo-k8s}"`
- **AND** no `{{PROJECT_NAME}}` or `{{REGISTRY_HOST}}` tokens SHALL remain in the file

#### Scenario: kubernetes-deployment-setup.sh rendered
- **WHEN** the manifest rendering step runs
- **THEN** `scripts/kubernetes-deployment-setup.sh` SHALL contain `REGISTRY="localhost:32000"`
- **AND** `scripts/kubernetes-deployment-setup.sh` SHALL contain `FRONTEND_IMAGE_NAME="dkp-demo"`
- **AND** no `{{PROJECT_NAME}}` or `{{REGISTRY_HOST}}` tokens SHALL remain in the file

### Requirement: Replace APP_HOSTNAME placeholder in ingress
The system SHALL replace `{{APP_HOSTNAME}}` in `k8s/ingress.yaml` with `dkp-demo.local`.

#### Scenario: Ingress manifest rendered
- **WHEN** the manifest rendering step runs
- **THEN** `k8s/ingress.yaml` SHALL contain `host: dkp-demo.local`
- **AND** `k8s/ingress.yaml` SHALL reference `dkp-demo-service` as the backend service name

### Requirement: Rendered manifests pass kubectl dry-run validation
All rendered k8s manifests SHALL pass `kubectl apply --dry-run=server` validation against the live MicroK8s API server inside the VM.

#### Scenario: Dry-run validation of all manifests
- **WHEN** `multipass exec dkp-demo-k8s -- microk8s kubectl apply --dry-run=server -f <manifest>` is run for each rendered manifest
- **THEN** the command SHALL exit with code 0 for every manifest file

vm-provisioning/spec.md
## ADDED Requirements

### Requirement: Multipass VM creation with fixed specifications
The system SHALL provide a script (`scripts/deploy/setup-vm.sh`) that creates a Multipass VM named `dkp-demo-k8s` with exactly 4 CPUs, 7.7 GB RAM, and 19.3 GB disk running Ubuntu, matching the reference architecture from the sister project.

#### Scenario: Fresh VM creation on a host with Multipass installed
- **WHEN** the user runs `scripts/deploy/setup-vm.sh` and no VM named `dkp-demo-k8s` exists
- **THEN** the script SHALL create a Multipass VM with 4 CPUs, 7.7 GB RAM, and 19.3 GB disk
- **AND** the script SHALL wait until the VM reaches "Running" state before proceeding

#### Scenario: VM already exists
- **WHEN** the user runs `scripts/deploy/setup-vm.sh` and a VM named `dkp-demo-k8s` already exists
- **THEN** the script SHALL skip creation and log that the VM already exists
- **AND** the script SHALL proceed to the configuration steps

### Requirement: Docker installation inside the VM
The system SHALL install Docker inside the Multipass VM so that image builds and registry pushes can be executed from within the VM.

#### Scenario: Docker installed and accessible
- **WHEN** the VM provisioning script completes
- **THEN** Docker SHALL be accessible inside the VM via `multipass exec dkp-demo-k8s -- docker info`
- **AND** the Docker daemon SHALL be configured with the MicroK8s registry (`localhost:32000`) as an insecure registry in `/etc/docker/daemon.json`

### Requirement: MicroK8s installation and add-on enablement
The system SHALL install MicroK8s inside the VM via snap and enable the following add-ons: `dns`, `ingress`, `registry`, and `storage`.

#### Scenario: MicroK8s running with all required add-ons
- **WHEN** the VM provisioning script completes
- **THEN** `multipass exec dkp-demo-k8s -- microk8s status` SHALL report MicroK8s is running
- **AND** the following add-ons SHALL be enabled: `dns`, `ingress`, `registry`, `storage`
- **AND** the registry SHALL be accessible at `localhost:32000` inside the VM

#### Scenario: MicroK8s add-on enablement is idempotent
- **WHEN** the VM provisioning script is run a second time and add-ons are already enabled
- **THEN** the script SHALL NOT fail and SHALL log that add-ons are already enabled

### Requirement: VM teardown script
The system SHALL provide a script (`scripts/deploy/destroy-vm.sh`) that stops and deletes the Multipass VM.

#### Scenario: Teardown of existing VM
- **WHEN** the user runs `scripts/deploy/destroy-vm.sh` and the VM `dkp-demo-k8s` exists
- **THEN** the script SHALL stop and delete the VM
- **AND** the script SHALL confirm deletion succeeded

#### Scenario: Teardown when VM does not exist
- **WHEN** the user runs `scripts/deploy/destroy-vm.sh` and the VM `dkp-demo-k8s` does not exist
- **THEN** the script SHALL log that no VM was found and exit successfully

### Requirement: Script exit codes reflect success or failure
All VM provisioning and teardown scripts SHALL exit with code 0 on success and non-zero on failure, enabling use in automated pipelines.

#### Scenario: Provisioning fails due to insufficient host resources
- **WHEN** the host does not have enough resources to create the VM
- **THEN** the script SHALL exit with a non-zero code and print a diagnostic message explaining the resource shortfall



## Design

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

## Current Task Context

## Current Task
- 1.1 Fix frontend port mismatch: update `docker-compose.yml` to use port `3000:3000` instead of `3001:3001` so it matches the frontend Dockerfile's `EXPOSE 3000`, `HEALTHCHECK` on port 3000, and k8s manifests' `containerPort: 3000`.
