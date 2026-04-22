#!/bin/bash

# Enable strict error handling
set -euo pipefail

# Common error handling functions for deployment scripts
# This file should be sourced by all deployment scripts
#
# VERBOSE Flag Documentation:
# - VERBOSE=false (default): Shows only ERROR and WARN level messages
# - VERBOSE=true: Shows all log levels including INFO and DEBUG
# - Usage: VERBOSE=true ./deploy-all.sh
# - When to use: Troubleshooting deployment failures, debugging new configurations
# - Impact: Generates 5-10x more log output, minimal performance impact

# Global error codes
ERROR_GENERAL=1
ERROR_DEPENDENCY=200
ERROR_REGISTRY=201
ERROR_DOCKER=202
ERROR_KUBERNETES=203
ERROR_NETWORK=204
ERROR_VALIDATION=205

# Global variables
# PROJECT_NAME: Replace with your project name before running deployment scripts
# This VM name is used for multipass VM creation and access
# Default is generic - override with: VM_NAME=my-vm ./deploy-to-k8s.sh
#
# Note: The deployment scripts are designed for multipass + microk8s environment.
# If using a different Kubernetes distribution (minikube, k3d, cloud provider),
# you will need to adapt the scripts to use the appropriate kubectl commands
# and remove multipass-specific commands.
VM_NAME="${VM_NAME:-dkp-demo-k8s}"
LOG_FILE="${LOG_FILE:-/tmp/deploy-$(date +%Y%m%d-%H%M%S).log}"
HEALTH_CHECK_PATH="${HEALTH_CHECK_PATH:-/api/health}"

# Common logging function
log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

# Info level logging function
log_info() {
    local message="$1"
    # Only output if VERBOSE is explicitly set to true
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] INFO: $message" | tee -a "$LOG_FILE"
    fi
}

# Warning level logging function
log_warning() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] WARNING: $message" | tee -a "$LOG_FILE"
}

# Error level logging function
log_error() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ERROR: $message" | tee -a "$LOG_FILE"
}

# Structured error logging function with detailed fields
log_structured_error() {
    local error_type="$1"
    local diagnostic="$2"
    local common_causes="$3"
    local recovery="$4"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] ══════════════════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
    echo "[$timestamp]                          STRUCTURED ERROR" | tee -a "$LOG_FILE"
    echo "[$timestamp] ══════════════════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
    echo "[$timestamp] ERROR TYPE: $error_type" | tee -a "$LOG_FILE"
    echo "[$timestamp] DIAGNOSTIC: $diagnostic" | tee -a "$LOG_FILE"
    echo "[$timestamp] COMMON CAUSES: $common_causes" | tee -a "$LOG_FILE"
    echo "[$timestamp] RECOVERY: $recovery" | tee -a "$LOG_FILE"
    echo "[$timestamp] ══════════════════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
}

# Common error handler
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

# Dependency validation error handler
handle_dependency_error() {
    handle_error "$ERROR_DEPENDENCY" "$1" "$2" "DEPENDENCY VALIDATION"
}

# Registry error handler
handle_registry_error() {
    handle_error "$ERROR_REGISTRY" "$1" "$2" "REGISTRY"
}

# Docker error handler
handle_docker_error() {
    handle_error "$ERROR_DOCKER" "$1" "$2" "DOCKER"
}

# Kubernetes error handler
handle_kubernetes_error() {
    handle_error "$ERROR_KUBERNETES" "$1" "$2" "KUBERNETES"
}

# Network error handler
handle_network_error() {
    handle_error "$ERROR_NETWORK" "$1" "$2" "NETWORK"
}

# Validation error handler
handle_validation_error() {
    handle_error "$ERROR_VALIDATION" "$1" "$2" "VALIDATION"
}

# Setup log file function - creates timestamped log file and directory if needed
setup_log_file() {
    local log_dir="${LOG_DIR:-/tmp}"
    local timestamp=$(date '+%Y%m%d-%H%M%S')
    
    # Ensure log directory exists
    mkdir -p "$log_dir"
    
    # Set global log file path if not already set
    if [[ -z "${LOG_FILE:-}" ]]; then
        LOG_FILE="$log_dir/deploy-$timestamp.log"
    fi
    
    # Create log file with header
    echo "=============================================" > "$LOG_FILE"
    echo "  DEPLOYMENT LOG - $timestamp" >> "$LOG_FILE"
    echo "=============================================" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "Log file created: $LOG_FILE"
    echo "Deployment started at: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    log_info "Log file initialized: $LOG_FILE"
}

