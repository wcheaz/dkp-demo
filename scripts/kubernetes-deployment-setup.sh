#!/bin/bash

################################################################################
# {{PROJECT_NAME}} Kubernetes Deployment Setup Script
# ================================================
#
# CONFIGURATION REQUIRED:
# ========================
# Before running this script, set environment variables or replace placeholders:
# (1) PROJECT_NAME - your project identifier (e.g., "my-app")
# (2) REGISTRY_HOST - your container registry address (e.g., "registry.example.com" or "localhost:32000")
#
# Default values are generic - override with:
#   VM_NAME=my-vm REGISTRY=registry.example.com ./scripts/kubernetes-deployment-setup.sh
#
# This script automates the manual deployment steps that are part of the
# human handoff process in the fix-k8s-agent-streaming workflow. It performs
# a complete end-to-end deployment of Docker images to a Kubernetes cluster
# running in a Multipass VM.
#
# Purpose:
# - After making code changes to the frontend or agent,
#   this script rebuilds the Docker images and deploys them to production
# - Eliminates the need to manually run multiple commands across the host
#   and VM during the deployment process
#
# What the script does:
# 1. Pre-flight validation: Checks that VM exists, Docker is accessible
# 2. Build phase: Builds Docker images (frontend, agent, or both)
# 3. Transfer phase: Saves images to tar files, transfers to VM, loads them
# 4. Registry phase: Tags and pushes images to local registry
# 5. Manifest phase: Applies updated Kubernetes manifests if specified
# 6. Restart phase: Restarts affected deployments to pick up new images
# 7. Verification phase: Runs verification script to test the deployment
# 8. Cleanup: Removes temporary tar files from host and VM
#
# When to use this script:
# - After implementing SSE streaming fixes in the frontend or agent code
# - After updating Kubernetes manifests (ingress.yaml, deployment.yaml, etc.)
# - Any time you need to deploy updated Docker images to the K8s cluster
#
# Related files:
# - openspec/changes/fix-k8s-agent-streaming/tasks.md (original manual steps)
# - k8s/*.yaml (Kubernetes manifests)
# - test/verify_k8s_sse_fix.sh (verification script)
#
# Usage examples:
#   scripts/kubernetes-deployment-setup.sh --build all --manifest k8s/ingress.yaml --restart --verify
#   scripts/kubernetes-deployment-setup.sh --build frontend --manifest k8s/deployment.yaml --restart
#   scripts/kubernetes-deployment-setup.sh --build agent --restart --delete-old
#
# Environment variables:
#   VM_NAME: Name of the Multipass VM (default: {{PROJECT_NAME}}-k8s)
#
# Disk space management:
#   - Without --delete-old: Script checks available disk space and fails if insufficient
#   - With --delete-old: Cleans up old Docker images and registry storage before deployment
#   - Use --delete-old when experiencing disk pressure, rollout loops, or eviction issues
#
# Environment requirements:
#   - Multipass (https://multipass.run) installed on host for VM management
#   - Docker installed on host machine for building images
#   - Docker installed inside the Multipass VM for loading images
#   - microk8s enabled inside the Multipass VM with registry addon
#   - kubectl configured to access the microk8s cluster
#
# Configuration steps:
#   1. Set VM_NAME to match your Multipass VM name (or use {{PROJECT_NAME}}-k8s default)
#   2. Set REGISTRY_HOST to match your container registry address
#   3. Ensure the VM is running: multipass start <VM_NAME>
#   4. Ensure microk8s is ready: multipass exec <VM_NAME> -- microk8s status
#
# Adapting for other Kubernetes environments:
#   If NOT using Multipass + microk8s (e.g., minikube, k3d, cloud provider):
#   - Replace multipass exec <VM_NAME> -- <command> with direct kubectl commands
#   - Remove multipass transfer commands and use direct registry push
#   - Adjust registry configuration for your environment's container registry
#   - Modify the VM existence check to use your environment's node discovery
#   - Update disk space checks for your environment's monitoring tools
################################################################################

set -e

