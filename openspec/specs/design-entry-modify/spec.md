## Purpose

Provides the ability for the AI agent to modify existing design entries (image and/or prompt text) via a frontend tool. Supports both static preset images via `image_name` and dynamically-served images via `image_url`.

## Requirements

### Requirement: modify_design_entry frontend tool
The system SHALL provide a `modify_design_entry` frontend tool registered via `useFrontendTool` in `src/app/page.tsx` that allows the AI agent to modify the image and/or prompt text of an existing design entry.

The tool SHALL accept these parameters:
- `design_id` (required, number): the 1-based ID of the design entry to modify.
- `image_name` (optional, string): the filename of the image to set (e.g., `"design-alpha.svg"` or `"design-beta.svg"`). Validated against the `ALLOWED_IMAGES` whitelist.
- `image_url` (optional, string): a full URL or path to set directly as the `imageUrl` (e.g., `/api/serve-image/test-image-1234567890.png`). Bypasses the `ALLOWED_IMAGES` whitelist.
- `prompt_text` (optional, string): the new prompt text.

The tool SHALL require that at least one of `image_name`, `image_url`, or `prompt_text` is provided. If none are provided, the handler SHALL return an error string and make no state changes.

When both `image_name` and `image_url` are provided, `image_url` SHALL take precedence.

The tool SHALL resolve a valid `image_name` to the path `/<image_name>` (served from the `public/` directory).

The tool SHALL set `image_url` directly as the `imageUrl` value without validation against `ALLOWED_IMAGES`.

#### Scenario: Modify image using image_url parameter
- **WHEN** the agent calls `modify_design_entry` with `design_id: 1` and `image_url: "/api/serve-image/test-image-1234567890.png"`
- **THEN** the design entry with `id === 1` SHALL have its `imageUrl` updated to `"/api/serve-image/test-image-1234567890.png"` and its `promptText` SHALL remain unchanged.

#### Scenario: image_url takes precedence over image_name
- **WHEN** the agent calls `modify_design_entry` with `design_id: 1`, `image_name: "design-alpha.svg"`, and `image_url: "/api/serve-image/test-image-1234567890.png"`
- **THEN** the design entry with `id === 1` SHALL have its `imageUrl` set to `"/api/serve-image/test-image-1234567890.png"` (the `image_url` value).

#### Scenario: Modify image only with image_name
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
- **WHEN** the agent calls `modify_design_entry` with an `image_name` that is not in the allowed set (`"design-alpha.svg"`, `"design-beta.svg"`) and no `image_url` is provided
- **THEN** the handler SHALL return an error string listing the valid image names.

#### Scenario: Neither image_name, image_url, nor prompt_text provided
- **WHEN** the agent calls `modify_design_entry` with only `design_id` and none of `image_name`, `image_url`, or `prompt_text`
- **THEN** the handler SHALL return an error string stating that at least one of `image_name`, `image_url`, or `prompt_text` must be provided.

#### Scenario: Only image_url provided with no image_name
- **WHEN** the agent calls `modify_design_entry` with `design_id: 1` and `image_url: "/api/serve-image/test-image-1234567890.png"` and no `image_name`
- **THEN** the handler SHALL NOT validate against `ALLOWED_IMAGES` and SHALL set `imageUrl` to the provided `image_url` value.

### Requirement: Available images documented in agent system prompt
The agent's system prompt SHALL list the available image filenames (`design-alpha.svg`, `design-beta.svg`) so the LLM can pass valid values to `modify_design_entry`. The system prompt SHALL also document the `image_url` parameter and explain when to use it (for dynamically downloaded images) versus `image_name` (for static preset images).

#### Scenario: Agent knows available images and image_url parameter
- **WHEN** the agent reads its system prompt
- **THEN** the system prompt SHALL contain the strings `"design-alpha.svg"` and `"design-beta.svg"`
- **AND** the system prompt SHALL contain the string `"image_url"`
- **AND** the system prompt SHALL contain instructions to use `image_url` for dynamically downloaded images.

### Requirement: Design ID displayed in UI
Each design card rendered by `DesignComponent` SHALL display the entry's `id` as a visible label (e.g., `#1`).

#### Scenario: ID visible on design card
- **WHEN** the design list contains an entry with `id: 3`
- **THEN** the rendered card for that entry SHALL show the text `#3`.

### Requirement: reset_design tool documented alongside modify_design_entry

The agent's system prompt section that documents frontend tools SHALL include `reset_design` documentation in the same block as `modify_design_entry`, so the agent is aware of both modification and reset capabilities when deciding which tool to use.

#### Scenario: System prompt lists both modify and reset tools

- **GIVEN** the agent system prompt in `agent/src/agent.py`
- **WHEN** the system prompt is read
- **THEN** the section documenting `modify_design_entry` and the section documenting `reset_design` SHALL both be present
- **AND** they SHALL appear in the same tool documentation block (not in separate disconnected sections)
