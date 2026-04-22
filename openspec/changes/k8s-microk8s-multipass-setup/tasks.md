## 1. Port Alignment

- [x] 1.1 Fix frontend port mismatch: update `docker-compose.yml` to use port `3000:3000` instead of `3001:3001` so it matches the frontend Dockerfile's `EXPOSE 3000`, `HEALTHCHECK` on port 3000, and k8s manifests' `containerPort: 3000`.
  - Done when: `docker-compose.yml` maps port 3000 and no reference to `3001` remains.
  - Verify by: `grep '3000:3000' docker-compose.yml` succeeds and `grep '3001' docker-compose.yml` fails.

## 2. Placeholder Replacement

- [x] 2.1 Replace all `{{PROJECT_NAME}}` with `dkp-demo`, `{{REGISTRY_HOST}}` with `localhost:32000`, and `{{APP_HOSTNAME}}` with `dkp-demo.local` in every file under `k8s/` and `scripts/`. Also fix bug in `scripts/deploy/setup-k8s-secrets.sh` where it references non-existent `k8s/setup-secrets.sh` (lines 37 and 94 — should be `scripts/deploy/setup-secrets.sh`). Also replace `{{PROJECT_NAME}}` with `dkp-demo` in `scripts/setup-vm-docker.sh` (line 12).
  - Done when: `grep -r '{{' k8s/ scripts/` returns no matches and the path bug in `setup-k8s-secrets.sh` is corrected.
  - Verify by: `grep -r '{{' k8s/ scripts/` exits with status 1 (no matches); `grep 'k8s/setup-secrets' scripts/deploy/setup-k8s-secrets.sh` exits with status 1.

## 3. VM Provisioning Script

- [x] 3.1 Create `scripts/deploy/setup-vm.sh` that provisions a Multipass VM named `dkp-demo-k8s` (4 CPUs, 7.7G RAM, 19.3G disk), installs Docker with insecure registry config for `localhost:32000`, installs MicroK8s via snap with retry logic (3 attempts, 10-second delay), enables dns/ingress/registry/storage add-ons, adds the ubuntu user to the microk8s group, and validates the cluster is ready. Script must be executable with `set -euo pipefail`, source colored logging from `scripts/deploy/common.sh`, and be idempotent (skip VM creation if already running, skip add-ons if already enabled).
  - Done when: `scripts/deploy/setup-vm.sh` exists, is executable, contains all provisioning steps, and handles idempotency.
  - Verify by: `test -x scripts/deploy/setup-vm.sh && grep 'set -euo pipefail' scripts/deploy/setup-vm.sh && grep 'multipass launch' scripts/deploy/setup-vm.sh && grep 'microk8s enable' scripts/deploy/setup-vm.sh`

## 4. VM Teardown Script

- [ ] 4.1 Create `scripts/deploy/destroy-vm.sh` that stops and deletes the `dkp-demo-k8s` VM when it exists, or logs "not found" and exits 0 when it doesn't. Script must be executable with `set -euo pipefail` and source logging from `scripts/deploy/common.sh`.
  - Done when: `scripts/deploy/destroy-vm.sh` exists, is executable, handles both the VM-exists and VM-not-found cases.
  - Verify by: `test -x scripts/deploy/destroy-vm.sh && grep 'multipass delete' scripts/deploy/destroy-vm.sh`

## 5. Deploy Pipeline Orchestrator

- [ ] 5.1 Create `deploy-all.sh` at the project root that orchestrates the full deployment pipeline. The script must source `scripts/deploy/common.sh` for logging, call `setup_log_file`, and implement these steps in order: (a) pre-flight checks — verify `multipass` CLI available, VM `dkp-demo-k8s` is running, Docker accessible on host and inside VM; (b) secrets generation — call `scripts/deploy/setup-secrets.sh`, fail if required env vars (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `EMBEDDING_MODEL`) are missing; (c) image builds — `docker build` for frontend (`-t dkp-demo:latest -f Dockerfile .`) and agent (`-t agent:latest -f agent/Dockerfile ./agent`); (d) disk space check — query VM available space, fail if less than 9 GB; (e) image transfer — `docker save` to tar, `multipass transfer` to VM, `docker load` in VM, `docker tag` for registry, `docker push` to `localhost:32000`; (f) manifest apply — transfer each `k8s/*.yaml` to VM and apply via `microk8s kubectl apply -f` in order: secrets → service → agent-service → deployment → agent-deployment → ingress; (g) deployment restart with `rollout status` wait; (h) rollback on any step failure — restore `.bak` backups if they exist, re-apply previous manifests; (i) cleanup — remove `.tar` files from host and `/tmp/*.tar` from VM. Include a `--skip-verify` flag to bypass verification for development iteration.
  - Done when: `deploy-all.sh` exists, is executable, and contains all pipeline stages (preflight, secrets, build, transfer, apply, restart, rollback, cleanup).
  - Verify by: `test -x deploy-all.sh && grep 'setup_log_file' deploy-all.sh && grep 'rollout restart' deploy-all.sh && grep 'rollout status' deploy-all.sh && grep '\-\-skip-verify' deploy-all.sh`

- [ ] 5.2 Add verification to `deploy-all.sh`: pod readiness check (poll `microk8s kubectl get pods` for up to 5 minutes, verify all pods `Running` with `1/1` ready), agent health check (`kubectl exec` into agent pod, curl `/api/health` on port 8000, expect HTTP 200), ingress reachability check (get VM IP via `multipass info`, curl `http://dkp-demo.local`, expect HTTP 200), and pass/fail summary output. Exit 0 if all checks pass, exit 1 if any fail. This step runs after manifest apply and rollout restart unless `--skip-verify` is set.
  - Done when: `deploy-all.sh` contains all three verification checks and the summary output.
  - Verify by: `grep '1/1' deploy-all.sh && grep 'api/health' deploy-all.sh && grep 'dkp-demo.local' deploy-all.sh && grep 'PASSED\|FAILED' deploy-all.sh`

## Human Handoff

The following validation steps require a running Multipass VM and cannot be executed autonomously. The operator should perform these after all tasks above are complete:

1. Run `scripts/deploy/setup-vm.sh` and verify VM reaches Running state with MicroK8s ready and registry accessible at `localhost:32000`.
2. Run `./deploy-all.sh` and verify the full pipeline completes without errors.
3. Verify frontend is reachable at `http://dkp-demo.local` (after adding VM IP to `/etc/hosts`) and returns the Next.js application HTML.
4. Verify agent health endpoint returns HTTP 200.
5. Run `scripts/deploy/destroy-vm.sh` and verify VM is fully removed.
