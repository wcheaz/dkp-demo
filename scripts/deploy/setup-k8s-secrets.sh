#!/bin/bash

# DEBUG LEVEL: FULL (problematic phase)

# Set strict error handling
set -euo pipefail

# Source common error handling functions
source "scripts/deploy/common.sh"

# Initialize log file
setup_log_file



# Enable debug output if DEBUG=all is set
if [ "${DEBUG:-}" = "all" ]; then
    log_info "DEBUG: Verbose debug output enabled for Kubernetes secrets setup"
    set -x
fi

# 5.4 Create Kubernetes secrets for sensitive environment variables
log_info "Starting Kubernetes secrets setup..."

# Check if k8s directory exists
if [ ! -d "k8s" ]; then
    log_error "k8s directory not found"
    log_structured_error "KUBERNETES MANIFESTS DIRECTORY MISSING" \
        "The k8s directory containing Kubernetes manifests was not found in the current working directory" \
        "Project structure incorrect, k8s directory was deleted or moved, script running from wrong directory" \
        "1. Verify you're in the correct project directory: $(pwd)\n2. Check if k8s directory exists: ls -la\n3. If missing, recreate the k8s directory with required manifests\n4. Ensure you haven't accidentally deleted or moved the k8s directory"
    exit 1
fi
log_info "k8s directory found: $(pwd)/k8s/"

# Check if setup-secrets.sh script exists
if [ ! -f "k8s/setup-secrets.sh" ]; then
    log_error "setup-secrets.sh script not found"
    log_structured_error "KUBERNETES SECRETS SETUP SCRIPT MISSING" \
        "The setup-secrets.sh script required for generating Kubernetes secrets was not found in the k8s directory" \
        "Script file was deleted or moved, incomplete project checkout, script running from wrong directory" \
        "1. Verify setup-secrets.sh exists in k8s directory: ls -la k8s/\n2. If missing, restore the script from your project repository\n3. Ensure you're in the correct project directory: $(pwd)\n4. Check if you have the complete project source code"
    exit 1
fi
log_info "setup-secrets.sh script found: $(pwd)/k8s/setup-secrets.sh"

# Check if .env file exists
if [ ! -f ".env" ]; then
    log_warning ".env file not found in current directory"
    log_info "Using environment variables from shell environment"
fi

# Set up environment variables for secrets creation
log_info "Setting up environment variables for secrets creation..."

# Read environment variables from .env file if it exists
if [ -f ".env" ]; then
    log_info "Loading environment variables from .env file..."
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ ! "$line" =~ ^#.*$ ]] && [[ -n "$line" ]]; then
            # Export the variable
            export "$line"
            log_info "Set environment variable: ${line%%=*}"
        fi
    done < .env
fi

# Verify required environment variables are set
REQUIRED_VARS=("OPENAI_API_KEY" "OPENAI_BASE_URL" "OPENAI_MODEL" "EMBEDDING_MODEL")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    log_error "Missing required environment variables:"
    for missing_var in "${MISSING_VARS[@]}"; do
        log_error "  - $missing_var"
    done
    log_structured_error "REQUIRED ENVIRONMENT VARIABLES MISSING" \
        "One or more required environment variables are not set, which are needed for Kubernetes secrets configuration" \
        "Environment variables not exported, .env file missing or incomplete, variables not properly configured in deployment environment" \
        "1. Set missing variables in your shell: export OPENAI_API_KEY=your_key_here\n2. Or create/update .env file with required variables\n3. Variables needed: OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, EMBEDDING_MODEL\n4. Get API keys from: https://platform.openai.com/api-keys"
    exit 1
fi
log_info "All required environment variables are set"

# Run the secrets setup script to generate the YAML file
log_info "Running secrets setup script to generate YAML file..."
if ! SKIP_VALIDATION=1 bash k8s/setup-secrets.sh 2>&1 | tee -a "$LOG_FILE"; then
    log_error "Failed to generate Kubernetes secrets YAML file"
    log_structured_error "KUBERNETES SECRETS GENERATION FAILED" \
        "The setup-secrets.sh script failed to generate a valid Kubernetes secrets YAML file" \
        "Invalid environment variable values, base64 encoding errors, file permission issues, or script syntax errors" \
        "1. Review the script output above for specific error messages\n2. Verify all environment variables are set correctly: echo \$OPENAI_API_KEY\n3. Check file permissions in k8s directory: ls -la k8s/\n4. Test environment variables manually: bash k8s/setup-secrets.sh\n5. Fix any reported issues and retry"
    exit 1
