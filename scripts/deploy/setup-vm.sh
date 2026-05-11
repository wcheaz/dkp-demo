#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

VM_NAME="${VM_NAME:-dkp-demo-k8s}"
VM_CPUS=4
VM_MEMORY="7.7G"
VM_DISK="30G"
MAX_RETRIES=3
RETRY_DELAY=10

vm_exists() {
    multipass list --format csv 2>/dev/null | cut -d',' -f1 | grep -qx "$VM_NAME"
}

vm_is_running() {
    local state
    state=$(multipass info "$VM_NAME" 2>/dev/null | grep "^State:" | awk '{print $2}')
    [[ "$state" == "Running" ]]
}

check_multipass() {
    if ! command -v multipass >/dev/null 2>&1; then
        handle_dependency_error "multipass is not installed on the host" \
            "Install multipass from https://multipass.run/"
    fi
    log "multipass CLI available"
}

create_vm() {
    if vm_exists && vm_is_running; then
        log "VM '$VM_NAME' already exists and is running — skipping creation"
        return 0
    fi

    if vm_exists; then
        log "VM '$VM_NAME' exists but is not running — starting it"
        multipass start "$VM_NAME"
        sleep 5
        if vm_is_running; then
            log "VM '$VM_NAME' is now running"
            return 0
        fi
        log_error "Failed to start VM '$VM_NAME'"
        exit 1
    fi

    log "Creating Multipass VM '$VM_NAME' (${VM_CPUS} CPUs, ${VM_MEMORY} RAM, ${VM_DISK} disk)..."
    if ! multipass launch --name "$VM_NAME" --cpus "$VM_CPUS" --memory "$VM_MEMORY" --disk "$VM_DISK" noble; then
        handle_error 1 "Failed to create VM '$VM_NAME'" \
            "Ensure host has sufficient resources (~25 GB disk, 8 GB RAM available)" "PROVISIONING"
    fi

    local wait_count=0
    while ! vm_is_running && [ $wait_count -lt 30 ]; do
        sleep 2
        wait_count=$((wait_count + 1))
    done

    if vm_is_running; then
        log "VM '$VM_NAME' created and running"
    else
        log_error "VM '$VM_NAME' did not reach Running state within 60 seconds"
        exit 1
    fi
}

install_docker() {
    log "Checking Docker in VM..."
    if multipass exec "$VM_NAME" -- docker --version >/dev/null 2>&1 && \
       multipass exec "$VM_NAME" -- docker info >/dev/null 2>&1; then
        log "Docker already installed and running in VM — skipping"
        configure_insecure_registry
        return 0
    fi

    log "Installing Docker in VM..."
    multipass exec "$VM_NAME" -- bash -c "sudo apt-get update -qq && sudo apt-get install -y -qq docker.io"
    multipass exec "$VM_NAME" -- sudo systemctl enable docker
    multipass exec "$VM_NAME" -- sudo systemctl start docker
    multipass exec "$VM_NAME" -- sudo usermod -aG docker ubuntu
    log "Docker installed in VM"

    configure_insecure_registry
}

configure_insecure_registry() {
    log "Configuring insecure registry (localhost:32000)..."
    local daemon_json
    daemon_json=$(multipass exec "$VM_NAME" -- cat /etc/docker/daemon.json 2>/dev/null || echo "{}")

    if echo "$daemon_json" | grep -q "localhost:32000"; then
        log "Insecure registry already configured — skipping Docker restart"
        return 0
    fi

    multipass exec "$VM_NAME" -- bash -c \
        'echo "{\"insecure-registries\": [\"localhost:32000\"]}" | sudo tee /etc/docker/daemon.json > /dev/null'
    multipass exec "$VM_NAME" -- sudo systemctl restart docker
    log "Insecure registry configured and Docker restarted"
}

