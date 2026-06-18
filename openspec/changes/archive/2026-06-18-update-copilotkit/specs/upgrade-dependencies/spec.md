## ADDED Requirements

### Requirement: Upgrade CopilotKit Dependencies
The project packages SHALL use version 1.60.2 for `@copilotkit/*` libraries, and unused copilot-related packages SHALL be removed.

#### Scenario: Verify package versions are upgraded correctly
- **WHEN** checking dependencies in package.json
- **THEN** @copilotkit/react-core, @copilotkit/react-ui, @copilotkit/react-textarea, and @copilotkit/runtime are set to 1.60.2, and @copilotkitnext/agent is removed from dependencies.
