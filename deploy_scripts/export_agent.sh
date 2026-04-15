#!/bin/bash
# ============================================================================
# AGENT DEPLOYMENT SCRIPT FOR KUBERNETES
# ============================================================================
#
# This script automates the deployment of the agent service to Kubernetes
# running inside a Multipass VM (dkp-demo-k8s).
#
# USAGE:
#   ./deploy_scripts/export_agent.sh [update|verify|restart]
#
#   update: Build and push new agent image to VM registry
#   verify: Check current deployment status and health
#   restart: Restart agent deployment
#
# PREREQUISITES:
#   - Docker CLI available on host
#   - Multipass VM running: multipass list
#   - Agent source code exists at ./agent/
# ============================================================================

set -e errexit
set -e pipefail
set -u

# Configuration
VM_NAME="dkp-demo-k8s"
REGISTRY="${VM_NAME}:32000"
REGISTRY_INTERNAL="localhost:32000"
IMAGE_NAME="agent"
IMAGE_TAG="latest"
DEPLOYMENT_NAME="agent"
SERVICE_NAME="agent-service"
NAMESPACE="default"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_separator() {
    echo ""
}

# Check Multipass VM status
check_vm_running() {
    if multipass list | grep -q "^${VM_NAME}.*Running"; then
        return 0
    else
        log_error "Multipass VM '${VM_NAME}' is not running"
        return 1
    fi
}

# Get host IP
get_vm_ip() {
    multipass list --format json | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    vm = next((v for v in data['list'] if v['name'] == '${VM_NAME}' and 'Running' in v['state']))
    if vm:
        for ip_data in vm['ipv4']:
            if ip_data.get('type') == 'IPv4' and not ip_data.get('mac'):
                ip = ip_data['ipv4'][0]
                break
        print(ip)
except:
        print('NOT_FOUND')
        sys.exit(1)
"
}

# Disk space management
check_vm_disk_space() {
    log_step "Checking VM disk space..."
    local free_percent
    free_percent=$(multipass exec "${VM_NAME}" -- df -h / | awk 'NR==4 {print int($5)}' 2>/dev/null)
    
    if [ -z "$free_percent" ]; then
        free_percent=0
    fi
    
    if [ "$free_percent" -lt 10 ]; then
        log_info "VM disk space: ${free_percent}% free"
        return 0
    else
        log_warning "VM disk space low: ${free_percent}% free (<10%)"
        log_warning "Consider cleaning up old images/pods or increasing VM disk size"
        return 1
    fi
}

# Build agent image
build_agent_image() {
    log_step "Building agent Docker image..."
    
    if [ ! -d "./agent" ]; then
        log_error "Agent directory './agent/' not found"
        return 1
    fi
    
    docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" ./agent/ 2>&1 | tee /tmp/agent_build.log
    
    if [ $? -ne 0 ]; then
        log_error "Docker build failed. Check /tmp/agent_build.log"
        return 1
    fi
    
    log_step "Verifying image contents..."
    if ! docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" ls -la /app/src/ | grep -q "agent.py\|main.py"; then
        log_error "Image verification failed - missing Python source files"
        return 1
    fi
    
    local image_size
    image_size=$(docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "{{.Size}}" 2>/dev/null)
    log_info "Image size: ${image_size}"
    
    log_success "Docker image built successfully"
    return 0
}

# Transfer and deploy
transfer_and_push() {
    log_step "Transferring image to VM..."
    
    if ! check_vm_disk_space; then
        log_error "VM disk space insufficient"
        return 1
    fi
    
    log_step "Creating tar file..."
    docker save "${IMAGE_NAME}:${IMAGE_TAG}" -o ./agent.tar 2>&1 | tee /tmp/agent_transfer.log
    
    if [ $? -ne 0 ]; then
        log_error "Docker save failed. Check /tmp/agent_transfer.log"
        return 1
    fi
    
    local tar_size
    tar_size=$(ls -lh ./agent.tar | awk '{print $5}')
    log_info "Tar file size: ${tar_size}"
    
    log_step "Transferring to VM..."
    multipass transfer ./agent.tar "${VM_NAME}:/tmp/agent.tar"
    
    if [ $? -ne 0 ]; then
        log_error "Transfer to VM failed"
        return 1
    fi
    
    log_step "Loading image in VM Docker..."
    multipass exec "${VM_NAME}" -- docker load -i /tmp/agent.tar
    
    if [ $? -ne 0 ]; then
        log_error "Docker load in VM failed"
        return 1
    fi
    
    local image_id
    image_id=$(multipass exec "${VM_NAME}" -- docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "{{.ID}}" | head -n1)
    log_info "Image ID: ${image_id}"
    
    log_step "Tagging image for VM registry..."
    multipass exec "${VM_NAME}" -- docker tag "${image_id}" "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    
    if [ $? -ne 0 ]; then
        log_error "Docker tag failed"
        return 1
    fi
    
    log_step "Pushing to VM registry..."
    multipass exec "${VM_NAME}" -- docker push "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}" 2>&1 | tee /tmp/agent_push.log
    
    if [ $? -ne 0 ]; then
        log_error "Docker push failed. Check /tmp/agent_push.log"
        return 1
    fi
    
    log_step "Cleaning up VM Docker..."
    multipass exec "${VM_NAME}" -- docker system prune -a -f --volumes 2>&1
    
    log_success "Image pushed to ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    return 0
}

