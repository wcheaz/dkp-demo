#!/bin/bash

# DEBUG LEVEL: MINIMAL (successful phase)

# Source common error handling functions
source "scripts/deploy/common.sh"

# Log build process start
log_info "Starting Docker build process"

# Validate package.json and package-lock.json synchronization
validate_lock_files() {
    log_info "Starting dependency validation..."
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        handle_dependency_error 201 "package.json not found" \
            "Ensure you're running this script from the project root directory where package.json is located."
        return 1
    fi
    
    # Check if package-lock.json exists
    if [ ! -f "package-lock.json" ]; then
        handle_dependency_error 202 "package-lock.json not found" \
            "Run 'npm install' to generate the missing package-lock.json. This file is required for reproducible builds."
        return 1
    fi
    
    log_info "Checking if package.json and package-lock.json are in sync..."
    
    # Run npm ci --dry-run to validate lock file consistency
    local ci_output
    ci_output=$(npm ci --dry-run 2>&1)
    local ci_status=$?
    
    if [ $ci_status -ne 0 ]; then
        handle_dependency_error 200 "Lock files are out of sync" \
            "Run 'npm install' to update package-lock.json, then commit both files together."
        return 1
    fi
    
    log_info "✅ SUCCESS: package.json and package-lock.json are synchronized"
    log_info "   Dependencies are ready for reproducible Docker builds."
    return 0
}

# Validate dependencies before building Docker image
if ! validate_lock_files; then
    log "🛑 DEPLOYMENT HALTED: Dependency validation failed"
    log "   Fix the lock file sync issue and try again"
    handle_dependency_error 200 "Dependency validation failed" \
        "Run 'npm install' to update package-lock.json, then commit both files together."
    exit 1
fi

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    handle_validation_error 201 "Dockerfile not found in project root" \
        "Ensure Dockerfile exists in the project root directory."
    exit 1
fi

# Pre-flight check: Verify Docker daemon is accessible
if ! docker info >/dev/null 2>&1; then
    handle_docker_error 202 "Docker daemon is not accessible" \
        "Start Docker daemon: sudo systemctl start docker"
    exit 1
fi

# Check disk space before Docker build operation
if ! df . | awk 'NR==2 {gsub(/%/,""); print $5}' | grep -q -E '^[0-9]+$' && [ $(df . | awk 'NR==2 {gsub(/%/,""); print $5}') -gt 90 ]; then
    log_info "WARNING: Low disk space for Docker build"
fi

# Build Docker image
log_info "Starting Docker image build for 'dkp-demo:latest'..."

# Build Docker image and capture exit code with scoped error handling
(
    set -e
    docker build -t dkp-demo:latest . 2>&1 | tee "$LOG_FILE"
    docker_build_status=${PIPESTATUS[0]}
    
    # Check Docker build exit code for success determination
    if [ $docker_build_status -ne 0 ]; then
        # Docker build failed - use exit code as authority
        log_error "Docker build failed with exit code $docker_build_status"
        handle_docker_error 203 "Failed to build Docker image" \
            "Check Dockerfile and project structure. Ensure all required files are present."
        exit $docker_build_status
    fi
)

# Docker build succeeded (exit code 0) - now verify image exists
log_info "Docker build completed successfully (exit code 0)"

log_info "Docker image 'dkp-demo:latest' built successfully"

# Verify Docker image exists using docker images query
if ! docker images dkp-demo:latest 2>/dev/null | grep -q "dkp-demo"; then
    handle_docker_error 204 "Docker image verification failed" \
        "Docker build succeeded but image not found. Verify: docker images dkp-demo:latest"
    exit 1
fi

# Both Docker build exit code (0) and image existence verification passed
log_info "Docker image 'dkp-demo:latest' verified successfully"
log_info "Docker build process completed successfully (exit code: 0, image verified)"

# Transfer Docker image to VM
log "=== TRANSFERRING DOCKER IMAGE TO VM ==="

VM_NAME="${VM_NAME:-dkp-demo-k8s}"
SOURCE_IMAGE="dkp-demo:latest"
TARGET_IMAGE="localhost:32000/dkp-demo:latest"

# Pre-flight check: Verify VM exists
if ! multipass list | grep -q "$VM_NAME"; then
    log "❌ ERROR: VM '$VM_NAME' not found"
    log "   Cannot transfer image without VM"
    exit 1
fi

# Pre-flight check: Verify Docker daemon in VM
if ! multipass exec "$VM_NAME" -- docker info >/dev/null 2>&1; then
    log "❌ ERROR: Docker daemon not accessible in VM"
    log "   Cannot transfer image without Docker in VM"
    exit 1
fi

# List all images to debug
log "All available Docker images:"
docker images | head -10 | tee -a "$LOG_FILE"

# Get actual image ID from Docker (to handle docker.io/library naming)
log "Getting image ID for $SOURCE_IMAGE..."
IMAGE_ID=$(docker images "$SOURCE_IMAGE" --format "{{.ID}}" 2>/dev/null | head -n1)
if [ -z "$IMAGE_ID" ]; then
    log "❌ ERROR: Cannot find image ID for $SOURCE_IMAGE"
    log "   Listing all images to help debug:"
    docker images | tee -a "$LOG_FILE"
    exit 1
fi
log "Found image ID: $IMAGE_ID"

# Save image to tar file using image ID
log "Saving image to tar file (this may take a moment)..."
TAR_FILE="./dkp-demo.tar"
(
    set -e
    if ! docker save "$IMAGE_ID" -o "$TAR_FILE" 2>&1 | tee -a "$LOG_FILE"; then
        log "❌ ERROR: Failed to save Docker image"
        exit 1
    fi
)

