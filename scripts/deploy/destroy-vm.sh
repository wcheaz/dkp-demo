#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

VM_NAME="${VM_NAME:-dkp-demo-k8s}"

vm_exists() {
    multipass list --format csv 2>/dev/null | cut -d',' -f1 | grep -qx "$VM_NAME"
}

main() {
    setup_log_file
    log "Starting teardown of VM '$VM_NAME'..."

    if ! vm_exists; then
        log "VM '$VM_NAME' not found — nothing to destroy"
        exit 0
    fi

    log "Stopping VM '$VM_NAME'..."
    multipass stop "$VM_NAME"
    log "VM '$VM_NAME' stopped"

    log "Deleting VM '$VM_NAME'..."
    multipass delete "$VM_NAME"
    log "VM '$VM_NAME' deleted"

    log "Purging deleted VMs..."
    multipass purge
    log "Purge complete"

    log ""
    log "============================================="
    log "  VM Teardown Complete"
    log "============================================="
    log "  VM '$VM_NAME' has been removed"
    log ""
    log "  To recreate: scripts/deploy/setup-vm.sh"
    log "============================================="
}

main "$@"
