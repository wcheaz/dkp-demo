#!/bin/bash

# Cleanup Resources Script
# Removes non-running Kubernetes pods and unused Docker images
# Usage: ./scripts/deploy/cleanup-resources.sh

# Change to project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT"

# Source common error handling functions
if [ -f "scripts/deploy/common.sh" ]; then
    source "scripts/deploy/common.sh"
else
    echo "ERROR: scripts/deploy/common.sh not found. Cannot continue with cleanup."
    exit 1
fi

# Error handling functions
log_warning() {
    echo "WARNING: $1" | tee -a "$LOG_FILE" 2>/dev/null || echo "WARNING: $1"
}

handle_critical_error() {
    echo "ERROR: $1" | tee -a "$LOG_FILE" 2>/dev/null || echo "ERROR: $1"
    exit 1
}

# Default values
VM_NAME="${VM_NAME:-dkp-demo-k8s}"

# Main cleanup function
cleanup_resources() {
    log_info "🧹 CLEANUP: Removing previous non-running pods and unused resources..."
    
    local pods_cleaned=0
    local docker_images_cleaned=0
    
    # Check if VM is accessible (critical failure)
    if ! multipass info "${VM_NAME}" >/dev/null 2>&1; then
        handle_critical_error "VM '${VM_NAME}' is not accessible. Cannot continue with cleanup."
    fi
    
    # Check if Docker daemon is accessible (critical failure)
    if ! docker info >/dev/null 2>&1; then
        handle_critical_error "Docker daemon is not accessible. Cannot continue with cleanup."
    fi

    # Clean up orphaned "modified" deployment and pods
    log_info "🧹 Cleaning up orphaned 'modified' deployments and pods..."
    
    # Check for any deployment named "dkp-demo-modified"
    local modified_deployment=$(multipass exec "${VM_NAME}" -- microk8s kubectl get deployment dkp-demo-modified -o name 2>/dev/null || echo "")
    
    if [ -n "$modified_deployment" ]; then
        log_info "🧹 Found 'modified' deployment: $modified_deployment"
        
        # Delete the 'modified' deployment (this will also delete its pods)
        log_info "🧹 Deleting 'modified' deployment..."
        if ! multipass exec "${VM_NAME}" -- microk8s kubectl delete deployment dkp-demo-modified --ignore-not-found=true 2>&1 | tee -a "$LOG_FILE"; then
            log_warning "Failed to delete 'modified' deployment. Continuing with cleanup."
        else
            log_info "✅ Deleted 'modified' deployment and its pods"
        fi
    else
        log_info "✅ No 'modified' deployment found"
    fi
    
    # Clean up Kubernetes pods that are not running
    log_info "🧹 Cleaning up non-running Kubernetes pods..."
    
    # Get all pods that are not in Running state
    local non_running_pods=$(multipass exec "${VM_NAME}" -- microk8s kubectl get pods -l app=dkp-demo -o jsonpath='{.items[?(@.status.phase!="Running")].metadata.name}' 2>/dev/null)
    local pod_command_result=$?
    
    if [ $pod_command_result -ne 0 ]; then
        log_warning "Failed to get pod status from Kubernetes. Skipping pod cleanup."
        non_running_pods=""
    fi
    
    if [ -n "$non_running_pods" ]; then
        log_info "🧹 Found non-running pods: $non_running_pods"
        
        # Delete evicted pods
        local evicted_pods=$(multipass exec "${VM_NAME}" -- microk8s kubectl get pods -l app=dkp-demo --field-selector=status.phase==Failed -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
        if [ -n "$evicted_pods" ]; then
            log_info "🧹 Deleting evicted pods..."
            if ! multipass exec "${VM_NAME}" -- microk8s kubectl delete pods -l app=dkp-demo --field-selector=status.phase==Failed --ignore-not-found=true 2>&1 | tee -a "$LOG_FILE"; then
                log_warning "Failed to delete some evicted pods. Continuing with cleanup."
            fi
            local evicted_count=$(echo "$evicted_pods" | wc -w)
            pods_cleaned=$((pods_cleaned + evicted_count))
            log_info "✅ Deleted $evicted_count evicted pods"
        fi
        
        # Delete pods with ImagePullBackOff or ErrImagePull
        local pull_error_pods=$(multipass exec "${VM_NAME}" -- microk8s kubectl get pods -l app=dkp-demo -o json 2>/dev/null | grep -o '"reason":"ImagePullBackOff"\|"reason":"ErrImagePull"' | wc -l)
        if [ "$pull_error_pods" -gt 0 ]; then
            log_info "🧹 Deleting pods with image pull errors..."
            if ! multipass exec "${VM_NAME}" -- microk8s kubectl delete pods -l app=dkp-demo --field-selector=status.phase!=Running --ignore-not-found=true 2>&1 | tee -a "$LOG_FILE"; then
                log_warning "Failed to delete some pods with image pull errors. Continuing with cleanup."
            fi
            log_info "✅ Deleted pods with image pull errors"
        fi
        
        # Delete CrashLoopBackOff pods
        local crash_loop_pods=$(multipass exec "${VM_NAME}" -- microk8s kubectl get pods -l app=dkp-demo -o json 2>/dev/null | grep -o '"reason":"CrashLoopBackOff"' | wc -l)
        if [ "$crash_loop_pods" -gt 0 ]; then
            log_info "🧹 Deleting CrashLoopBackOff pods..."
            if ! multipass exec "${VM_NAME}" -- microk8s kubectl delete pods -l app=dkp-demo --field-selector=status.phase!=Running --ignore-not-found=true 2>&1 | tee -a "$LOG_FILE"; then
                log_warning "Failed to delete some CrashLoopBackOff pods. Continuing with cleanup."
            fi
            log_info "✅ Deleted CrashLoopBackOff pods"
        fi
        
        # Delete any remaining non-running pods
        local remaining_non_running=$(multipass exec "${VM_NAME}" -- microk8s kubectl get pods -l app=dkp-demo --field-selector=status.phase!=Running -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
        if [ -n "$remaining_non_running" ]; then
            local remaining_count=$(echo "$remaining_non_running" | wc -w)
            log_info "🧹 Deleting remaining non-running pods..."
            if ! multipass exec "${VM_NAME}" -- microk8s kubectl delete pods -l app=dkp-demo --field-selector=status.phase!=Running --ignore-not-found=true 2>&1 | tee -a "$LOG_FILE"; then
                log_warning "Failed to delete some remaining non-running pods. Continuing with cleanup."
            fi
            pods_cleaned=$((pods_cleaned + remaining_count))
            log_info "✅ Deleted $remaining_count remaining non-running pods"
        fi
        
    else
        log_info "✅ No non-running pods found - all pods are healthy"
    fi
    
    # Stop and remove containers with label app=dkp-demo before image deletion
    log_info "🧹 Stopping containers with label app=dkp-demo..."
    
    # Get running containers with the app label
    local running_containers=$(docker ps -q -f "label=app=dkp-demo" 2>/dev/null || echo "")
    if [ -n "$running_containers" ]; then
        local running_count=$(echo "$running_containers" | wc -l)
        log_info "🧹 Stopping $running_count running containers..."
        if ! docker stop $running_containers 2>&1 | tee -a "$LOG_FILE"; then
            log_warning "Failed to stop some running containers. Continuing with cleanup."
        fi
        log_info "✅ Stopped $running_count running containers"
    fi
    
    log_info "🧹 Removing stopped containers with label app=dkp-demo..."
    
    # Get all containers (including stopped) with the app label
    local all_containers=$(docker ps -a -q -f "label=app=dkp-demo" 2>/dev/null || echo "")
    if [ -n "$all_containers" ]; then
        local all_count=$(echo "$all_containers" | wc -l)
        log_info "🧹 Removing $all_count stopped containers..."
        if ! docker rm $all_containers 2>&1 | tee -a "$LOG_FILE"; then
            log_warning "Failed to remove some stopped containers. Continuing with cleanup."
        fi
        log_info "✅ Removed $all_count stopped containers"
    fi
    
    # Clean up unused Docker images
    log_info "🧹 Cleaning up unused Docker images..."
    
    # Remove dangling images
    local dangling_images=$(docker images -f "dangling=true" -q 2>/dev/null || echo "")
    if [ -n "$dangling_images" ]; then
        local dangling_count=$(echo "$dangling_images" | wc -l)
        log_info "🧹 Removing $dangling_count dangling Docker images..."
        if ! docker rmi $dangling_images 2>&1 | tee -a "$LOG_FILE"; then
            log_warning "Failed to remove some dangling Docker images. Continuing with cleanup."
        else
            docker_images_cleaned=$((docker_images_cleaned + dangling_count))
            log_info "✅ Removed dangling Docker images"
        fi
    fi
    
    # Remove old dkp-demo images (keep only latest)
    local old_app_images=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "^dkp-demo:" | grep -v ":latest$" | grep -v "localhost:32000/" 2>/dev/null || echo "")
    if [ -n "$old_app_images" ]; then
        local old_count=$(echo "$old_app_images" | wc -l)
        log_info "🧹 Removing $old_count old dkp-demo images..."
        if ! docker rmi $old_app_images 2>&1 | tee -a "$LOG_FILE"; then
            log_warning "Failed to remove some old dkp-demo images. Continuing with cleanup."
        else
            docker_images_cleaned=$((docker_images_cleaned + old_count))
            log_info "✅ Removed old dkp-demo images"
        fi
    fi
    
    # Clean up Docker build cache
    log_info "🧹 Cleaning up Docker build cache..."
    if ! docker builder prune -f 2>&1 | tee -a "$LOG_FILE"; then
        log_warning "Failed to clean up Docker build cache. Continuing with cleanup."
    else
        log_info "✅ Cleaned up Docker build cache"
    fi
    
    # Cleanup summary
    log_info "🧹 CLEANUP SUMMARY:"
    log_info "  • Pods cleaned: $pods_cleaned"
    log_info "  • Docker images cleaned: $docker_images_cleaned"
    
    if [ $pods_cleaned -eq 0 ] && [ $docker_images_cleaned -eq 0 ]; then
        log_info "  • Status: No cleanup needed (environment already clean)"
    else
        log_info "  • Status: Cleanup completed successfully"
    fi
    
    log_info "✅ PRE-DEPLOYMENT CLEANUP COMPLETED"
}

# Main execution
log_info "🚀 STARTING RESOURCE CLEANUP"
cleanup_resources
log_info "🎉 CLEANUP COMPLETED SUCCESSFULLY!"
