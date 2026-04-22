## 1. VM Provisioning

- [ ] 1.1 Create `scripts/deploy/setup-vm.sh` with `multipass launch` using `--cpus 4 --memory 7.7G --disk 19.3G --name dkp-demo-k8s` and idempotent VM-exists check (skip creation if already running, proceed to configuration)
- [ ] 1.2 Add Docker installation inside the VM: `multipass exec dkp-demo-k8s -- sudo apt-get update && sudo apt-get install -y docker.io`, then add user to docker group
- [ ] 1.3 Add Docker insecure registry configuration in the VM: write `/etc/docker/daemon.json` with `{ "insecure-registries": ["localhost:32000"] }` and restart Docker daemon
- [ ] 1.4 Add MicroK8s installation inside the VM: `multipass exec dkp-demo-k8s -- sudo snap install microk8s --classic --channel=1.28/stable` with retry logic (3 attempts, 10-second delay)
- [ ] 1.5 Add MicroK8s add-on enablement: `microk8s enable dns ingress registry storage` with idempotent checks (skip if already enabled)
- [ ] 1.6 Add post-install validation: verify `microk8s status` reports running, verify registry reachable at `localhost:32000` inside the VM, verify Docker daemon accessible
- [ ] 1.7 Make `setup-vm.sh` executable (`chmod +x`) and add `set -euo pipefail` with colored logging functions sourced from `scripts/deploy/common.sh`

## 2. VM Teardown

- [ ] 2.1 Create `scripts/deploy/destroy-vm.sh` that runs `multipass stop dkp-demo-k8s && multipass delete dkp-demo-k8s` when the VM exists, or logs "not found" and exits 0 when it doesn't
- [ ] 2.2 Make `destroy-vm.sh` executable and add `set -euo pipefail` with logging

## 3. Port Alignment

- [ ] 3.1 Update `docker-compose.yml` to use port `3000:3000` instead of `3001:3001` so it matches the frontend Dockerfile's `EXPOSE 3000`, `HEALTHCHECK` on port 3000, and k8s manifests' `containerPort: 3000`

## 4. Placeholder Replacement in K8s Manifests

- [ ] 4.1 Replace all `{{PROJECT_NAME}}` with `dkp-demo` in `k8s/deployment.yaml`: deployment name, labels, container name, image reference, secret/configmap references
- [ ] 4.2 Replace all `{{PROJECT_NAME}}` with `dkp-demo` in `k8s/service.yaml`: service name, labels, selector
- [ ] 4.3 Replace all `{{PROJECT_NAME}}` with `dkp-demo` and `{{APP_HOSTNAME}}` with `dkp-demo.local` in `k8s/ingress.yaml`: ingress name, labels, host, backend service name
- [ ] 4.4 Replace all `{{REGISTRY_HOST}}` with `localhost:32000` and `{{PROJECT_NAME}}` with `dkp-demo` in `k8s/agent-deployment.yaml`: image reference, secret/configmap references
- [ ] 4.5 Replace all `{{PROJECT_NAME}}` with `dkp-demo` in `k8s/secrets.yaml`: secret name, configmap name, labels

## 5. Placeholder Replacement in Deploy Scripts

- [ ] 5.1 Replace all `{{PROJECT_NAME}}` with `dkp-demo` and `{{REGISTRY_HOST}}` with `localhost:32000` in `scripts/deploy/common.sh`: `VM_NAME` default variable
- [ ] 5.2 Replace all `{{PROJECT_NAME}}` with `dkp-demo` and `{{REGISTRY_HOST}}` with `localhost:32000` in `scripts/kubernetes-deployment-setup.sh`: `VM_NAME`, `REGISTRY`, `FRONTEND_IMAGE_NAME`, `FRONTEND_DEPLOYMENT` variables and insecure registry config
- [ ] 5.3 Replace all `{{PROJECT_NAME}}` with `dkp-demo` and `{{REGISTRY_HOST}}` with `localhost:32000` in `k8s/setup-secrets.sh`: `VM_NAME` default, validation commands
- [ ] 5.4 Verify no `{{PLACEHOLDER}}` tokens remain in any file under `k8s/` and `scripts/` using `grep -r '{{' k8s/ scripts/`

## 6. Deploy Pipeline Orchestrator

- [ ] 6.1 Create `deploy-all.sh` at project root with `set -euo pipefail`, sourcing `scripts/deploy/common.sh` for logging, and `setup_log_file` call
- [ ] 6.2 Add pre-flight checks to `deploy-all.sh`: verify `multipass` CLI available, verify VM `dkp-demo-k8s` is running, verify Docker accessible on host, verify Docker accessible inside VM
- [ ] 6.3 Add secrets generation step: call `k8s/setup-secrets.sh` to generate `k8s/secrets.yaml` from `.env`, fail if required env vars (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `EMBEDDING_MODEL`) are missing
- [ ] 6.4 Add frontend image build step: `docker build -t dkp-demo:latest -f Dockerfile .`
- [ ] 6.5 Add agent image build step: `docker build -t agent:latest -f agent/Dockerfile ./agent`
- [ ] 6.6 Add disk space check function: query VM available space via `multipass exec dkp-demo-k8s -- df --output=avail /`, fail if less than required (2GB for frontend + 5GB for agent + 2GB margin)
- [ ] 6.7 Add image transfer function: `docker save` to tar, `multipass transfer` to VM, `docker load` in VM, `docker tag` for registry, `docker push` to `localhost:32000`
- [ ] 6.8 Add manifest apply step: transfer each `k8s/*.yaml` to VM and apply via `microk8s kubectl apply -f` in order: `secrets.yaml` → `service.yaml` → `agent-service.yaml` → `deployment.yaml` → `agent-deployment.yaml` → `ingress.yaml`
- [ ] 6.9 Add deployment restart step: `microk8s kubectl rollout restart deployment/dkp-demo` and `microk8s kubectl rollout restart deployment/agent`, with `rollout status` wait
- [ ] 6.10 Add rollback function: on any step failure, restore `.bak` backup files if they exist, re-apply previous deployment manifest, log rollback status
- [ ] 6.11 Add cleanup: remove `.tar` files from host and `/tmp/*.tar` from VM after successful push

## 7. Verification

- [ ] 7.1 Add pod readiness check to `deploy-all.sh`: poll `microk8s kubectl get pods` for up to 5 minutes, verify all pods `Running` with `1/1` ready, fail with diagnostic output on timeout
- [ ] 7.2 Add agent health check: `microk8s kubectl exec` into the agent pod and curl `/api/health` on port 8000, expect HTTP 200
- [ ] 7.3 Add ingress reachability check: get VM IP via `multipass info dkp-demo-k8s`, curl `http://dkp-demo.local` (after instructing user to add VM IP to `/etc/hosts`), expect HTTP 200
- [ ] 7.4 Add pass/fail summary output: print each check name with PASSED/FAILED status, exit 0 if all passed, exit 1 if any failed
- [ ] 7.5 Add `--skip-verify` flag to `deploy-all.sh` to bypass verification for faster iteration during development

## 8. End-to-End Validation

- [ ] 8.1 Run `scripts/deploy/setup-vm.sh` and verify VM reaches Running state with MicroK8s ready and registry accessible
- [ ] 8.2 Run `./deploy-all.sh` and verify the full pipeline completes without errors
- [ ] 8.3 Verify frontend is reachable at `http://dkp-demo.local` and returns the Next.js application HTML
- [ ] 8.4 Verify agent health endpoint returns HTTP 200
- [ ] 8.5 Run `scripts/deploy/destroy-vm.sh` and verify VM is fully removed