# Cleanup old logs function - rotates and compresses logs, keeping only last 10
cleanup_old_logs() {
    local log_dir="${LOG_DIR:-/tmp}"
    local max_size_mb=100
    local max_logs=10
    
    log_info "Starting log cleanup process"
    
    # Check if log directory exists
    if [[ ! -d "$log_dir" ]]; then
        log_warning "Log directory does not exist: $log_dir"
        return 0
    fi
    
    # Find all deployment log files
    local log_files=()
    while IFS= read -r -d '' file; do
        log_files+=("$file")
    done < <(find "$log_dir" -name "deploy-*.log" -type f -print0 2>/dev/null)
    
    if [[ ${#log_files[@]} -eq 0 ]]; then
        log_info "No deployment log files found for cleanup"
        return 0
    fi
    
    log_info "Found ${#log_files[@]} deployment log files to check"
    
    # Check and rotate large log files
    for log_file in "${log_files[@]}"; do
        if [[ -f "$log_file" ]]; then
            local file_size_mb
            file_size_mb=$(du -m "$log_file" | cut -f1 2>/dev/null || echo "0")
            
            if [[ "$file_size_mb" -gt "$max_size_mb" ]]; then
                log_warning "Log file exceeds ${max_size_mb}MB (${file_size_mb}MB): $log_file"
                
                # Rotate the log file
                local timestamp=$(date '+%Y%m%d-%H%M%S')
                local rotated_file="${log_file}.rotated-${timestamp}"
                
                if mv "$log_file" "$rotated_file" 2>/dev/null; then
                    log_info "Log file rotated to: $rotated_file"
                    
                    # Compress the rotated file
                    if gzip "$rotated_file" 2>/dev/null; then
                        log_info "Log file compressed: ${rotated_file}.gz"
                    else
                        log_warning "Failed to compress rotated log file: $rotated_file"
                    fi
                else
                    log_warning "Failed to rotate log file: $log_file"
                fi
            fi
        fi
    done
    
    # Find all log files including rotated and compressed ones
    local all_log_files=()
    while IFS= read -r -d '' file; do
        all_log_files+=("$file")
    done < <(find "$log_dir" \( -name "deploy-*.log" -o -name "deploy-*.log.rotated-*" \) -type f -print0 2>/dev/null)
    
    # Sort files by modification time (newest first)
    IFS=$'\n' sorted_files=($(sort -r <<<"${all_log_files[*]}"))
    unset IFS
    
    # Remove excess log files, keeping only the most recent max_logs
    local total_files=${#sorted_files[@]}
    if [[ "$total_files" -gt "$max_logs" ]]; then
        local files_to_remove=$((total_files - max_logs))
        log_info "Removing $files_to_remove old log files (keeping last $max_logs)"
        
        for ((i=max_logs; i<total_files; i++)); do
            local file_to_remove="${sorted_files[$i]}"
            if [[ -f "$file_to_remove" ]]; then
                if rm "$file_to_remove" 2>/dev/null; then
                    log_info "Removed old log file: $file_to_remove"
                else
                    log_warning "Failed to remove old log file: $file_to_remove"
                fi
            fi
        done
    fi
    
    log_info "Log cleanup process completed"
}

# Verify command function - executes command and checks exit code
# Usage: verify_command <command_description> <command_to_execute> [error_type] [recovery_suggestion]
verify_command() {
    local command_description="$1"
    shift
    local command_to_execute="$1"
    shift
    local error_type="${1:-GENERAL}"
    shift
    local recovery_suggestion="${1:-Check the command syntax and ensure all dependencies are available}"
    
    log_info "Executing: $command_description"
    
    # Execute the command and capture both output and exit code
    local output
    if ! output=$(${command_to_execute} 2>&1); then
        local exit_code=$?
        log_error "Command failed: $command_description"
        log_error "Exit code: $exit_code"
        log_error "Command output: $output"
        
        # Use structured error logging for detailed failure information
        log_structured_error "$error_type" "Command '$command_description' failed with exit code $exit_code" "Command syntax error, missing dependencies, permission issues, or system resource constraints" "$recovery_suggestion"
        
        # Exit with the original command's exit code, or use error code 1 if it's 0
        if [[ $exit_code -eq 0 ]]; then
            exit 1
        else
            exit $exit_code
        fi
    fi
    
    # Log success and output if verbose mode is enabled
    log_info "Command succeeded: $command_description"
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        echo "Command output: $output" | tee -a "$LOG_FILE"
    fi
    
    return 0
}