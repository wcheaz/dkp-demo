#!/bin/bash

# DEBUG LEVEL: MINIMAL (successful phase)
# This script tags the Docker image for the local microk8s registry.
# Based on deployment status: SUCCESS - minimal debug output retained.

set -euo pipefail

# Set default values
DEBUG="${DEBUG:-false}"
VM_NAME="${VM_NAME:-dkp-demo-k8s}"

# Source common error handling functions
if [ -f "scripts/deploy/common.sh" ]; then
    source "scripts/deploy/common.sh"
else
    # Fallback error handling if common.sh is not available
    LOG_FILE="${LOG_FILE:-/tmp/deploy-$(date +%Y%m%d-%H%M%S).log}"
    
    log() {
        local message="$1"
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] $message" | tee -a "$LOG_FILE"
    }
    
    log_error() {
        local message="$1"
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] ERROR: $message" | tee -a "$LOG_FILE"
    }
    
    handle_error() {
        local error_code="$1"
        local error_message="$2"
        local recovery_suggestion="$3"
        local error_type="${4:-GENERAL}"
        
        log "═══════════════════════════════════════════════════════════════════════════════"
        log "                          $error_type ERROR"
        log "═══════════════════════════════════════════════════════════════════════════════"
        log "ERROR CODE: $error_code"
        log "ERROR SUMMARY: $error_message"
        log "═══════════════════════════════════════════════════════════════════════════════"
        log "QUICK FIX: $recovery_suggestion"
        log "═══════════════════════════════════════════════════════════════════════════════"
        
        exit "$error_code"
    }
    
    handle_docker_error() {
        handle_error "$1" "$2" "$3" "DOCKER"
    }
    
    log_info() {
        local message="$1"
        # Only output if VERBOSE is explicitly set to true
        if [[ "${VERBOSE:-false}" == "true" ]]; then
            local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            echo "[$timestamp] INFO: $message" | tee -a "$LOG_FILE"
        fi
    }
    
    log_warning() {
        local message="$1"
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] WARNING: $message" | tee -a "$LOG_FILE"
    }
fi

# ===========================
# DOCKER IMAGE TAGGING FUNCTION
# ===========================

