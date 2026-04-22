## ADDED Requirements

### Requirement: Multipass VM creation with fixed specifications
The system SHALL provide a script (`scripts/deploy/setup-vm.sh`) that creates a Multipass VM named `dkp-demo-k8s` with exactly 4 CPUs, 7.7 GB RAM, and 19.3 GB disk running Ubuntu, matching the reference architecture from the sister project.

#### Scenario: Fresh VM creation on a host with Multipass installed
- **WHEN** the user runs `scripts/deploy/setup-vm.sh` and no VM named `dkp-demo-k8s` exists
- **THEN** the script SHALL create a Multipass VM with 4 CPUs, 7.7 GB RAM, and 19.3 GB disk
- **AND** the script SHALL wait until the VM reaches "Running" state before proceeding

#### Scenario: VM already exists
- **WHEN** the user runs `scripts/deploy/setup-vm.sh` and a VM named `dkp-demo-k8s` already exists
- **THEN** the script SHALL skip creation and log that the VM already exists
- **AND** the script SHALL proceed to the configuration steps

### Requirement: Docker installation inside the VM
The system SHALL install Docker inside the Multipass VM so that image builds and registry pushes can be executed from within the VM.

#### Scenario: Docker installed and accessible
- **WHEN** the VM provisioning script completes
- **THEN** Docker SHALL be accessible inside the VM via `multipass exec dkp-demo-k8s -- docker info`
- **AND** the Docker daemon SHALL be configured with the MicroK8s registry (`localhost:32000`) as an insecure registry in `/etc/docker/daemon.json`

### Requirement: MicroK8s installation and add-on enablement
The system SHALL install MicroK8s inside the VM via snap and enable the following add-ons: `dns`, `ingress`, `registry`, and `storage`.

#### Scenario: MicroK8s running with all required add-ons
- **WHEN** the VM provisioning script completes
- **THEN** `multipass exec dkp-demo-k8s -- microk8s status` SHALL report MicroK8s is running
- **AND** the following add-ons SHALL be enabled: `dns`, `ingress`, `registry`, `storage`
- **AND** the registry SHALL be accessible at `localhost:32000` inside the VM

#### Scenario: MicroK8s add-on enablement is idempotent
- **WHEN** the VM provisioning script is run a second time and add-ons are already enabled
- **THEN** the script SHALL NOT fail and SHALL log that add-ons are already enabled

### Requirement: VM teardown script
The system SHALL provide a script (`scripts/deploy/destroy-vm.sh`) that stops and deletes the Multipass VM.

#### Scenario: Teardown of existing VM
- **WHEN** the user runs `scripts/deploy/destroy-vm.sh` and the VM `dkp-demo-k8s` exists
- **THEN** the script SHALL stop and delete the VM
- **AND** the script SHALL confirm deletion succeeded

#### Scenario: Teardown when VM does not exist
- **WHEN** the user runs `scripts/deploy/destroy-vm.sh` and the VM `dkp-demo-k8s` does not exist
- **THEN** the script SHALL log that no VM was found and exit successfully

### Requirement: Script exit codes reflect success or failure
All VM provisioning and teardown scripts SHALL exit with code 0 on success and non-zero on failure, enabling use in automated pipelines.

#### Scenario: Provisioning fails due to insufficient host resources
- **WHEN** the host does not have enough resources to create the VM
- **THEN** the script SHALL exit with a non-zero code and print a diagnostic message explaining the resource shortfall
