## Purpose

Renders templated k8s manifests and deploy scripts by replacing placeholders with concrete values for the target environment.

## Requirements

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
