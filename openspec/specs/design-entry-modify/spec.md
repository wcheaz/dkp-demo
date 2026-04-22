## Purpose

Provides the ability for the AI agent to modify existing design entries (image and/or prompt text) via a frontend tool.

## Requirements

### Requirement: modify_design_entry frontend tool
The system SHALL provide a `modify_design_entry` frontend tool registered via `useFrontendTool` in `src/app/page.tsx` that allows the AI agent to modify the image and/or prompt text of an existing design entry.

The tool SHALL accept these parameters:
- `design_id` (required, number): the 1-based ID of the design entry to modify.
- `image_name` (optional, string): the filename of the image to set (e.g., `"design-alpha.svg"` or `"design-beta.svg"`).
- `prompt_text` (optional, string): the new prompt text.

The tool SHALL require that at least one of `image_name` or `prompt_text` is provided. If neither is provided, the handler SHALL return an error string and make no state changes.

The tool SHALL resolve a valid `image_name` to the path `/<image_name>` (served from the `public/` directory).

#### Scenario: Modify image only
- **WHEN** the agent calls `modify_design_entry` with `design_id: 1` and `image_name: "design-beta.svg"`
- **THEN** the design entry with `id === 1` SHALL have its `imageUrl` updated to `"/design-beta.svg"` and its `promptText` SHALL remain unchanged.

#### Scenario: Modify prompt text only
- **WHEN** the agent calls `modify_design_entry` with `design_id: 2` and `prompt_text: "Updated prompt"`
- **THEN** the design entry with `id === 2` SHALL have its `promptText` updated to `"Updated prompt"` and its `imageUrl` SHALL remain unchanged.

#### Scenario: Modify both image and prompt text
- **WHEN** the agent calls `modify_design_entry` with `design_id: 1`, `image_name: "design-alpha.svg"`, and `prompt_text: "New text"`
- **THEN** the design entry with `id === 1` SHALL have both `imageUrl` and `promptText` updated.

#### Scenario: Design ID not found
- **WHEN** the agent calls `modify_design_entry` with a `design_id` that does not match any existing entry
- **THEN** the handler SHALL return an error string containing the invalid ID and the list of valid IDs.

#### Scenario: Invalid image name
- **WHEN** the agent calls `modify_design_entry` with an `image_name` that is not in the allowed set (`"design-alpha.svg"`, `"design-beta.svg"`)
- **THEN** the handler SHALL return an error string listing the valid image names.

#### Scenario: Neither image_name nor prompt_text provided
- **WHEN** the agent calls `modify_design_entry` with only `design_id` and neither `image_name` nor `prompt_text`
- **THEN** the handler SHALL return an error string stating that at least one of `image_name` or `prompt_text` must be provided.

### Requirement: Available images documented in agent system prompt
The agent's system prompt SHALL list the available image filenames (`design-alpha.svg`, `design-beta.svg`) so the LLM can pass valid values to `modify_design_entry`.

#### Scenario: Agent knows available images
- **WHEN** the agent reads its system prompt
- **THEN** the system prompt SHALL contain the strings `"design-alpha.svg"` and `"design-beta.svg"` and instructions to use only those values for `image_name`.

### Requirement: Design ID displayed in UI
Each design card rendered by `DesignComponent` SHALL display the entry's `id` as a visible label (e.g., `#1`).

#### Scenario: ID visible on design card
- **WHEN** the design list contains an entry with `id: 3`
- **THEN** the rendered card for that entry SHALL show the text `#3`.
