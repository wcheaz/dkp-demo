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