# Configuration
# Replace {{PROJECT_NAME}} with your project identifier (e.g., "my-app")
# Replace {{REGISTRY_HOST}} with your container registry (e.g., "localhost:32000" or "registry.example.com")
VM_NAME="${VM_NAME:-{{PROJECT_NAME}}-k8s}"
REGISTRY="{{REGISTRY_HOST}}"
FRONTEND_IMAGE_NAME="{{PROJECT_NAME}}"
AGENT_IMAGE_NAME="agent"
FRONTEND_DEPLOYMENT="{{PROJECT_NAME}}"
AGENT_DEPLOYMENT="agent"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -b, --build BUILD_TYPE     What to build: frontend, agent, or all (default: all)"
    echo "  -m, --manifest FILE        K8s manifest to apply (can be specified multiple times)"
    echo "  -r, --restart              Restart deployments after applying manifests"
    echo "  -v, --verify               Run verification script after deployment"
    echo "  -d, --delete-old           Delete old image data before deployment (cleans disk space)"
    echo "  -h, --help                 Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  VM_NAME                    Name of the Multipass VM (default: {{PROJECT_NAME}}-k8s)"
    echo ""
    echo "Examples:"
    echo "  $0 --build all --manifest k8s/ingress.yaml --restart --verify"
    echo "  $0 --build frontend --manifest k8s/deployment.yaml --restart"
    echo "  $0 --build agent --restart --delete-old"
    echo ""
    echo "Notes:"
    echo "  - Use --delete-old when experiencing disk pressure or rollout loops"
    echo "  - Without --delete-old, script checks disk space and fails if insufficient"
    exit 1
}

# Function to check disk space on VM
check_disk_space() {
    log_info "Checking disk space on VM..."

    # Get available disk space in KB
    AVAILABLE_KB=$(multipass exec "$VM_NAME" -- df --output=avail / | tail -n1)
    if [ -z "$AVAILABLE_KB" ]; then
        log_error "Failed to get disk space from VM"
        exit 1
    fi

    # Convert to GB
    AVAILABLE_GB=$((AVAILABLE_KB / 1024 / 1024))

    log_info "Available disk space: ${AVAILABLE_GB}GB"

    # Calculate required space based on build type
    REQUIRED_GB=0
    if [[ "$BUILD_TYPE" == "frontend" || "$BUILD_TYPE" == "all" ]]; then
        REQUIRED_GB=$((REQUIRED_GB + 1))  # Frontend is ~300MB, reserve 1GB
    fi
    if [[ "$BUILD_TYPE" == "agent" || "$BUILD_TYPE" == "all" ]]; then
        REQUIRED_GB=$((REQUIRED_GB + 5))  # Agent is ~4.2GB, reserve 5GB
    fi

    # Add safety margin (2GB)
    REQUIRED_GB=$((REQUIRED_GB + 2))

    log_info "Required disk space: ${REQUIRED_GB}GB"

    if [ "$AVAILABLE_GB" -lt "$REQUIRED_GB" ]; then
        log_error "Insufficient disk space on VM!"
        log_error "Available: ${AVAILABLE_GB}GB, Required: ${REQUIRED_GB}GB"
        log_error ""
        log_error "To free up space, run with --delete-old flag:"
        log_error "  $0 --build $BUILD_TYPE --restart --delete-old"
        log_error ""
        log_error "Or manually clean up:"
        log_error "  multipass exec $VM_NAME -- docker image prune -a -f"
        log_error "  multipass exec $VM_NAME -- df -h /"
        exit 1
    fi

    log_info "✅ Disk space check passed"
}

