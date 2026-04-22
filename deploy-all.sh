#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/scripts/deploy/common.sh"

VM_NAME="${VM_NAME:-dkp-demo-k8s}"
REGISTRY="localhost:32000"
FRONTEND_IMAGE="dkp-demo"
AGENT_IMAGE="agent"
SKIP_VERIFY=false
MANIFEST_ORDER=("secrets.yaml" "service.yaml" "agent-service.yaml" "deployment.yaml" "agent-deployment.yaml" "ingress.yaml")

cleanup_tar_files() {
    log "Cleaning up tar files..."
    rm -f "${SCRIPT_DIR}/${FRONTEND_IMAGE}.tar" "${SCRIPT_DIR}/${AGENT_IMAGE}.tar" 2>/dev/null || true
    multipass exec "$VM_NAME" -- rm -f "/tmp/${FRONTEND_IMAGE}.tar" "/tmp/${AGENT_IMAGE}.tar" 2>/dev/null || true
    log "Tar files cleaned up"
}

rollback_on_failure() {
    local failed_step="$1"
    log_error "Pipeline failed at step: $failed_step"
    log "Attempting rollback..."

    local bak_files=()
    for manifest in "${MANIFEST_ORDER[@]}"; do
        if [ -f "${SCRIPT_DIR}/k8s/${manifest}.bak" ]; then
            bak_files+=("$manifest")
        fi
    done

    if [ ${#bak_files[@]} -eq 0 ]; then
        log "No .bak files found — skipping manifest rollback"
        return 0
    fi

    for manifest in "${bak_files[@]}"; do
        log "Restoring k8s/${manifest} from .bak..."
        cp "${SCRIPT_DIR}/k8s/${manifest}.bak" "${SCRIPT_DIR}/k8s/${manifest}"
    done

    log "Re-applying restored manifests..."
    for manifest in "${bak_files[@]}"; do
        local manifest_name
        manifest_name=$(basename "$manifest")
        multipass transfer "${SCRIPT_DIR}/k8s/${manifest}" "${VM_NAME}:/home/ubuntu/${manifest_name}" 2>/dev/null || true
        multipass exec "$VM_NAME" -- microk8s kubectl apply -f "/home/ubuntu/${manifest_name}" 2>/dev/null || true
        log "Re-applied restored $manifest"
    done

    log "Rollback completed"
}

preflight_checks() {
    log "Running pre-flight checks..."

    if ! command -v multipass >/dev/null 2>&1; then
        handle_dependency_error "multipass CLI not found on host" \
            "Install multipass from https://multipass.run/"
    fi
    log "multipass CLI available"

    local vm_state
    vm_state=$(multipass info "$VM_NAME" 2>/dev/null | grep "^State:" | awk '{print $2}' || echo "")
    if [[ "$vm_state" != "Running" ]]; then
        handle_error 1 "VM '$VM_NAME' is not running (state: ${vm_state:-not found})" \
            "Run: scripts/deploy/setup-vm.sh"
    fi
    log "VM '$VM_NAME' is running"

    if ! docker info >/dev/null 2>&1; then
        handle_docker_error "Docker daemon not accessible on host" \
            "Start Docker: sudo systemctl start docker"
    fi
    log "Docker accessible on host"

    if ! multipass exec "$VM_NAME" -- docker info >/dev/null 2>&1; then
        handle_docker_error "Docker daemon not accessible inside VM" \
            "Run: scripts/deploy/setup-vm.sh to reconfigure"
    fi
    log "Docker accessible inside VM"

    log "Pre-flight checks passed"
}

generate_secrets() {
    log "Generating Kubernetes secrets..."

    local env_file="${SCRIPT_DIR}/.env"

    local required_vars=("OPENAI_API_KEY" "OPENAI_BASE_URL" "OPENAI_MODEL" "EMBEDDING_MODEL")
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        local val=""
        if [ -f "$env_file" ]; then
            val=$(grep "^${var}=" "$env_file" 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'" || echo "")
        fi
        if [ -z "${!var:-}" ] && [ -z "$val" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        local missing_list
        missing_list=$(IFS=', '; echo "${missing_vars[*]}")
        handle_error 1 "Missing required environment variables: $missing_list" \
            "Add them to .env or export them in your shell"
    fi

    if ! bash "${SCRIPT_DIR}/scripts/deploy/setup-k8s-secrets.sh"; then
        log_error "Secrets generation failed"
        return 1
    fi

    log "Kubernetes secrets generated"
}

build_images() {
    log "Building Docker images..."

    log "Building frontend image (${FRONTEND_IMAGE}:latest)..."
    if ! docker build -t "${FRONTEND_IMAGE}:latest" -f "${SCRIPT_DIR}/Dockerfile" "${SCRIPT_DIR}"; then
        log_error "Frontend Docker build failed"
        return 1
    fi
    log "Frontend image built"

    log "Building agent image (${AGENT_IMAGE}:latest)..."
    if ! docker build -t "${AGENT_IMAGE}:latest" -f "${SCRIPT_DIR}/agent/Dockerfile" "${SCRIPT_DIR}/agent"; then
        log_error "Agent Docker build failed"
        return 1
    fi
    log "Agent image built"

    log "Docker images built successfully"
}

check_disk_space() {
    log "Checking disk space in VM..."

    local available_kb
    available_kb=$(multipass exec "$VM_NAME" -- df --output=avail / | tail -n1)
    if [ -z "$available_kb" ]; then
        log_error "Failed to query VM disk space"
        return 1
    fi

    local available_gb=$((available_kb / 1024 / 1024))
    log "Available disk space in VM: ${available_gb} GB"

    if [ "$available_gb" -lt 9 ]; then
        log_error "Insufficient disk space: ${available_gb} GB available, need at least 9 GB"
        log "Consider running with cleanup or destroying/recreating the VM"
        return 1
    fi

    log "Disk space check passed"
}

transfer_and_push_image() {
    local image_name="$1"
    local tar_file="${SCRIPT_DIR}/${image_name}.tar"

    log "Processing image: ${image_name}"

    log "Saving ${image_name}:latest to tar..."
    if ! docker save "${image_name}:latest" -o "$tar_file"; then
        log_error "Failed to save ${image_name} image to tar"
        return 1
    fi
    local tar_size
    tar_size=$(ls -lh "$tar_file" | awk '{print $5}')
    log "Image saved (${tar_size})"

    log "Transferring ${image_name}.tar to VM..."
    if ! multipass transfer "$tar_file" "${VM_NAME}:/tmp/${image_name}.tar"; then
        log_error "Failed to transfer ${image_name}.tar to VM"
        rm -f "$tar_file"
        return 1
    fi
    log "Image transferred to VM"

    log "Loading ${image_name} in VM Docker..."
    local load_output
    load_output=$(multipass exec "$VM_NAME" -- docker load -i "/tmp/${image_name}.tar" 2>&1)
    if [ $? -ne 0 ]; then
        log_error "Failed to load ${image_name} in VM"
        rm -f "$tar_file"
        multipass exec "$VM_NAME" -- rm -f "/tmp/${image_name}.tar" 2>/dev/null || true
        return 1
    fi
    log "Image loaded in VM"

    local vm_image_id
    vm_image_id=$(echo "$load_output" | grep -o 'sha256:[a-f0-9]\+')
    if [ -z "$vm_image_id" ]; then
        log_error "Could not extract image ID from load output"
        rm -f "$tar_file"
        return 1
    fi

    local target_image="${REGISTRY}/${image_name}:latest"
    log "Tagging as ${target_image}..."
    if ! multipass exec "$VM_NAME" -- docker tag "$vm_image_id" "$target_image"; then
        log_error "Failed to tag ${image_name}"
        rm -f "$tar_file"
        return 1
    fi

    log "Pushing ${target_image}..."
    if ! multipass exec "$VM_NAME" -- docker push "$target_image"; then
        log_error "Failed to push ${image_name} to registry"
        rm -f "$tar_file"
        return 1
    fi
    log "${image_name} pushed to ${target_image}"

    rm -f "$tar_file"
    multipass exec "$VM_NAME" -- rm -f "/tmp/${image_name}.tar" 2>/dev/null || true
}

transfer_all_images() {
    log "Transferring and pushing images to registry..."

    if ! transfer_and_push_image "$FRONTEND_IMAGE"; then
        log_error "Frontend image transfer failed"
        return 1
    fi

    if ! transfer_and_push_image "$AGENT_IMAGE"; then
        log_error "Agent image transfer failed"
        return 1
    fi

    log "All images transferred and pushed"
}

apply_manifests() {
    log "Applying Kubernetes manifests..."

    for manifest in "${MANIFEST_ORDER[@]}"; do
        local manifest_path="${SCRIPT_DIR}/k8s/${manifest}"
        if [ ! -f "$manifest_path" ]; then
            log_error "Manifest not found: k8s/${manifest}"
            return 1
        fi

        cp "$manifest_path" "${manifest_path}.bak"
    done

    for manifest in "${MANIFEST_ORDER[@]}"; do
        local manifest_path="${SCRIPT_DIR}/k8s/${manifest}"
        local manifest_name
        manifest_name=$(basename "$manifest")

        log "Applying ${manifest}..."

        if ! multipass transfer "$manifest_path" "${VM_NAME}:/home/ubuntu/${manifest_name}"; then
            log_error "Failed to transfer ${manifest} to VM"
            return 1
        fi

        if ! multipass exec "$VM_NAME" -- microk8s kubectl apply -f "/home/ubuntu/${manifest_name}"; then
            log_error "Failed to apply ${manifest}"
            return 1
        fi

        log "Applied ${manifest}"
    done

    log "All manifests applied"
}

restart_deployments() {
    log "Restarting deployments..."

    log "Restarting deployment/${FRONTEND_IMAGE}..."
    if ! multipass exec "$VM_NAME" -- microk8s kubectl rollout restart "deployment/${FRONTEND_IMAGE}"; then
        log_error "Failed to restart deployment/${FRONTEND_IMAGE}"
        return 1
    fi

    log "Waiting for ${FRONTEND_IMAGE} rollout..."
    if ! multipass exec "$VM_NAME" -- microk8s kubectl rollout status "deployment/${FRONTEND_IMAGE}" --timeout=300s; then
        log_error "Rollout status check failed for ${FRONTEND_IMAGE}"
        return 1
    fi
    log "Deployment ${FRONTEND_IMAGE} restarted"

    log "Restarting deployment/${AGENT_IMAGE}..."
    if ! multipass exec "$VM_NAME" -- microk8s kubectl rollout restart "deployment/${AGENT_IMAGE}"; then
        log_error "Failed to restart deployment/${AGENT_IMAGE}"
        return 1
    fi

    log "Waiting for ${AGENT_IMAGE} rollout..."
    if ! multipass exec "$VM_NAME" -- microk8s kubectl rollout status "deployment/${AGENT_IMAGE}" --timeout=300s; then
        log_error "Rollout status check failed for ${AGENT_IMAGE}"
        return 1
    fi
    log "Deployment ${AGENT_IMAGE} restarted"

    log "All deployments restarted and ready"
}

verify_deployment() {
    log "Running deployment verification..."

    local verify_passed=true
    local frontend_status="PENDING"
    local agent_status="PENDING"
    local health_status="PENDING"
    local ingress_status="PENDING"

    log "Checking pod readiness (timeout: 5 minutes)..."
    local attempt=0
    local max_attempts=60
    local all_ready=false

    while [ $attempt -lt $max_attempts ]; do
        local pod_output
        pod_output=$(multipass exec "$VM_NAME" -- microk8s kubectl get pods -o wide 2>&1)

        local not_ready_count
        not_ready_count=$(echo "$pod_output" | grep -v "NAME" | grep -v "^$" | grep -cv "1/1.*Running" || echo "0")

        if [ "$not_ready_count" -eq 0 ]; then
            local total_pods
            total_pods=$(echo "$pod_output" | grep -v "NAME" | grep -v "^$" | wc -l)
            if [ "$total_pods" -ge 1 ]; then
                all_ready=true
                break
            fi
        fi

        attempt=$((attempt + 1))
        sleep 5
    done

    local frontend_pods
    frontend_pods=$(multipass exec "$VM_NAME" -- microk8s kubectl get pods -l "app=${FRONTEND_IMAGE}" --no-headers 2>/dev/null || echo "")
    if echo "$frontend_pods" | grep -q "1/1.*Running"; then
        frontend_status="PASSED"
        log "Frontend pods: PASSED — Running with 1/1 ready"
    else
        frontend_status="FAILED"
        log_error "Frontend pods: FAILED"
        echo "$frontend_pods" | tee -a "$LOG_FILE"
        verify_passed=false
    fi

    local agent_pods
    agent_pods=$(multipass exec "$VM_NAME" -- microk8s kubectl get pods -l "app=${AGENT_IMAGE}" --no-headers 2>/dev/null || echo "")
    if echo "$agent_pods" | grep -q "1/1.*Running"; then
        agent_status="PASSED"
        log "Agent pods: PASSED — Running with 1/1 ready"
    else
        agent_status="FAILED"
        log_error "Agent pods: FAILED"
        echo "$agent_pods" | tee -a "$LOG_FILE"
        verify_passed=false
    fi

    if [ "$agent_status" = "PASSED" ]; then
        log "Checking agent health endpoint..."
        local agent_pod_name
        agent_pod_name=$(multipass exec "$VM_NAME" -- microk8s kubectl get pods -l "app=${AGENT_IMAGE}" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

        if [ -n "$agent_pod_name" ]; then
            local health_response
            health_response=$(multipass exec "$VM_NAME" -- microk8s kubectl exec "$agent_pod_name" -- curl -sf -o /dev/null -w "%{http_code}" http://localhost:8000/api/health 2>/dev/null || echo "000")

            if [ "$health_response" = "200" ]; then
                health_status="PASSED"
                log "Agent health (/api/health): PASSED — HTTP 200"
            else
                health_status="FAILED"
                log_error "Agent health (/api/health): FAILED — HTTP ${health_response}"
                verify_passed=false
            fi
        else
            health_status="FAILED"
            log_error "Agent health: FAILED — could not get agent pod name"
            verify_passed=false
        fi
    else
        health_status="SKIPPED"
        log "Agent health: SKIPPED (agent pod not ready)"
    fi

    log "Checking ingress reachability..."
    local vm_ip
    vm_ip=$(multipass info "$VM_NAME" 2>/dev/null | grep "IPv4" | awk '{print $2}' || echo "")

    if [ -n "$vm_ip" ]; then
        local ingress_response
        ingress_response=$(curl -sf -o /dev/null -w "%{http_code}" --connect-timeout 10 --resolve "dkp-demo.local:80:${vm_ip}" "http://dkp-demo.local" 2>/dev/null || echo "000")

        if [ "$ingress_response" = "200" ]; then
            ingress_status="PASSED"
            log "Ingress (dkp-demo.local): PASSED — HTTP 200"
        else
            ingress_status="FAILED"
            log_error "Ingress (dkp-demo.local): FAILED — HTTP ${ingress_response}"
            log "Ensure /etc/hosts contains: ${vm_ip} dkp-demo.local"
            verify_passed=false
        fi
    else
        ingress_status="FAILED"
        log_error "Ingress: FAILED — could not determine VM IP"
        verify_passed=false
    fi

    log ""
    log "============================================="
    log "  VERIFICATION SUMMARY"
    log "============================================="
    log "  Frontend pods:        ${frontend_status}"
    log "  Agent pods:           ${agent_status}"
    log "  Agent health:         ${health_status}"
    log "  Ingress reachable:    ${ingress_status}"
    log "============================================="

    if [ "$verify_passed" = true ]; then
        log "All verification checks PASSED"
        return 0
    else
        log_error "One or more verification checks FAILED"
        return 1
    fi
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --skip-verify)
                SKIP_VERIFY=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [--skip-verify]"
                echo ""
                echo "Options:"
                echo "  --skip-verify    Skip post-deploy verification"
                echo "  -h, --help       Show this help message"
                echo ""
                echo "Environment Variables:"
                echo "  VM_NAME          Multipass VM name (default: dkp-demo-k8s)"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

main() {
    parse_args "$@"
    setup_log_file

    log "============================================="
    log "  dkp-demo Full Deployment Pipeline"
    log "============================================="
    log "  VM:          $VM_NAME"
    log "  Registry:    $REGISTRY"
    log "  Skip verify: $SKIP_VERIFY"
    log "============================================="

    trap cleanup_tar_files EXIT

    if ! preflight_checks; then
        rollback_on_failure "preflight"
        exit 1
    fi

    if ! generate_secrets; then
        rollback_on_failure "secrets"
        exit 1
    fi

    if ! build_images; then
        rollback_on_failure "build"
        exit 1
    fi

    if ! check_disk_space; then
        rollback_on_failure "disk-space"
        exit 1
    fi

    if ! transfer_all_images; then
        rollback_on_failure "image-transfer"
        exit 1
    fi

    if ! apply_manifests; then
        rollback_on_failure "manifest-apply"
        exit 1
    fi

    if ! restart_deployments; then
        rollback_on_failure "restart"
        exit 1
    fi

    if [ "$SKIP_VERIFY" = false ]; then
        if ! verify_deployment; then
            rollback_on_failure "verification"
            exit 1
        fi
    else
        log "Verification skipped (--skip-verify)"
    fi

    log ""
    log "============================================="
    log "  Deployment Complete"
    log "============================================="
    log ""
    log "  Next steps:"
    log "    1. Get VM IP:    multipass info $VM_NAME"
    log "    2. Add to hosts: echo '<VM_IP> dkp-demo.local' | sudo tee -a /etc/hosts"
    log "    3. Open browser: http://dkp-demo.local"
    log ""
    log "  Useful commands:"
    log "    Pods:     multipass exec $VM_NAME -- microk8s kubectl get pods"
    log "    Logs:     multipass exec $VM_NAME -- microk8s kubectl logs -l app=dkp-demo"
    log "    Teardown: scripts/deploy/destroy-vm.sh"
    log "============================================="

    exit 0
}

main "$@"