install_microk8s() {
    log "Checking MicroK8s in VM..."
    if multipass exec "$VM_NAME" -- sudo microk8s status --wait-ready --timeout=30 >/dev/null 2>&1; then
        log "MicroK8s already installed and running — skipping"
        return 0
    fi

    local attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        log "Installing MicroK8s via snap (attempt $attempt/$MAX_RETRIES)..."
        if multipass exec "$VM_NAME" -- sudo snap install microk8s --classic; then
            log "MicroK8s installed successfully"
            return 0
        fi

        log_warning "MicroK8s install attempt $attempt failed"
        if [ $attempt -lt $MAX_RETRIES ]; then
            log "Retrying in ${RETRY_DELAY} seconds..."
            sleep "$RETRY_DELAY"
        fi
        attempt=$((attempt + 1))
    done

    log_error "MicroK8s installation failed after $MAX_RETRIES attempts"
    log "Check snap logs: multipass exec $VM_NAME -- sudo snap logs microk8s"
    exit 1
}

configure_microk8s_user() {
    log "Adding ubuntu user to microk8s group..."
    multipass exec "$VM_NAME" -- sudo usermod -aG microk8s ubuntu
    multipass exec "$VM_NAME" -- sudo chown -R "$(id -u):$(id -g)" /home/ubuntu/.kube 2>/dev/null || true
    log "User configured for MicroK8s access"
}

wait_for_microk8s_ready() {
    log "Waiting for MicroK8s to be ready..."
    local attempt=0
    local max_attempts=60
    while [ $attempt -lt $max_attempts ]; do
        if multipass exec "$VM_NAME" -- sudo microk8s status --wait-ready --timeout=10 >/dev/null 2>&1; then
            log "MicroK8s is ready"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 5
    done
    log_error "MicroK8s did not become ready within 5 minutes"
    exit 1
}

enable_addons() {
    local addons=("dns" "ingress" "registry" "storage")

    for addon in "${addons[@]}"; do
        local addon_status
        addon_status=$(multipass exec "$VM_NAME" -- sudo microk8s status 2>/dev/null \
            | grep -oP "(?<=$addon: )\w+" || echo "disabled")

        if [[ "$addon_status" == "enabled" ]]; then
            log "Add-on '$addon' already enabled — skipping"
        else
            log "Enabling MicroK8s add-on: $addon..."
            multipass exec "$VM_NAME" -- sudo microk8s enable "$addon"
            log "Add-on '$addon' enabled"
        fi
    done
}

validate_cluster() {
    log "Validating cluster state..."

    if ! multipass exec "$VM_NAME" -- sudo microk8s status --wait-ready --timeout=30 >/dev/null 2>&1; then
        log_error "MicroK8s is not running"
        exit 1
    fi
    log "MicroK8s status: running"

    log "Checking registry at localhost:32000..."
    local registry_check
    registry_check=$(multipass exec "$VM_NAME" -- curl -sf http://localhost:32000/v2/_catalog 2>/dev/null || echo "")
    if [ -n "$registry_check" ]; then
        log "Registry accessible at localhost:32000"
    else
        log_warning "Registry not yet accessible at localhost:32000 (may need a moment to start)"
    fi

    log "Node status:"
    multipass exec "$VM_NAME" -- sudo microk8s kubectl get nodes

    log ""
    log "============================================="
    log "  VM Provisioning Complete"
    log "============================================="
    log "  VM Name:    $VM_NAME"
    log "  CPUs:       $VM_CPUS"
    log "  Memory:     $VM_MEMORY"
    log "  Disk:       $VM_DISK"
    log "  Registry:   localhost:32000 (inside VM)"
    log ""
    log "  Next steps:"
    log "    1. Get VM IP: multipass info $VM_NAME"
    log "    2. Add to /etc/hosts: <VM_IP> dkp-demo.local"
    log "    3. Run: ./deploy-all.sh"
    log "============================================="
}

main() {
    setup_log_file
    log "Starting VM provisioning for '$VM_NAME'..."

    check_multipass
    create_vm
    install_docker
    install_microk8s
    configure_microk8s_user
    wait_for_microk8s_ready
    enable_addons
    validate_cluster

    log "VM provisioning completed successfully"
}

main "$@"