# Function to clean up old image data
cleanup_old_images() {
    log_warn "Cleaning up old image data..."

    # Prune unused Docker images in VM
    log_info "Pruning unused Docker images..."
    RECLAIMED=$(multipass exec "$VM_NAME" -- docker image prune -a -f 2>&1 | grep "Total reclaimed space" || echo "0B")
    log_info "Docker images reclaimed: $RECLAIMED"

    # Clean up registry storage
    log_info "Cleaning up registry storage..."

    # First, delete the registry pod if it exists
    REGISTRY_POD=$(multipass exec "$VM_NAME" -- microk8s kubectl get pods -n container-registry -o name 2>/dev/null || echo "")
    if [ -n "$REGISTRY_POD" ]; then
        log_info "Deleting registry pod: $REGISTRY_POD"
        multipass exec "$VM_NAME" -- microk8s kubectl delete "$REGISTRY_POD" -n container-registry --grace-period=5 >/dev/null 2>&1 || true

        # Wait for pod to be deleted (max 30 seconds)
        log_info "Waiting for registry pod to be deleted..."
        for i in {1..6}; do
            POD_EXISTS=$(multipass exec "$VM_NAME" -- microk8s kubectl get pods -n container-registry -o name 2>/dev/null || echo "")
            if [ -z "$POD_EXISTS" ]; then
                log_info "✅ Registry pod deleted"
                break
            fi
            if [ $i -eq 6 ]; then
                log_warn "Registry pod not deleted after 30 seconds, forcing deletion..."
                multipass exec "$VM_NAME" -- microk8s kubectl delete "$REGISTRY_POD" -n container-registry --force --grace-period=0 >/dev/null 2>&1 || true
                sleep 2
            fi
            sleep 5
        done
    fi

        # Find and delete registry PVC
        REGISTRY_PVC=$(multipass exec "$VM_NAME" -- microk8s kubectl get pvc -n container-registry -o name 2>/dev/null | grep registry-claim || true)

        if [ -n "$REGISTRY_PVC" ]; then
            log_info "Deleting registry PVC: $REGISTRY_PVC"

            # Try to remove PVC finalizer if it's stuck
            log_info "Removing PVC finalizer if present..."
            multipass exec "$VM_NAME" -- microk8s kubectl patch "$REGISTRY_PVC" -n container-registry --type merge -p '{"metadata":{"finalizers":[]}}' >/dev/null 2>&1 || true
            sleep 2

            multipass exec "$VM_NAME" -- microk8s kubectl delete "$REGISTRY_PVC" -n container-registry --grace-period=5 >/dev/null 2>&1 || true

        # Wait for PVC to be deleted (max 30 seconds)
        log_info "Waiting for registry PVC to be deleted..."
        for i in {1..6}; do
            PVC_EXISTS=$(multipass exec "$VM_NAME" -- microk8s kubectl get pvc -n container-registry -o name 2>/dev/null | grep registry-claim || echo "")
            if [ -z "$PVC_EXISTS" ]; then
                log_info "✅ Registry PVC deleted"
                break
            fi
            if [ $i -eq 6 ]; then
                log_warn "Registry PVC not deleted after 30 seconds, continuing anyway..."
                break
            fi
            sleep 5
        done

        # Find and delete the PV
        PV_NAME=$(multipass exec "$VM_NAME" -- microk8s kubectl get pv -o name | grep pvc- || true)
        if [ -n "$PV_NAME" ]; then
            log_info "Deleting registry PV: $PV_NAME"

            # First, try to remove the protection finalizer if PV is stuck
            log_info "Removing PV protection finalizer if present..."
            multipass exec "$VM_NAME" -- microk8s kubectl patch "$PV_NAME" --type merge -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain","claimRef":null},"metadata":{"finalizers":[]}}' >/dev/null 2>&1 || true
            sleep 2

            multipass exec "$VM_NAME" -- microk8s kubectl delete "$PV_NAME" --grace-period=5 >/dev/null 2>&1 || true

            # Wait for PV to be deleted (max 30 seconds)
            for i in {1..6}; do
                PV_EXISTS=$(multipass exec "$VM_NAME" -- microk8s kubectl get pv -o name | grep "$PV_NAME" || echo "")
                if [ -z "$PV_EXISTS" ]; then
                    log_info "✅ Registry PV deleted"
                    break
                fi
                if [ $i -eq 6 ]; then
                    log_warn "Registry PV not deleted after 30 seconds, continuing anyway..."
                    break
                fi
                sleep 5
            done
        fi

        # Remove storage directory if it still exists
        STORAGE_DIR=$(multipass exec "$VM_NAME" -- ls -d /var/snap/microk8s/common/default-storage/container-registry-registry-claim-pvc-* 2>/dev/null || true)
        if [ -n "$STORAGE_DIR" ]; then
            log_info "Removing registry storage directory..."
            multipass exec "$VM_NAME" -- sudo rm -rf "$STORAGE_DIR" 2>/dev/null || true
            log_info "✅ Storage directory removed"
        fi

        # Try to remove PVC finalizer if it's still stuck
        PVC_STUCK=$(multipass exec "$VM_NAME" -- microk8s kubectl get pvc -n container-registry -o name 2>/dev/null | grep registry-claim || echo "")
        if [ -n "$PVC_STUCK" ]; then
            log_info "Removing stuck PVC finalizer..."
            multipass exec "$VM_NAME" -- microk8s kubectl patch "$PVC_STUCK" -n container-registry --type merge -p '{"metadata":{"finalizers":[]}}' >/dev/null 2>&1 || true
            sleep 2
        fi
    fi

    # Recreate the registry PVC
    log_info "Recreating registry PVC..."
    multipass exec "$VM_NAME" -- bash -c 'cat <<EOF | microk8s kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: registry-claim
  namespace: container-registry
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 20Gi
  storageClassName: microk8s-hostpath
EOF
' >/dev/null 2>&1

    # Wait for new registry pod to be created
    log_info "Waiting for new registry pod to be created..."

    # Wait for registry pod to be created and running (max 120 seconds)
    log_info "Waiting for registry pod to be ready..."
    for i in {1..24}; do
        READY_COUNT=$(multipass exec "$VM_NAME" -- microk8s kubectl get pods -n container-registry 2>/dev/null | grep -c "1/1.*Running" 2>/dev/null || true)
        READY_COUNT=$(echo "$READY_COUNT" | tr -d '[:space:]')

        if [ "$READY_COUNT" -ge 1 ] 2>/dev/null; then
            log_info "✅ Registry is ready"
            break
        fi
        if [ $i -eq 24 ]; then
            log_warn "Registry not ready after 120 seconds, continuing anyway..."
        fi
        sleep 5
    done

    # Check final disk usage
    AVAILABLE_KB=$(multipass exec "$VM_NAME" -- df --output=avail / | tail -n1)
    AVAILABLE_GB=$((AVAILABLE_KB / 1024 / 1024))
    log_info "Available disk space after cleanup: ${AVAILABLE_GB}GB"

    log_info "✅ Cleanup completed"
}

