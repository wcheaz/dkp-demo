## Why

The project currently has no running Kubernetes cluster for testing. All k8s manifests (`k8s/*.yaml`) and deploy scripts (`scripts/deploy/*.sh`) exist as templates with `{{PROJECT_NAME}}` and `{{REGISTRY_HOST}}` placeholders but have never been validated against a live cluster. A local Kubernetes environment is needed to test container orchestration, service networking, ingress routing, and the full frontend-agent communication path under realistic conditions before any production deployment.

## What Changes

- Add a Multipass VM provisioning script that creates an Ubuntu VM with 4 CPU, 7.7 GB RAM, and 19.3 GB disk — matching the reference architecture from the sister project (`my-ag-ui-app`).
- Install and configure MicroK8s inside the VM with required add-ons: DNS, NGINX ingress, built-in registry (`localhost:32000`), and hostpath storage.
- Install Docker inside the VM for local image builds and registry push operations.
- Replace all `{{PROJECT_NAME}}` and `{{REGISTRY_HOST}}` placeholders in existing k8s manifests with concrete values (`dkp-demo` and `localhost:32000`).
- Replace all `{{PROJECT_NAME}}` and `{{REGISTRY_HOST}}` placeholders in deploy scripts (`scripts/deploy/common.sh`, `scripts/kubernetes-deployment-setup.sh`, `k8s/setup-secrets.sh`).
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

- **Files modified**: All `k8s/*.yaml` files (placeholder replacement), `scripts/deploy/common.sh`, `scripts/kubernetes-deployment-setup.sh`, `k8s/setup-secrets.sh`, frontend `Dockerfile` (port alignment).
- **New files**: `scripts/deploy/setup-vm.sh` (VM provisioning), `scripts/deploy/destroy-vm.sh` (teardown), `deploy-all.sh` (orchestrator), `k8s/configmap.yaml` (extracted from secrets.yaml for clean separation if needed).
- **Dependencies**: `multipass` CLI on the host machine, `docker` CLI on the host machine, internet access for snap installs and base image pulls.
- **Runtime requirements**: Host must have ~25 GB free disk for VM image, Docker layers, and container images. Host OS must support Multipass (Linux recommended).
- **Risk**: Port mismatch between Dockerfile (3000) and docker-compose.yml (3001) must be resolved before manifests will work. The agent image is large (~4 GB) due to PyTorch dependency, requiring adequate VM disk space and transfer time.