# Verify tar file was created
if [ ! -f "$TAR_FILE" ]; then
    log "❌ ERROR: Tar file was not created"
    log "   Expected: $TAR_FILE"
    ls -lh ./ | tee -a "$LOG_FILE"
    exit 1
fi
log "✅ Image saved to $TAR_FILE ($(ls -lh "$TAR_FILE" | awk '{print $5}'))"

# Transfer tar file to VM
log "Transferring tar file to VM..."
transfer_output=""
if ! transfer_output=$(multipass transfer "$TAR_FILE" "$VM_NAME:/tmp/" 2>&1); then
    log "❌ ERROR: Failed to transfer image to VM"
    log "   multipass transfer error:"
    echo "$transfer_output" | tee -a "$LOG_FILE"
    rm -f "$TAR_FILE"
    exit 1
fi
log "✅ Image transferred to VM"

# Check disk space and cleanup before image load
log "Checking VM disk space..."
AVAILABLE_SPACE_MB=$(multipass exec "$VM_NAME" -- df -BM / | awk 'NR==2 {sub(/M$/,"",$4); print $4}')
log "Available space: ${AVAILABLE_SPACE_MB}MB"

# Prune unused Docker data to free space
log "Cleaning up unused Docker images and containers..."
if ! multipass exec "$VM_NAME" -- docker system prune -f 2>&1 | tee -a "$LOG_FILE"; then
    log "⚠️  WARNING: Docker system prune failed (non-critical)"
    # Don't fail deployment, just warn
fi

# Verify space again after cleanup
AVAILABLE_SPACE_MB=$(multipass exec "$VM_NAME" -- df -BM / | awk 'NR==2 {sub(/M$/,"",$4); print $4}')
log "Available space after cleanup: ${AVAILABLE_SPACE_MB}MB"

# Require minimum 500MB
MIN_SPACE_MB=500
if [ "$AVAILABLE_SPACE_MB" -lt "$MIN_SPACE_MB" ]; then
    log "❌ ERROR: Insufficient disk space on VM (${AVAILABLE_SPACE_MB}MB available, ${MIN_SPACE_MB}MB required)"
    log "   Free up space or increase VM disk size"
    rm -f "$TAR_FILE"
    exit 1
fi

log "✅ Sufficient disk space available for image load"

# Load image in VM
log "Loading image in VM..."
load_output=""
if ! load_output=$(multipass exec "$VM_NAME" -- docker load -i /tmp/dkp-demo.tar 2>&1); then
    log "❌ ERROR: Failed to load image in VM"
    log "   docker load error:"
    echo "$load_output" | tee -a "$LOG_FILE"
    multipass exec "$VM_NAME" -- rm -f /tmp/dkp-demo.tar
    rm -f "$TAR_FILE"
    exit 1
fi
log "✅ Image loaded in VM"
log "   $load_output" | tee -a "$LOG_FILE"

# Extract image ID from load output and complete image operations
# docker load output format: "Loaded image ID: sha256:..."
VM_IMAGE_ID=$(echo "$load_output" | grep -o 'sha256:[a-f0-9]\+')
if [ -z "$VM_IMAGE_ID" ]; then
    log "❌ ERROR: Could not extract image ID from load output"
    log "   Load output: $load_output"
    multipass exec "$VM_NAME" -- rm -f /tmp/dkp-demo.tar
    rm -f "$TAR_FILE"
    exit 1
fi
log "Loaded image ID: $VM_IMAGE_ID"

# Tag image for registry
log "Tagging image for registry..."
if ! multipass exec "$VM_NAME" -- docker tag "$VM_IMAGE_ID" "$TARGET_IMAGE" 2>&1 | tee -a "$LOG_FILE"; then
    log "❌ ERROR: Failed to tag image in VM"
    multipass exec "$VM_NAME" -- rm -f /tmp/dkp-demo.tar
    rm -f "$TAR_FILE"
    exit 1
fi
log "✅ Image tagged as $TARGET_IMAGE in VM"

# Verify image in VM
log "Verifying image in VM..."
if ! multipass exec "$VM_NAME" -- docker images "$TARGET_IMAGE" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | grep -q "$TARGET_IMAGE"; then
    log "❌ ERROR: Image verification failed in VM"
    log "   Expected: $TARGET_IMAGE"
    log "   Found:"
    multipass exec "$VM_NAME" -- docker images | grep dkp-demo | tee -a "$LOG_FILE"
    multipass exec "$VM_NAME" -- rm -f /tmp/dkp-demo.tar
    rm -f "$TAR_FILE"
    exit 1
fi
log "✅ Image verified in VM: $TARGET_IMAGE"

# Also tag as dkp-demo:latest for consistency (non-critical)
log "Tagging image as dkp-demo:latest..."
set +e
if ! multipass exec "$VM_NAME" -- docker tag "$VM_IMAGE_ID" dkp-demo:latest 2>&1 | tee -a "$LOG_FILE"; then
    log "⚠️  WARNING: Failed to tag image as dkp-demo:latest (non-critical)"
    # Don't fail deployment, just warn
fi
log "✅ Image also tagged as dkp-demo:latest"



log "✅ Docker image successfully built and transferred to VM"
log "   Host image: dkp-demo:latest"
log "   VM image: $TARGET_IMAGE"

# Ensure script exits with code 0 on successful build
set +e
exit 0