# Parse arguments
BUILD_TYPE="all"
MANIFESTS=()
RESTART_DEPLOYMENTS=false
RUN_VERIFICATION=false
DELETE_OLD_IMAGES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--build)
            BUILD_TYPE="$2"
            shift 2
            ;;
        -m|--manifest)
            MANIFESTS+=("$2")
            shift 2
            ;;
        -r|--restart)
            RESTART_DEPLOYMENTS=true
            shift
            ;;
        -v|--verify)
            RUN_VERIFICATION=true
            shift
            ;;
        -d|--delete-old)
            DELETE_OLD_IMAGES=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate build type
if [[ "$BUILD_TYPE" != "frontend" && "$BUILD_TYPE" != "agent" && "$BUILD_TYPE" != "all" ]]; then
    log_error "Invalid build type: $BUILD_TYPE. Must be frontend, agent, or all"
    exit 1
fi

log_info "Starting Kubernetes deployment setup"
log_info "VM: $VM_NAME"
log_info "Build type: $BUILD_TYPE"

# Pre-flight checks
log_info "Running pre-flight checks..."

# Check if VM exists
if ! multipass list | grep -q "$VM_NAME"; then
    log_error "VM '$VM_NAME' not found. Please create the VM first."
    exit 1
fi

# Check if Docker is accessible
if ! docker info >/dev/null 2>&1; then
    log_error "Docker daemon is not accessible. Start Docker daemon: sudo systemctl start docker"
    exit 1
fi

# Check if Docker in VM is accessible
if ! multipass exec "$VM_NAME" -- docker info >/dev/null 2>&1; then
    log_error "Docker daemon not accessible in VM. Cannot transfer images."
    exit 1
fi

log_info "✅ Pre-flight checks passed"

# Configure Docker in VM to use insecure registry
# The MicroK8s registry is HTTP-only on localhost:32000, but Docker defaults
# to HTTPS and may resolve localhost to IPv6 [::1], causing connection refused.
log_info "Configuring Docker in VM for insecure registry..."
NEEDS_DOCKER_RESTART=false
DAEMON_JSON_EXISTS=$(multipass exec "$VM_NAME" -- test -f /etc/docker/daemon.json && echo "yes" || echo "no")

if [ "$DAEMON_JSON_EXISTS" = "no" ]; then
    multipass exec "$VM_NAME" -- sudo mkdir -p /etc/docker
    multipass exec "$VM_NAME" -- sudo bash -c "cat > /etc/docker/daemon.json <<'DEOF'
{
  \"insecure-registries\": [\"{{REGISTRY_HOST}}\"]
}
DEOF"
    NEEDS_DOCKER_RESTART=true
    log_info "Created /etc/docker/daemon.json"
else
    # Check if insecure-registries already includes our registry
    HAS_INSECURE=$(multipass exec "$VM_NAME" -- grep -c "{{REGISTRY_HOST}}" /etc/docker/daemon.json 2>/dev/null || echo "0")
    if [ "$HAS_INSECURE" -eq 0 ]; then
        log_info "Adding {{REGISTRY_HOST}} to insecure-registries in existing daemon.json..."
        multipass exec "$VM_NAME" -- sudo python3 -c "
