#!/bin/bash

# Script to set up Kubernetes secrets for dkp-demo
# This script reads environment variables and creates Kubernetes secrets
# 
# Usage: ./setup-secrets.sh [--apply]
#   --apply    Apply the generated secrets to Kubernetes cluster
#
# Environment Variables:
#   OPENAI_API_KEY          (Required) Your OpenAI API key
#   OPENAI_BASE_URL         (Optional) OpenAI base URL, default: https://api.openai.com/v1
#   OPENAI_MODEL            (Optional) OpenAI model, default: gpt-4
#   LLM_MAX_TOKENS          (Optional) Max tokens, default: 4096
#   LLM_CONTEXT_WINDOW      (Optional) Context window, default: 8192
#   EMBEDDING_MODEL         (Optional) Embedding model, default: text-embedding-ada-002
#   LOGFIRE_TOKEN           (Optional) Logfire token
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Cannot read .env file
#   3 - Required environment variable not set
#   4 - Cannot encode empty string to base64
#   5 - Base64 encoding failed
#   6 - Base64 encoding returned empty result
#   7 - kubectl command not found
#   8 - OPENAI_API_KEY is required but not set
#   9 - Cannot create output directory
#   10 - Cannot write to output directory
#   11 - Failed to write secrets file
#   12 - Generated YAML file is invalid
#   13 - Failed to apply secrets to Kubernetes cluster

set -e

# Error handling function with recovery suggestions
handle_error() {
    local exit_code=$1
    local error_message=$2
    local recovery_suggestion=$3
    
    echo "=================================================================="
    echo "❌ ERROR: $error_message"
    echo "=================================================================="
    echo "ERROR TYPE: KUBERNETES SECRETS SETUP FAILURE"
    echo "DIAGNOSTIC: $error_message"
    echo "COMMON CAUSES:"
    echo "  - Missing required environment variables"
    echo "  - File permission issues"
    echo "  - Kubernetes cluster not accessible"
    echo "RECOVERY:"
    echo "  $recovery_suggestion"
    echo "=================================================================="
    exit $exit_code
}