# Restart deployment
restart_agent_deployment() {
    log_step "Restarting agent deployment..."
    
    multipass exec "${VM_NAME}" -- microk8s kubectl rollout restart deployment "${DEPLOYMENT_NAME}"
    
    if [ $? -ne 0 ]; then
        log_error "Deployment restart failed"
        return 1
    fi
    
    log_step "Waiting for rollout to complete..."
    sleep 15
    
    multipass exec "${VM_NAME}" -- microk8s kubectl get pods -l "app=${IMAGE_NAME}" -o wide
    
    log_success "Deployment restarted"
    return 0
}

# Verify deployment
verify_deployment() {
    log_step "Verifying agent deployment..."
    
    log_step "Checking pod status..."
    local pod_status
    pod_status=$(multipass exec "${VM_NAME}" -- microk8s kubectl get pods -l "app=${IMAGE_NAME}" --no-headers | awk 'NR==1 {print $1}' 2>/dev/null)
    
    if [ "$pod_status" == "1/1" ]; then
        log_info "Agent pod: Running and Ready"
    else
        log_warning "Agent pod status: ${pod_status} (expected 1/1)"
    fi
    
    log_step "Checking service endpoints..."
    local endpoints
    endpoints=$(multipass exec "${VM_NAME}" -- microk8s kubectl get ep "${SERVICE_NAME}" --no-headers 2>/dev/null)
    
    if [ -n "$endpoints" ]; then
        log_success "Service has endpoints: ${endpoints}"
    else
        log_warning "Service has no endpoints"
    fi
    
    log_step "Getting agent pod logs (last 30 lines)..."
    local pod_name
    pod_name=$(multipass exec "${VM_NAME}" -- microk8s kubectl get pods -l "app=${IMAGE_NAME}" --no-headers | awk 'NR==1 {print $1}')
    
    multipass exec "${VM_NAME}" -- microk8s kubectl logs "${pod_name}" --tail=30 2>&1 | tee /tmp/agent_pod_logs.log
    
    log_info "Logs saved to /tmp/agent_pod_logs.log"
    
    log_step "Testing agent health from host..."
    local health_check
    health_check=$(curl -s http://localhost:32000/v2/agent/manifests/latest 2>&1 | python3 -m json.tool 2>/dev/null | grep -oE "digest" | head -1 | awk '{print $1}')
    
    if [ -n "$health_check" ]; then
        log_info "Registry digest: ${health_check}"
    else
        log_error "No registry digest found"
    fi
    
    return 0
}

# Main execution
main() {
    local command="${1:-}"
    
    print_separator
    echo "AGENT DEPLOYMENT SCRIPT"
    echo "====================="
    print_separator
    
    log_info "Checking prerequisites..."
    
    if ! check_vm_running; then
        exit 1
    fi
    
    if ! get_vm_ip > /dev/null; then
        log_error "Failed to get VM IP address"
        exit 1
    fi
    
    local vm_ip
    vm_ip=$(cat /tmp/vm_ip)
    
    echo "VM: ${VM_NAME}"
    echo "VM IP: ${vm_ip}"
    echo "Registry: ${REGISTRY}"
    print_separator
    
    case "$command" in
        update)
            log_step "Starting UPDATE workflow..."
            
            if ! grep -q "ENV HOME=/home/appuser" ./agent/Dockerfile; then
                log_warning "Dockerfile missing ENV HOME=/home/appuser"
            fi
            
            build_agent_image
            if [ $? -ne 0 ]; then
                exit 1
            fi
            
            check_vm_disk_space
            if [ $? -ne 0 ]; then
                exit 1
            fi
            
            transfer_and_push
            if [ $? -ne 0 ]; then
                exit 1
            fi
            
            restart_agent_deployment
            if [ $? -ne 0 ]; then
                exit 1
            fi
            
            log_success "UPDATE workflow completed"
            ;;
            
        verify)
            log_step "Starting VERIFICATION workflow..."
            verify_deployment
            if [ $? -ne 0 ]; then
                exit 1
            fi
            ;;
            
        restart)
            log_step "Starting RESTART workflow..."
            restart_agent_deployment
            if [ $? -ne 0 ]; then
                exit 1
            fi
            ;;
            
        *)
            echo "Usage: $0 <command>"
            echo ""
            echo "Commands:"
            echo "  update  - Build and push new agent image to Kubernetes"
            echo "  verify  - Check agent deployment status and health"
            echo "  restart  - Restart agent deployment"
            echo ""
            echo "Examples:"
            echo "  $0 deploy_scripts/export_agent.sh update"
            echo "  $0 deploy_scripts/export_agent.sh verify"
            echo "  $0 deploy_scripts/export_agent.sh restart"
            print_separator
            exit 1
            ;;
    esac
}

main "$@"
