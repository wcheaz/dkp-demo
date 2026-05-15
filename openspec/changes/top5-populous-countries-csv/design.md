## Context

This change introduces a standalone Python script that generates a CSV file containing demographic and linguistic data for the top 5 most populous countries. The project uses Python 3.12+ with strict typing. The script will live in the `test/` directory per project conventions.

The current state has no existing CSV generation capability. This is a greenfield addition with no dependencies on existing project modules.

## Goals / Non-Goals

**Goals:**

- Generate a well-formatted CSV with title, description, and country data
- Support bolded country names using `**name**` Markdown-style syntax within the CSV
- Include localized "Hello World" translations for each of the 5 countries
- Be fully idempotent — repeated runs produce identical output, overwriting previous files
- Include a reset/cleanup step to allow re-running the entire workflow from scratch

**Non-Goals:**

- Dynamic data fetching from external APIs or databases
- Support for more than 5 countries (fixed dataset)
- Localization beyond the primary language per country
- GUI or web-based interface

## Decisions

### 1. Static embedded dataset over external API

**Decision**: Hard-code country data (name, population, greeting) directly in the script.

**Rationale**: The top 5 most populous countries are well-known and stable. Using an external API would add network dependencies, latency, and failure modes for a dataset that changes infrequently. This keeps the script self-contained and deterministic.

**Alternatives considered**: REST API (e.g., World Bank), CSV download from a data source — rejected due to unnecessary complexity.

### 2. Markdown-style bold syntax in CSV

**Decision**: Use `**Country Name**` syntax within CSV cell values to indicate bold.

**Rationale**: CSV has no native formatting. Markdown-style bold markers are a widely understood convention and can be post-processed by rendering tools. The proposal explicitly requests bolded country names.

### 3. CSV structure with title/description header rows

**Decision**: Use the first two rows for title and description respectively, followed by a blank row, then column headers, then data rows.

**Rationale**: Keeps the file human-readable while maintaining a clear visual separation between metadata and data. This matches the user's request for "a title and a description at the top."

### 4. File overwrite strategy for idempotency

**Decision**: The script uses `w` mode (overwrite) when opening the output file, ensuring every run produces the same result regardless of prior state.

**Rationale**: Append mode would duplicate data on re-runs. Overwrite guarantees idempotent output.

### 5. Reset task as a separate cleanup step

**Decision**: Include a final task in `tasks.md` that deletes the generated CSV and resets task checkboxes.

**Rationale**: Allows the entire workflow to be re-run from scratch. This fulfills the user's requirement for reentrancy.

## Risks / Trade-offs

- **[Stale data]** → Population figures are static snapshots; acceptable for a demo. No mitigation needed.
- **[CSV rendering]** → Markdown bold syntax won't render in all CSV viewers; this is by design since the spec explicitly requests bold via text markers.
- **[Encoding]** → Non-ASCII characters in greetings (e.g., Hindi "नमस्ते दुनिया") require UTF-8 encoding. Mitigation: explicit `encoding='utf-8'` in file operations.