import json, sys
with open('/etc/docker/daemon.json') as f:
    config = json.load(f)
ir = config.get('insecure-registries', [])
if '{{REGISTRY_HOST}}' not in ir:
    ir.append('{{REGISTRY_HOST}}')
config['insecure-registries'] = ir
with open('/etc/docker/daemon.json', 'w') as f:
    json.dump(config, f, indent=2)
"
        NEEDS_DOCKER_RESTART=true
    fi
fi

if [ "$NEEDS_DOCKER_RESTART" = true ]; then
    log_info "Restarting Docker in VM..."
    multipass exec "$VM_NAME" -- sudo systemctl restart docker
    # Wait for Docker to be ready
    for i in {1..12}; do
        if multipass exec "$VM_NAME" -- docker info >/dev/null 2>&1; then
            log_info "✅ Docker in VM restarted and ready"
            break
        fi
        if [ $i -eq 12 ]; then
            log_error "Docker in VM not ready after 60 seconds"
            exit 1
        fi
        sleep 5
    done
else
    log_info "✅ Docker in VM already configured for insecure registry"
fi

# Cleanup old images if requested
if [ "$DELETE_OLD_IMAGES" = true ]; then
    cleanup_old_images
else
    # Check disk space before proceeding
    check_disk_space
fi

# Function to build and transfer image
build_and_transfer_image() {
    local image_name="$1"
    local build_context="$2"
    local dockerfile_path="${3:-Dockerfile}"
    
    log_info "Building $image_name:latest..."
    
    # Build image
    if ! docker build -t "$image_name:latest" -f "$dockerfile_path" "$build_context"; then
        log_error "Failed to build $image_name:latest"
        return 1
    fi
    
    log_info "✅ $image_name:latest built successfully"
    
    # Get image ID
    IMAGE_ID=$(docker images "$image_name:latest" --format "{{.ID}}" 2>/dev/null | head -n1)
    if [ -z "$IMAGE_ID" ]; then
        log_error "Cannot find image ID for $image_name:latest"
        return 1
    fi
    log_info "Image ID: $IMAGE_ID"
    
    # Save image to tar
    TAR_FILE="./${image_name}.tar"
    log_info "Saving image to $TAR_FILE..."
    if ! docker save "$IMAGE_ID" -o "$TAR_FILE"; then
        log_error "Failed to save $image_name image"
        return 1
    fi
    
    log_info "✅ Image saved to $TAR_FILE ($(ls -lh "$TAR_FILE" | awk '{print $5}'))"
    
    # Transfer to VM
    log_info "Transferring $TAR_FILE to VM..."
    if ! multipass transfer "$TAR_FILE" "$VM_NAME:/tmp/"; then
        log_error "Failed to transfer $TAR_FILE to VM"
        rm -f "$TAR_FILE"
        return 1
    fi
    
    log_info "✅ Image transferred to VM"
    
    # Load image in VM
    log_info "Loading image in VM..."
    load_output=$(multipass exec "$VM_NAME" -- docker load -i "/tmp/${image_name}.tar" 2>&1)
    if [ $? -ne 0 ]; then
        log_error "Failed to load $image_name image in VM"
        multipass exec "$VM_NAME" -- rm -f "/tmp/${image_name}.tar"
        rm -f "$TAR_FILE"
        return 1
    fi
    
    log_info "✅ Image loaded in VM"
    
    # Extract image ID from load output
    VM_IMAGE_ID=$(echo "$load_output" | grep -o 'sha256:[a-f0-9]\+')
    if [ -z "$VM_IMAGE_ID" ]; then
        log_error "Could not extract image ID from load output"
        multipass exec "$VM_NAME" -- rm -f "/tmp/${image_name}.tar"
        rm -f "$TAR_FILE"
        return 1
    fi
    
    # Tag and push to registry
    TARGET_IMAGE="${REGISTRY}/${image_name}:latest"
    log_info "Tagging image as $TARGET_IMAGE..."
    if ! multipass exec "$VM_NAME" -- docker tag "$VM_IMAGE_ID" "$TARGET_IMAGE"; then
        log_error "Failed to tag $image_name image"
        multipass exec "$VM_NAME" -- rm -f "/tmp/${image_name}.tar"
        rm -f "$TAR_FILE"
        return 1
    fi
    
    log_info "Pushing image to registry..."
    if ! multipass exec "$VM_NAME" -- docker push "$TARGET_IMAGE"; then
        log_error "Failed to push $image_name image to registry"
        multipass exec "$VM_NAME" -- rm -f "/tmp/${image_name}.tar"
        rm -f "$TAR_FILE"
        return 1
    fi
    
    log_info "✅ $image_name successfully pushed to $TARGET_IMAGE"
    
    # Cleanup
    rm -f "$TAR_FILE"
    multipass exec "$VM_NAME" -- rm -f "/tmp/${image_name}.tar"
}

