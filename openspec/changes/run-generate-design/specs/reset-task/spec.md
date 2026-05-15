## ADDED Requirements

### Requirement: Final task unchecks all task checkboxes
The last task in the spec SHALL rewrite `tasks.md`, replacing every `- [x]` with `- [ ]`.

#### Scenario: All tasks unchecked after run
- **WHEN** the reset task is executed
- **THEN** every `- [x]` in `tasks.md` SHALL become `- [ ]`

### Requirement: Reset is idempotent
The reset task SHALL be safe to run on an already-reset file.

#### Scenario: Already-unchecked file
- **WHEN** all checkboxes are already `- [ ]`
- **THEN** the file SHALL remain unchanged