# Configuration
SECRETS_FILE="k8s/secrets.yaml.template"
OUTPUT_FILE="k8s/secrets.yaml"
ENV_FILE=".env"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to encode a string to base64 with error handling
encode_base64() {
    local input="$1"
    
    if [ -z "$input" ]; then
        handle_error 4 "Cannot encode empty string to base64" \
            "1. Ensure all required environment variables are set\n" \
            "2. Check that values are not empty or null\n" \
            "3. Verify your .env file contains valid values"
    fi
    
    local result
    result=$(echo -n "$input" | base64 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        handle_error 5 "Base64 encoding failed for value" \
            "1. Verify the input value is valid text\n" \
            "2. Check for special characters that might need escaping\n" \
            "3. Ensure base64 command is available: which base64"
    fi
    
    if [ -z "$result" ]; then
        handle_error 6 "Base64 encoding returned empty result" \
            "1. Verify the input value is not corrupted\n" \
            "2. Check base64 command is working properly\n" \
            "3. Try encoding manually: echo -n '$input' | base64"
    fi
    
    echo "$result"
}

# Function to get environment variable value with fallback and error handling
get_env_value() {
    local var_name="$1"
    local default_value="$2"
    
    # Check if variable is set in environment
    if [ -n "${!var_name}" ]; then
        echo "${!var_name}"
        return 0
    fi
    
    # Try to get value from .env file
    if [ -f "$ENV_FILE" ]; then
        if [ ! -r "$ENV_FILE" ]; then
            handle_error 2 "Cannot read .env file" \
                "1. Check file permissions: ls -la $ENV_FILE\n" \
                "2. Ensure file is readable: chmod 644 $ENV_FILE\n" \
                "3. Verify file exists and is not corrupted"
        fi
        
        local value=$(grep "^$var_name=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'" 2>/dev/null || echo "")
        if [ -n "$value" ]; then
            echo "$value"
            return 0
        else
            log "WARNING: Variable '$var_name' not found in $ENV_FILE, using default value"
        fi
    else
        log "INFO: No .env file found, checking environment variables"
    fi
    
    # Return default value if available
    if [ -n "$default_value" ]; then
        echo "$default_value"
        return 0
    fi
    
    # No value found and no default
    handle_error 3 "Required environment variable '$var_name' is not set" \
        "1. Set the variable in your environment: export $var_name=<value>\n" \
        "2. Or create a .env file with: echo '$var_name=<value>' >> $ENV_FILE\n" \
        "3. Or provide it when running: $var_name=<value> $0"
}

log "Setting up Kubernetes secrets..."

# Check if multipass is available (since we use multipass exec for kubectl operations)
if ! command -v multipass >/dev/null 2>&1; then
    handle_error 7 "multipass command not found" \
        "1. Install multipass: follow Multipass installation guide\n" \
        "2. Ensure multipass is in your PATH: export PATH=\$PATH:/usr/local/bin\n" \
        "3. Verify Multipass VM is accessible: multipass list"
fi

# Get environment variable values with error handling
log "Reading environment variables..."
OPENAI_API_KEY=$(get_env_value "OPENAI_API_KEY" "")
OPENAI_BASE_URL=$(get_env_value "OPENAI_BASE_URL" "https://api.openai.com/v1")
OPENAI_MODEL=$(get_env_value "OPENAI_MODEL" "gpt-4")
LLM_MAX_TOKENS=$(get_env_value "LLM_MAX_TOKENS" "4096")
LLM_CONTEXT_WINDOW=$(get_env_value "LLM_CONTEXT_WINDOW" "8192")
EMBEDDING_MODEL=$(get_env_value "EMBEDDING_MODEL" "text-embedding-ada-002")
LOGFIRE_TOKEN=$(get_env_value "LOGFIRE_TOKEN" "")

# Validate required values
if [ -z "$OPENAI_API_KEY" ]; then
    handle_error 8 "OPENAI_API_KEY is required but not set" \
        "1. Get your API key from https://platform.openai.com/api-keys\n" \
        "2. Set it in your environment: export OPENAI_API_KEY=your_key_here\n" \
        "3. Or add it to your .env file: echo 'OPENAI_API_KEY=your_key_here' >> .env"
fi

# Encode values to base64 with error handling
log "Encoding values to base64..."
OPENAI_API_KEY_BASE64=$(encode_base64 "$OPENAI_API_KEY")
OPENAI_BASE_URL_BASE64=$(encode_base64 "$OPENAI_BASE_URL")
OPENAI_MODEL_BASE64=$(encode_base64 "$OPENAI_MODEL")
EMBEDDING_MODEL_BASE64=$(encode_base64 "$EMBEDDING_MODEL")
LOGFIRE_TOKEN_BASE64=$(encode_base64 "$LOGFIRE_TOKEN")

# Check if output directory is writable
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR" || handle_error 9 "Cannot create output directory $OUTPUT_DIR" \
        "1. Check directory permissions: ls -la $(dirname $OUTPUT_DIR)\n" \
        "2. Ensure you have write access: chmod 755 $(dirname $OUTPUT_DIR)\n" \
        "3. Or run with appropriate user permissions"
fi

if [ ! -w "$OUTPUT_DIR" ]; then
    handle_error 10 "Cannot write to output directory $OUTPUT_DIR" \
        "1. Check directory permissions: ls -la $OUTPUT_DIR\n" \
        "2. Ensure you have write access: chmod 755 $OUTPUT_DIR\n" \
        "3. Or run with appropriate user permissions"
fi

# Generate the secrets file with error handling
log "Generating Kubernetes secrets file..."
if ! cat > "$OUTPUT_FILE" << EOF
apiVersion: v1
kind: Secret
metadata:
  name: dkp-demo-secrets
  namespace: default
  labels:
    app: dkp-demo
type: Opaque
data:
  # Base64 encoded values for sensitive environment variables
  OPENAI_API_KEY: $OPENAI_API_KEY_BASE64
  OPENAI_BASE_URL: $OPENAI_BASE_URL_BASE64
  OPENAI_MODEL: $OPENAI_MODEL_BASE64
  EMBEDDING_MODEL: $EMBEDDING_MODEL_BASE64
  LOGFIRE_TOKEN: $LOGFIRE_TOKEN_BASE64
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: dkp-demo-config
  namespace: default
  labels:
    app: dkp-demo
data:
  # Non-sensitive configuration values
  LLM_MAX_TOKENS: "$LLM_MAX_TOKENS"
  LLM_CONTEXT_WINDOW: "$LLM_CONTEXT_WINDOW"
EOF
then
    handle_error 11 "Failed to write secrets file to $OUTPUT_FILE" \
        "1. Check disk space: df -h\n" \
        "2. Verify file permissions: ls -la $OUTPUT_DIR\n" \
        "3. Ensure directory is writable: chmod 755 $OUTPUT_DIR\n" \
        "4. Check if file is locked by another process"
fi

# Validate generated YAML file with Kubernetes API server
# Skip validation if we're generating on host (validation happens in deploy_scripts/setup-k8s-secrets.sh)
if [ -z "${SKIP_VALIDATION:-}" ]; then
    log "Validating generated secrets file against Kubernetes API server..."
    if ! multipass exec "${VM_NAME:-{{PROJECT_NAME}}-k8s}" -- microk8s kubectl apply --dry-run=server -f - < "$OUTPUT_FILE" 2>/dev/null; then
        handle_error 12 "Secrets YAML validation failed against Kubernetes API server" \
            "1. Check generated file for syntax errors: cat $OUTPUT_FILE\n" \
            "2. Verify all base64 values are properly encoded\n" \
            "3. Ensure no special characters broke YAML format\n" \
            "4. Check Kubernetes cluster connectivity: multipass exec ${VM_NAME:-{{PROJECT_NAME}}-k8s} -- microk8s kubectl cluster-info\n" \
            "5. Verify you have necessary permissions: multipass exec ${VM_NAME:-{{PROJECT_NAME}}-k8s} -- microk8s kubectl auth can-i create secret\n" \
            "6. Try regenerating file after fixing environment variables"
    fi
else
    log "Skipping validation (will be done in deployment script)"
fi

log "✅ Kubernetes secrets file generated successfully: $OUTPUT_FILE"

# Optional: Apply the secrets to Kubernetes if requested
if [ "$1" = "--apply" ]; then
    log "Applying secrets to Kubernetes cluster..."
        if ! multipass exec "${VM_NAME:-{{PROJECT_NAME}}-k8s}" -- microk8s kubectl apply -f - < "$OUTPUT_FILE" 2>/dev/null; then
        handle_error 13 "Failed to apply secrets to Kubernetes cluster" \
            "1. Check Kubernetes cluster connectivity: multipass exec ${VM_NAME:-{{PROJECT_NAME}}-k8s} -- microk8s kubectl cluster-info\n" \
            "2. Verify kubectl configuration: multipass exec ${VM_NAME:-{{PROJECT_NAME}}-k8s} -- microk8s kubectl config current-context\n" \
            "3. Ensure you have necessary permissions: multipass exec ${VM_NAME:-{{PROJECT_NAME}}-k8s} -- microk8s kubectl auth can-i create secret\n" \
            "4. Check for existing secrets: multipass exec ${VM_NAME:-{{PROJECT_NAME}}-k8s} -- microk8s kubectl get secret {{PROJECT_NAME}}-secrets\n" \
            "5. Ensure secrets file passes validation: multipass exec ${VM_NAME:-{{PROJECT_NAME}}-k8s} -- microk8s kubectl apply --dry-run=server -f $OUTPUT_FILE"
    fi
    log "✅ Secrets applied to Kubernetes cluster successfully"
fi
