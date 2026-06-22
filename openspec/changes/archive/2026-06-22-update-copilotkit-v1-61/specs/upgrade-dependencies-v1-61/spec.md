## ADDED Requirements

### Requirement: Upgrade CopilotKit Dependencies to 1.61.0
The project packages SHALL use version 1.61.0 for `@copilotkit/*` libraries.

#### Scenario: Verify package versions are upgraded correctly
- **WHEN** checking dependencies in package.json
- **THEN** @copilotkit/react-core, @copilotkit/react-ui, @copilotkit/react-textarea, and @copilotkit/runtime are set to 1.61.0 in package.json.
