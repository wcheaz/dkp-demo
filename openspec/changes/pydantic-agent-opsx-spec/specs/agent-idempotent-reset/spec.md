## ADDED Requirements

### Requirement: Reset task unchecks all task checkboxes
The final task in the spec SHALL rewrite the change's `tasks.md` file, replacing every occurrence of `- [x]` with `- [ ]`.

#### Scenario: All checked tasks become unchecked
- **WHEN** the reset task is executed
- **THEN** every `- [x]` in `tasks.md` SHALL be replaced with `- [ ]`, enabling the spec to be re-applied from a clean state

#### Scenario: Reset task is last in task list
- **WHEN** the `tasks.md` file is generated
- **THEN** the reset task SHALL be the final checkbox item in the file

### Requirement: Reset task is idempotent
The reset task SHALL be safe to run on an already-reset `tasks.md` (where all checkboxes are `- [ ]`).

#### Scenario: Running on already-unchecked file
- **WHEN** the reset task is executed on a file where all checkboxes are already `- [ ]`
- **THEN** the file SHALL remain unchanged
