## Purpose

Validates that the Kubernetes cluster is healthy and all deployed services are reachable after deployment.

## Requirements

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