fi
log_info "Kubernetes secrets YAML file generated successfully: k8s/secrets.yaml"

# Copy the secrets file to the VM for validation and application
log_info "Copying secrets file to VM for Kubernetes operations..."
if ! multipass transfer k8s/secrets.yaml "${VM_NAME:-dkp-demo-k8s}:/home/ubuntu/secrets.yaml" 2>&1 | tee -a "$LOG_FILE"; then
    log_error "Failed to copy secrets file to VM"
    log_structured_error "FILE TRANSFER FAILED" \
        "The secrets.yaml file could not be transferred to the Multipass VM" \
        "VM not running, file permission issues, network connectivity problems, or insufficient disk space on VM" \
        "1. Verify VM is running: multipass list\n2. Check file permissions: ls -la k8s/secrets.yaml\n3. Verify network connectivity to VM\n4. Check available disk space on VM: multipass exec ${VM_NAME:-dkp-demo-k8s} -- df -h"
    exit 1
fi
log_info "Secrets file copied to VM successfully"

# Validate the generated secrets file using Kubernetes API server
log_info "Validating secrets YAML against Kubernetes API server..."
VALIDATION_OUTPUT=$(multipass exec "${VM_NAME:-dkp-demo-k8s}" -- microk8s kubectl apply --dry-run=server -f /home/ubuntu/secrets.yaml 2>&1)
VALIDATION_EXIT_CODE=${PIPESTATUS[0]}
echo "$VALIDATION_OUTPUT" | tee -a "$LOG_FILE"
if [ $VALIDATION_EXIT_CODE -ne 0 ]; then
    log_error "Secrets YAML validation failed against Kubernetes API server"
    log_structured_error "KUBERNETES SECRETS VALIDATION FAILURE" \
        "Generated secrets YAML file is invalid or incompatible with Kubernetes API server" \
        "YAML syntax errors in generated secrets file, Invalid base64 encoding of secret values, Missing required fields or incorrect Kubernetes API version, Kubernetes cluster connectivity issues" \
        "1. Check the generated file for errors: cat k8s/secrets.yaml\n2. Verify Kubernetes cluster connectivity: multipass exec ${VM_NAME:-dkp-demo-k8s} -- microk8s kubectl cluster-info\n3. Ensure you have necessary permissions: multipass exec ${VM_NAME:-dkp-demo-k8s} -- microk8s kubectl auth can-i create secret\n4. Fix any environment variable issues and regenerate the file"
    exit 1
fi
log_info "Secrets YAML validation passed"

# Apply the validated secrets to Kubernetes
log_info "Applying secrets to Kubernetes cluster..."
APPLY_OUTPUT=$(multipass exec "${VM_NAME:-dkp-demo-k8s}" -- microk8s kubectl apply -f /home/ubuntu/secrets.yaml 2>&1)
APPLY_EXIT_CODE=${PIPESTATUS[0]}
echo "$APPLY_OUTPUT" | tee -a "$LOG_FILE"
if [ $APPLY_EXIT_CODE -ne 0 ]; then
    log_error "Failed to apply secrets to Kubernetes cluster"
    log_structured_error "KUBERNETES SECRETS APPLICATION FAILED" \
        "The kubectl apply command failed to apply the validated secrets YAML to the Kubernetes cluster" \
        "Kubernetes cluster connectivity issues, insufficient permissions, invalid cluster configuration, or conflicting existing resources" \
        "1. Check Kubernetes cluster connectivity: multipass exec ${VM_NAME:-dkp-demo-k8s} -- microk8s kubectl cluster-info\n2. Verify your kubectl context: multipass exec ${VM_NAME:-dkp-demo-k8s} -- microk8s kubectl config current-context\n3. Check permissions: multipass exec ${VM_NAME:-dkp-demo-k8s} -- microk8s kubectl auth can-i create secret\n4. Check for existing secrets: multipass exec ${VM_NAME:-dkp-demo-k8s} -- microk8s kubectl get secret dkp-demo-secrets\n5. If secrets exist, delete first: multipass exec ${VM_NAME:-dkp-demo-k8s} -- microk8s kubectl delete secret dkp-demo-secrets\n6. Ensure Kubernetes cluster is running and accessible"
    exit 1
fi

# Secrets setup completed successfully

log_info "Kubernetes secrets setup completed successfully"