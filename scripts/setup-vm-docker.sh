#!/bin/bash

# setup-vm-docker.sh - Script to install and configure Docker in the multipass VM
# This script should be run on the host machine, not inside the VM

set -euo pipefail

# Configuration
# PROJECT_NAME: Replace with your project name before running deployment scripts.
# This VM name is used for multipass VM creation and access.
# Override with: VM_NAME=my-vm ./scripts/setup-vm-docker.sh
VM_NAME="${VM_NAME:-dkp-demo-k8s}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to execute command in VM
vm_exec() {
    multipass exec "$VM_NAME" -- "$@"
}

# Function to execute command in VM with error handling
vm_exec_safe() {
    if ! vm_exec "$@"; then
        log_error "Command failed in VM: $*"
        return 1
    fi
}

# Check prerequisites
log "Checking prerequisites..."

if ! command_exists multipass; then
    log_error "multipass is not installed"
    log "Please install multipass from: https://multipass.run/"
    exit 1
fi

log_success "multipass is installed"

# Check if VM exists
if ! multipass list | grep -q "$VM_NAME"; then
    log_error "VM '$VM_NAME' not found"
    log "Available VMs:"
    multipass list
    exit 1
fi

log_success "VM '$VM_NAME' exists"

# Check if VM is running
VM_STATE=$(multipass info "$VM_NAME" | grep "State:" | awk '{print $2}')
if [ "$VM_STATE" != "Running" ]; then
    log_error "VM '$VM_NAME' is not running (state: $VM_STATE)"
    log "Starting VM..."
    multipass start "$VM_NAME"
    sleep 10
fi

log_success "VM '$VM_NAME' is running"

# Check if Docker is already installed
log "Checking if Docker is already installed..."

if vm_exec docker --version >/dev/null 2>&1; then
    DOCKER_VERSION=$(vm_exec docker --version)
    log_success "Docker is already installed: $DOCKER_VERSION"
    log "Checking Docker daemon status..."

    if vm_exec docker info >/dev/null 2>&1; then
        log_success "Docker daemon is running and accessible"
        exit 0
    else
        log_warning "Docker is installed but daemon is not running"
        log "Starting Docker daemon..."

        if vm_exec sudo systemctl start docker; then
            log_success "Docker daemon started"
            vm_exec sudo systemctl enable docker
            log_success "Docker daemon enabled to start on boot"

            if vm_exec docker info >/dev/null 2>&1; then
                log_success "Docker daemon is now accessible"
                exit 0
            else
                log_error "Docker daemon still not accessible after starting"
                exit 1
            fi
        else
            log_error "Failed to start Docker daemon"
            exit 1
        fi
    fi
fi

log "Docker is not installed, proceeding with installation..."

# Install Docker in VM
log "Updating package index in VM..."
vm_exec sudo apt-get update

log "Installing Docker in VM..."
vm_exec sudo apt-get install -y docker.io

log "Enabling Docker to start on boot..."
vm_exec sudo systemctl enable docker

log "Starting Docker daemon..."
vm_exec sudo systemctl start docker

# Add user to docker group
log "Adding ubuntu user to docker group..."
vm_exec sudo usermod -aG docker ubuntu

# Verify installation
log "Verifying Docker installation..."

if vm_exec docker --version >/dev/null 2>&1; then
    DOCKER_VERSION=$(vm_exec docker --version)
    log_success "Docker installed: $DOCKER_VERSION"
else
    log_error "Docker installation verification failed"
    exit 1
fi

if vm_exec docker info >/dev/null 2>&1; then
    log_success "Docker daemon is running and accessible"
else
    log_error "Docker daemon is not running or not accessible"
    exit 1
fi

# Test Docker functionality
log "Testing Docker functionality..."

if vm_exec docker ps >/dev/null 2>&1; then
    log_success "Docker commands work without sudo"
else
    log_warning "Docker commands require sudo, this may be due to group membership not being activated"
    log "Testing with sudo..."

    if vm_exec sudo docker ps >/dev/null 2>&1; then
        log_success "Docker commands work with sudo"
        log_warning "You may need to log out and log back in for group membership to take effect"
    else
        log_error "Docker commands do not work even with sudo"
        exit 1
    fi
fi

log ""
log "🎉 Docker setup completed successfully!"
log ""
log "Docker version: $DOCKER_VERSION"
log "Docker daemon: Running and accessible"
log "User permissions: Configured (ubuntu user in docker group)"
log ""
log "You can now run deployment with:"
log "  ./deploy-all.sh"