# Build and transfer images based on build type
if [[ "$BUILD_TYPE" == "frontend" || "$BUILD_TYPE" == "all" ]]; then
    build_and_transfer_image "$FRONTEND_IMAGE_NAME" "." "Dockerfile"
    if [ $? -ne 0 ]; then
        log_error "Frontend image build/transfer failed"
        exit 1
    fi
fi

if [[ "$BUILD_TYPE" == "agent" || "$BUILD_TYPE" == "all" ]]; then
    build_and_transfer_image "$AGENT_IMAGE_NAME" "./agent" "agent/Dockerfile"
    if [ $? -ne 0 ]; then
        log_error "Agent image build/transfer failed"
        exit 1
    fi
fi

# Apply K8s manifests if specified
if [ ${#MANIFESTS[@]} -gt 0 ]; then
    log_info "Applying Kubernetes manifests..."
    
    for manifest in "${MANIFESTS[@]}"; do
        if [ ! -f "$manifest" ]; then
            log_error "Manifest file not found: $manifest"
            exit 1
        fi
        
        log_info "Applying $manifest..."
        MANIFEST_NAME=$(basename "$manifest")
        
        if ! multipass transfer "$manifest" "$VM_NAME:/home/ubuntu/$MANIFEST_NAME"; then
            log_error "Failed to transfer $manifest to VM"
            exit 1
        fi
        
        if ! multipass exec "$VM_NAME" -- microk8s kubectl apply -f "/home/ubuntu/$MANIFEST_NAME"; then
            log_error "Failed to apply $manifest"
            exit 1
        fi
        
        log_info "✅ Applied $manifest"
    done
fi

# Restart deployments if requested
if [ "$RESTART_DEPLOYMENTS" = true ]; then
    log_info "Restarting deployments..."
    
    DEPLOYMENTS_TO_RESTART=()
    
    if [[ "$BUILD_TYPE" == "frontend" || "$BUILD_TYPE" == "all" ]]; then
        DEPLOYMENTS_TO_RESTART+=("$FRONTEND_DEPLOYMENT")
    fi
    
    if [[ "$BUILD_TYPE" == "agent" || "$BUILD_TYPE" == "all" ]]; then
        DEPLOYMENTS_TO_RESTART+=("$AGENT_DEPLOYMENT")
    fi
    
    for deployment in "${DEPLOYMENTS_TO_RESTART[@]}"; do
        log_info "Restarting deployment/$deployment..."
        if ! multipass exec "$VM_NAME" -- microk8s kubectl rollout restart deployment/"$deployment"; then
            log_error "Failed to restart deployment/$deployment"
            exit 1
        fi
        
        log_info "Waiting for rollout to complete..."
        if ! multipass exec "$VM_NAME" -- microk8s kubectl rollout status deployment/"$deployment"; then
            log_error "Rollout status check failed for $deployment"
            exit 1
        fi
        
        log_info "✅ Deployment $deployment restarted successfully"
    done
fi

# Run verification if requested
if [ "$RUN_VERIFICATION" = true ]; then
    log_info "Running verification script..."
    
    if [ ! -f "test/verify_k8s_sse_fix.sh" ]; then
        log_warn "Verification script not found at test/verify_k8s_sse_fix.sh, skipping verification"
    else
        if ! bash test/verify_k8s_sse_fix.sh; then
            log_error "Verification failed"
            log_info "To rollback, run: multipass exec $VM_NAME -- microk8s kubectl rollout undo deployment/<deployment-name>"
            exit 1
        fi
        log_info "✅ Verification passed"
    fi
fi

log_info "🎉 Deployment completed successfully!"
log_info ""
log_info "Next steps:"
log_info "  - Check pod status: multipass exec $VM_NAME -- microk8s kubectl get pods"
log_info "  - View logs: multipass exec $VM_NAME -- microk8s kubectl logs -f deployment/<deployment-name>"
log_info "  - To rollback (if needed): multipass exec $VM_NAME -- microk8s kubectl rollout undo deployment/<deployment-name>"

exit 0