tag_image_for_local_registry() {
    log_info "Starting Docker image tagging for local registry (executing within VM)..."
    
    # Track tagging operation start time for performance measurement
    local TAGGING_START_TIME
    TAGGING_START_TIME=$(date +%s)
    log_info "⏱️  Tagging operation started at: $(date -d "@$TAGGING_START_TIME" '+%Y-%m-%d %H:%M:%S')"
    
    # Validate VM accessibility before proceeding
    log_info "Validating VM accessibility before Docker operations..."
    if ! multipass list | grep -q "$VM_NAME"; then
        log "❌ ERROR: VM '$VM_NAME' is not accessible or does not exist"
        log "   Cannot perform Docker tagging without VM access"
        log "RECOVERY STEPS:"
        log "1. Check VM status: multipass list"
        log "2. Start VM if needed: multipass start $VM_NAME"
        log "3. Verify VM is running: multipass info $VM_NAME"
        return 1
    fi
    log_info "✅ VM is accessible for Docker operations"
    
    # Validate Docker daemon availability within VM before checking images
    log_info "Validating Docker daemon availability within VM before image existence check..."
    if ! multipass exec "$VM_NAME" -- docker info >/dev/null 2>&1; then
        log "❌ ERROR: Docker daemon is not accessible within VM"
        log "   Cannot validate image existence without Docker daemon access in VM"
        log "RECOVERY STEPS:"
        log "1. Start Docker daemon in VM: multipass exec $VM_NAME -- sudo systemctl start docker"
        log "2. Check Docker daemon status in VM: multipass exec $VM_NAME -- sudo systemctl status docker"
        log "3. Verify Docker is running in VM: multipass exec $VM_NAME -- docker info"
        log "4. Restart Docker in VM if needed: multipass exec $VM_NAME -- sudo systemctl restart docker"
        return 1
    fi
    log_info "✅ Docker daemon is accessible for image validation within VM"
        
        # Comprehensive validation to ensure source image exists within VM before tagging
    log_info "Performing comprehensive validation of source image dkp-demo:latest within VM..."
    
    # Method 1: Check exact tag match within VM (primary method)
    log_info "Method 1: Checking exact tag match for dkp-demo:latest within VM..."
    local exact_match_result
    exact_match_result=$(multipass exec "$VM_NAME" -- docker images dkp-demo:latest --format "{{.Repository}}:{{.Tag}}" 2>/dev/null || echo "")
    if echo "$exact_match_result" | grep -q "dkp-demo:latest"; then
        log_info "✅ Source image found with exact tag match within VM: dkp-demo:latest"
    else
        log "⚠️  Exact tag match not found within VM - checking for alternatives..."
        
        # Method 2: Check for any dkp-demo image with any tag within VM
        log_info "Method 2: Checking for any dkp-demo image with any tag within VM..."
        local any_tag_result
        any_tag_result=$(multipass exec "$VM_NAME" -- docker images dkp-demo --format "{{.Repository}}:{{.Tag}}" 2>/dev/null || echo "")
        if [ -n "$any_tag_result" ]; then
            log_info "⚠️  Found dkp-demo images with different tags within VM:"
            echo "$any_tag_result" | tee -a "$LOG_FILE"
            log "   But dkp-demo:latest specifically is missing within VM"
            log "   This may indicate the image was built with a different tag or not loaded into VM"
        else
            log_info "⚠️  No dkp-demo images found with any tag within VM"
        fi
        
        # Method 3: Check for images containing "dkp-demo" in repository name within VM
        log_info "Method 3: Checking for images containing 'dkp-demo' in repository name within VM..."
        local similar_images
        similar_images=$(multipass exec "$VM_NAME" -- docker images --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | grep -i "dkp-demo" || echo "")
        if [ -n "$similar_images" ]; then
            log_info "⚠️  Found similar images that might be related within VM:"
            echo "$similar_images" | tee -a "$LOG_FILE"
        else
            log_info "⚠️  No images found containing 'dkp-demo' in repository name within VM"
        fi
        
        # Method 4: List all available images within VM for debugging
        log_info "Method 4: Listing all available Docker images within VM for debugging..."
        local all_images
        all_images=$(multipass exec "$VM_NAME" -- docker images --format "{{.Repository}}:{{.Tag}} {{.Size}} {{.CreatedAt}}" 2>/dev/null | head -20 || echo "")
        if [ -n "$all_images" ]; then
            log_info "Available Docker images within VM (first 20):"
            echo "$all_images" | tee -a "$LOG_FILE"
        else
            log_info "⚠️  No Docker images found in VM's Docker daemon"
        fi
        
        # Final determination: image does not exist within VM
        log "❌ ERROR: Source image dkp-demo:latest not found within VM after comprehensive validation"
        log "   Image existence validation failed using multiple methods within VM"
        log ""
        log "REQUIRED ACTION:"
        log "1. Ensure image was built on host: docker build -t dkp-demo:latest ."
        log "2. Load image into VM if not present: docker save dkp-demo:latest | multipass exec $VM_NAME -- docker load"
        log "3. Or rebuild image within VM: multipass exec $VM_NAME -- docker build -t dkp-demo:latest ."
        log ""
        log "TROUBLESHOOTING:"
        log "- Check if image was built on host: docker images | grep my-ag"
        log "- Check Docker daemon status within VM: multipass exec $VM_NAME -- docker info"
        log "- Verify image exists within VM: multipass exec $VM_NAME -- docker images | grep my-ag"
        log "- Ensure Docker build process completed successfully on host"
        
        return 1
    fi
    log_info "✅ Comprehensive validation passed: Source image dkp-demo:latest exists within VM"
    
    # Get source image details for logging from within VM
    local source_image_details
    source_image_details=$(multipass exec "$VM_NAME" -- docker images dkp-demo:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || echo "Failed to get details")
    log_info "Source image details within VM:"
    echo "$source_image_details" | tee -a "$LOG_FILE"
    
    # Define the target registry image tag
    local target_image_tag="localhost:32000/dkp-demo:latest"
    log_info "Target registry image tag: $target_image_tag"
    log_info "   This tag will be created within VM where localhost:32000 resolves to microk8s registry"
    
    # Check if target tag already exists within VM to avoid conflicts
    log_info "Checking if target tag already exists within VM..."
    if multipass exec "$VM_NAME" -- docker images "$target_image_tag" --format "{{.Repository}}:{{.Tag}}" | grep -q "$target_image_tag"; then
        log "⚠️  WARNING: Target tag $target_image_tag already exists within VM"
        log "   Removing existing tag to avoid conflicts..."
        if ! multipass exec "$VM_NAME" -- docker rmi "$target_image_tag" 2>&1 | tee -a "$LOG_FILE"; then
            log "⚠️  WARNING: Could not remove existing tag $target_image_tag within VM"
            log "   This may cause the tagging operation to fail"
            log "   You can manually remove it: multipass exec $VM_NAME -- docker rmi $target_image_tag"
        else
            log_info "✅ Existing tag $target_image_tag removed successfully within VM"
        fi
    else
        log_info "✅ Target tag $target_image_tag does not exist within VM (safe to proceed)"
    fi
    
    # Tag the image with local registry endpoint within VM
    log_info "Tagging image with local registry endpoint within VM..."
    log_info "   Command: multipass exec $VM_NAME -- docker tag dkp-demo:latest $target_image_tag"
    log_info "   This makes the image addressable by the microk8s local registry within VM"
    log_info "   Note: localhost:32000 will resolve to VM's microk8s registry (not host's)"
    
    # Pre-flight check: Verify Docker daemon is accessible within VM before tagging operation
    log_info "Performing pre-flight check: Docker daemon accessibility within VM before tagging..."
    if ! multipass exec "$VM_NAME" -- docker info >/dev/null 2>&1; then
        log "❌ ERROR: Docker daemon is not accessible within VM"
        log "   Cannot perform Docker tagging without Docker daemon access in VM"
        log "RECOVERY STEPS:"
        log "1. Start Docker daemon in VM: multipass exec $VM_NAME -- sudo systemctl start docker"
        log "2. Check Docker daemon status in VM: multipass exec $VM_NAME -- sudo systemctl status docker"
        log "3. Verify Docker is running in VM: multipass exec $VM_NAME -- docker info"
        log "4. Restart Docker in VM if needed: multipass exec $VM_NAME -- sudo systemctl restart docker"
        log "5. Check user permissions in VM: multipass exec $VM_NAME -- groups | grep docker"
        return 1
    fi
    log_info "✅ Docker daemon is accessible for tagging operation within VM"
    
    local tag_output
    local tag_exit_code
    
    # Execute the tagging command with error capture within VM
    if tag_output=$(multipass exec "$VM_NAME" -- docker tag dkp-demo:latest "$target_image_tag" 2>&1); then
        tag_exit_code=0
        log_info "✅ Docker image tagging command completed successfully within VM"
        log_info "   Tagging operation: COMPLETED (within VM)"
    else
        tag_exit_code=$?
        log "❌ ERROR: Failed to tag Docker image within VM (exit code: $tag_exit_code)"
        log "   Tagging operation: FAILED (within VM)"
        log "Error output:"
        echo "$tag_output" | tee -a "$LOG_FILE"
        
        # Analyze specific error patterns and provide targeted guidance
        log "ANALYZING IMAGE TAGGING FAILURE (within VM)..."
        
        if echo "$tag_output" | grep -q -E "(No such image|image not found|not found|does not exist)"; then
            log "ERROR TYPE: SOURCE IMAGE NOT FOUND IN VM"
            log "DIAGNOSTIC: The source image dkp-demo:latest does not exist or is not accessible within VM"
            log "RECOVERY STEPS:"
            log "1. Verify image exists within VM: multipass exec $VM_NAME -- docker images dkp-demo:latest"
            log "2. Build image if missing within VM: multipass exec $VM_NAME -- docker build -t dkp-demo:latest ."
            log "3. Load image from host to VM: docker save dkp-demo:latest | multipass exec $VM_NAME -- docker load"
            log "4. Check image name and tag within VM: multipass exec $VM_NAME -- docker images | head -20"
            
        elif echo "$tag_output" | grep -q -E "(permission denied|Permission denied|access denied|Operation not permitted)"; then
            log "ERROR TYPE: PERMISSION FAILURE WITHIN VM"
            log "DIAGNOSTIC: Insufficient permissions to tag Docker images within VM"
            log "RECOVERY STEPS:"
            log "1. Check Docker daemon access within VM: multipass exec $VM_NAME -- docker info"
            log "2. Check user permissions within VM: multipass exec $VM_NAME -- groups | grep docker"
            log "3. Run with proper Docker group permissions in VM: multipass exec $VM_NAME -- sudo usermod -aG docker \$USER"
            log "4. Or use sudo within VM: multipass exec $VM_NAME -- sudo docker tag dkp-demo:latest $target_image_tag"
            
        elif echo "$tag_output" | grep -q -E "daemon|Docker daemon|Cannot connect to Docker daemon|connection refused"; then
            log "ERROR TYPE: DOCKER DAEMON ACCESS FAILURE WITHIN VM"
            log "DIAGNOSTIC: Cannot connect to Docker daemon service within VM"
            log "RECOVERY STEPS:"
            log "1. Start Docker daemon in VM: multipass exec $VM_NAME -- sudo systemctl start docker"
            log "2. Check Docker daemon status in VM: multipass exec $VM_NAME -- sudo systemctl status docker"
            log "3. Verify Docker is running in VM: multipass exec $VM_NAME -- docker info"
            log "4. Restart Docker in VM if needed: multipass exec $VM_NAME -- sudo systemctl restart docker"
            
        elif echo "$tag_output" | grep -q -E "(repository|repository name|invalid repository|malformed repository)"; then
            log "ERROR TYPE: INVALID REPOSITORY NAME"
            log "DIAGNOSTIC: The target registry tag contains invalid characters or format"
            log "RECOVERY STEPS:"
            log "1. Verify target tag format: $target_image_tag"
            log "2. Ensure registry endpoint is correct: localhost:32000"
            log "3. Check for invalid characters in image name"
            log "4. Valid format: [registry_host:port/][namespace/]repository[:tag]"
            
        elif echo "$tag_output" | grep -q -E "(tag|tag name|invalid tag|tag already exists|conflict)"; then
            log "ERROR TYPE: TAG CONFLICT OR INVALID TAG WITHIN VM"
            log "DIAGNOSTIC: Tag already exists within VM, conflicts with existing tag, or tag format is invalid"
            log "RECOVERY STEPS:"
            log "1. Remove existing tag within VM: multipass exec $VM_NAME -- docker rmi $target_image_tag"
            log "2. Verify tag format: localhost:32000/dkp-demo:latest"
            log "3. Use force flag if needed: multipass exec $VM_NAME -- docker tag -f dkp-demo:latest $target_image_tag"
            log "4. Check existing tags within VM: multipass exec $VM_NAME -- docker images | grep localhost:32000"
            
        elif echo "$tag_output" | grep -q -E "(filesystem|storage|disk space|no space|out of space|layer|overlay)"; then
            log "ERROR TYPE: FILESYSTEM OR STORAGE FAILURE WITHIN VM"
            log "DIAGNOSTIC: Docker storage or filesystem issues within VM preventing image tagging"
            log "RECOVERY STEPS:"
            log "1. Check disk space within VM: multipass exec $VM_NAME -- df -h"
            log "2. Check Docker storage within VM: multipass exec $VM_NAME -- docker info | grep -A 10 'Storage Driver'"
            log "3. Clean up Docker resources within VM: multipass exec $VM_NAME -- docker system prune -f"
            log "4. Check filesystem permissions within VM: multipass exec $VM_NAME -- ls -la /var/lib/docker"
            
        elif echo "$tag_output" | grep -q -E "(memory|OOM|out of memory|resource|allocation|cannot allocate)"; then
            log "ERROR TYPE: MEMORY OR RESOURCE CONSTRAINT FAILURE WITHIN VM"
            log "DIAGNOSTIC: VM lacks sufficient memory or resources for Docker operations"
            log "RECOVERY STEPS:"
            log "1. Check memory usage within VM: multipass exec $VM_NAME -- free -h"
            log "2. Check system resources within VM: multipass exec $VM_NAME -- top -bn1 | head -20"
            log "3. Free up memory within VM: multipass exec $VM_NAME -- sudo apt autoremove -y && sudo apt clean"
            log "4. Close unnecessary applications or increase VM memory"
            
        else
            log "ERROR TYPE: UNKNOWN IMAGE TAGGING FAILURE WITHIN VM"
            log "DIAGNOSTIC: Image tagging failed with unknown error pattern within VM"
            log "ERROR DETAILS:"
            log "Tag command exit code: $tag_exit_code"
            log "Source image: dkp-demo:latest"
            log "Target tag: $target_image_tag"
            log "Tag command output:"
            echo "$tag_output" | tee -a "$LOG_FILE"
            log "RECOVERY STEPS:"
            log "1. Verify Docker is working within VM: multipass exec $VM_NAME -- docker --version && multipass exec $VM_NAME -- docker info"
            log "2. Check source image within VM: multipass exec $VM_NAME -- docker images dkp-demo:latest"
            log "3. Try manual tagging within VM: multipass exec $VM_NAME -- docker tag dkp-demo:latest $target_image_tag"
            log "4. Check Docker daemon logs within VM: multipass exec $VM_NAME -- sudo journalctl -u docker.service -n 20"
        fi
        
        return 1
    fi
    
    # Verify the tagging was successful within VM (mandatory verification)
    log_info "Verifying tagged image exists after successful tagging..."
    if multipass exec "$VM_NAME" -- docker images "$target_image_tag" --format "{{.Repository}}:{{.Tag}}" | grep -q "$target_image_tag"; then
        log_info "✅ Image tagging verification successful within VM"
        log_info "   Target tag $target_image_tag exists and is accessible within VM"
        
        # Get tagged image details for logging from within VM
        local tagged_image_details
        tagged_image_details=$(multipass exec "$VM_NAME" -- docker images "$target_image_tag" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || echo "Failed to get details")
        log_info "Tagged image details within VM:"
        echo "$tagged_image_details" | tee -a "$LOG_FILE"
        
        # Verify that both images (source and tagged) exist and have the same image ID within VM
        local source_image_id
        local tagged_image_id
        
        source_image_id=$(multipass exec "$VM_NAME" -- docker images dkp-demo:latest --format "{{.ID}}" 2>/dev/null || echo "unknown")
        tagged_image_id=$(multipass exec "$VM_NAME" -- docker images "$target_image_tag" --format "{{.ID}}" 2>/dev/null || echo "unknown")
        
        if [ "$source_image_id" = "$tagged_image_id" ] && [ "$source_image_id" != "unknown" ]; then
            log_info "✅ Image ID verification successful - both images reference the same underlying image within VM"
            log_info "   Source image ID: $source_image_id"
            log_info "   Tagged image ID: $tagged_image_id"
        else
            log "⚠️  WARNING: Image ID verification failed or IDs are different within VM"
            log_info "   Source image ID: $source_image_id"
            log_info "   Tagged image ID: $tagged_image_id"
            log_info "   This may indicate the tagging operation didn't work as expected within VM"
        fi
        
    else
        log "❌ ERROR: Image tagging verification failed within VM"
        log "   Target tag $target_image_tag does not exist after tagging operation within VM"
        log "   This indicates the tagging command may have silently failed within VM"
        
        # Check if the source image still exists within VM
        if multipass exec "$VM_NAME" -- docker images dkp-demo:latest --format "{{.Repository}}:{{.Tag}}" | grep -q "dkp-demo:latest"; then
            log "✅ Source image still exists within VM: dkp-demo:latest"
        else
            log "❌ CRITICAL: Source image dkp-demo:latest is missing after failed tagging within VM"
            log "   This may indicate a serious issue with the Docker daemon within VM"
            log "   RECOVERY: You may need to rebuild the image within VM: multipass exec $VM_NAME -- docker build -t dkp-demo:latest ."
        fi
        
        return 1
    fi
    
    log_info "✅ Docker image tagging for local registry completed successfully within VM"
    log_info "   Image tagged as: $target_image_tag"
    log_info "   Ready for: Push to microk8s local registry at localhost:32000 (within VM)"
    log_info "   Next step: Use the registry push function to push this tagged image from within VM"
    
    # Calculate and log tagging operation duration
    local TAGGING_END_TIME
    TAGGING_END_TIME=$(date +%s)
    local TAGGING_DURATION
    TAGGING_DURATION=$((TAGGING_END_TIME - TAGGING_START_TIME))
    log_info "⏱️  Tagging operation completed at: $(date -d "@$TAGGING_END_TIME" '+%Y-%m-%d %H:%M:%S')"
    log_info "⏱️  Total tagging operation duration: $TAGGING_DURATION seconds"
    
    return 0
}

# ===========================
# MAIN TAGGING EXECUTION
# ===========================

log_info "Starting Docker image tagging for local registry..."
log_info "Using comprehensive tagging function with validation and error handling..."

# Use the comprehensive image tagging function with full validation and error handling
if ! tag_image_for_local_registry; then
    handle_error 1 "Failed to tag Docker image for local registry" \
        "Check logs above for detailed error analysis and recovery steps." "DOCKER"
fi

log_info "✅ Docker image tagging for registry completed with comprehensive validation"
log_info "   Image successfully tagged as: localhost:32000/dkp-demo:latest"