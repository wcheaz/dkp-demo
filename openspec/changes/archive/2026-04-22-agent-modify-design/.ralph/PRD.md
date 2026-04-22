# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

## Why

The AI agent currently can only *add* design entries via the `add_design_entry` frontend tool but has no way to *modify* existing ones. Users need the agent to update the image and/or prompt text of a previously created design entry — for example, to swap in a different placeholder image or revise the prompt after seeing the result. Without modification capability, the only option is to delete and re-add, which loses ordering and creates a poor UX.

## What Changes

- Add an `id` field (1-based, auto-incremented) to each `DesignEntry` so that existing entries can be uniquely referenced by the agent and displayed in the UI.
- Rename the two test SVGs in `tmp/` to more descriptive names (`tmp/design-alpha.svg`, `tmp/design-beta.svg`) and copy them to `public/` so they are served by Next.js. The agent will reference these by filename when choosing which image to set.
- Add a new `modify_design_entry` frontend tool (registered via `useFrontendTool` in `src/app/page.tsx`) that accepts `design_id`, an optional `image_name`, and an optional `prompt_text`, then updates the matching entry in state.
- Update `DesignComponent` to display the design `id` alongside each entry so the agent and user can see which ID to reference.

## Capabilities

### New Capabilities
- `design-entry-modify`: Frontend tool allowing the AI agent to modify the image and/or prompt text of an existing design entry by its ID.

### Modified Capabilities
- `design-entry-model`: The `DesignEntry` type gains a required `id` field (1-based integer). All code that creates `DesignEntry` objects must assign the next sequential ID.

## Impact

- **`src/lib/types.ts`** — `DesignEntry` interface gains `id: number` field.
- **`src/app/page.tsx`** — `add_design_entry` handler assigns sequential IDs; new `modify_design_entry` frontend tool registered.
- **`src/components/design-component.tsx`** — Display design ID in each card.
- **`src/components/add-design-button.tsx`** — Assign sequential ID when creating test entries.
- **`agent/src/agent.py`** — `DesignEntry` Pydantic model gains `id` field; system prompt updated to document `modify_design_entry` tool and available images.
- **`public/`** — Two new SVG files copied from `tmp/` with descriptive names.
- **`tmp/`** — SVGs renamed to `design-alpha.svg` and `design-beta.svg`.

## Specifications

design-entry-model/spec.md
## MODIFIED Requirements

### Requirement: DesignEntry type has an id field
The `DesignEntry` interface (TypeScript, `src/lib/types.ts`) and the `DesignEntry` Pydantic model (Python, `agent/src/agent.py`) SHALL include an `id: number` field.

The `id` SHALL be 1-based and assigned at creation time using the formula `max(existing entries' ids, 0) + 1`.

All code paths that create `DesignEntry` objects — `add_design_entry` handler, `AddDesignButton`, and any other constructor — SHALL assign the next sequential ID.

#### Scenario: First design entry gets id 1
- **WHEN** the first `DesignEntry` is created in an empty state
- **THEN** the entry SHALL have `id: 1`.

#### Scenario: Subsequent entries increment id
- **WHEN** a new `DesignEntry` is created and the last existing entry has `id: 3`
- **THEN** the new entry SHALL have `id: 4`.

#### Scenario: Existing designs without ids are assigned ids on access
- **WHEN** state contains design entries that lack an `id` field (e.g., from a pre-migration state)
- **THEN** the application SHALL assign sequential IDs to those entries before rendering or processing them.

### Requirement: Test SVG files have descriptive names
The test SVG files SHALL be renamed and copied as follows:
- `tmp/next.svg` → renamed to `tmp/design-alpha.svg`, copied to `public/design-alpha.svg`
- `tmp/vercel.svg` → renamed to `tmp/design-beta.svg`, copied to `public/design-beta.svg`

The default image for new design entries SHALL remain `"/next.svg"` (unchanged from current behavior).

#### Scenario: Descriptive SVG files available in public
- **WHEN** the application starts
- **THEN** `public/design-alpha.svg` and `public/design-beta.svg` SHALL exist and be servable by Next.js.

#### Scenario: Original tmp files renamed
- **WHEN** the rename is complete
- **THEN** `tmp/design-alpha.svg` and `tmp/design-beta.svg` SHALL exist. `tmp/next.svg` and `tmp/vercel.svg` SHALL NOT exist.

design-entry-modify/spec.md
## ADDED Requirements

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



## Design

## Context

The application has a design-list feature rendered via `DesignComponent`. Each entry currently contains `imageUrl` (string path) and `promptText` (string). Entries are created by:

1. `add_design_entry` — a CopilotKit frontend tool in `page.tsx` called by the AI agent after every response.
2. `AddDesignButton` — a manual button that inserts a test entry.

There is no mechanism to modify an entry after creation. The AI agent (`agent/src/agent.py`) has a Pydantic `DesignEntry` model and a `YourState.designs: List[DesignEntry]` field, but the backend tool for adding entries is commented out (state propagation is handled on the frontend via CopilotKit shared state).

The two test SVGs currently live at `tmp/next.svg` and `tmp/vercel.svg`. The app references `/next.svg` (served from `public/`) as the default placeholder image.

## Goals / Non-Goals

**Goals:**
- Allow the AI agent to modify the `imageUrl` and/or `promptText` of an existing design entry via a new `modify_design_entry` frontend tool.
- Give each design entry a stable, sequential, 1-based `id` so the agent can unambiguously target an entry.
- Provide a fixed set of named placeholder images the agent can choose from, with descriptive filenames.
- Display the design ID in the UI so users can see and reference which entry is which.

**Non-Goals:**
- Real image generation or dynamic image upload.
- Deleting design entries (out of scope for this change).
- Reordering designs.
- Persisting designs across page reloads (state remains in-memory).

## Decisions

### D1: 1-based sequential IDs assigned at creation time

Each `DesignEntry` gets an `id: number` field. The ID is computed as `max(existingIds, 0) + 1` at creation time. This is simple, stable, and unique within a session.

**Rationale:** 1-based IDs are user-friendly (displayed in the UI and referenced by the agent). They avoid the off-by-one confusion that 0-based indexing can cause for non-technical users and the LLM.

**Alternative considered:** UUIDs — rejected because they are not human-readable and add complexity for no benefit in a single-session, in-memory state.

### D2: Frontend tool pattern (useFrontendTool) for modify_design_entry

The new tool follows the same `useFrontendTool` pattern already used by `add_design_entry`. This avoids the state-propagation issues encountered when trying to use a backend agent tool (see commented-out `add_design_entry` in `agent.py`).

**Parameters:**
- `design_id` (required, number) — the 1-based ID of the entry to modify.
- `image_name` (optional, string) — filename of the image to set (e.g., `"design-alpha.svg"`).
- `prompt_text` (optional, string) — new prompt text.

At least one of `image_name` or `prompt_text` must be provided. If `image_name` is provided, the handler resolves it to the path `/design-alpha.svg` (served from `public/`).

### D3: Rename and copy test SVGs to public/

Current files:
- `tmp/next.svg` → copy to `public/design-alpha.svg`
- `tmp/vercel.svg` → copy to `public/design-beta.svg`

The original `tmp/` files are renamed to match:
- `tmp/next.svg` → `tmp/design-alpha.svg`
- `tmp/vercel.svg` → `tmp/design-beta.svg`

The existing `public/next.svg` and `public/vercel.svg` remain untouched (other parts of the app may reference them).

**Rationale:** Descriptive names make it clear to the agent and developers which image is which, reducing ambiguity in tool invocations.

### D4: Available images enumerated in agent system prompt

The agent's system prompt lists the available images by name (`design-alpha.svg`, `design-beta.svg`) so the LLM knows exactly which values it can pass to `image_name`. This prevents hallucinated filenames.

### D5: ID displayed in DesignComponent cards

Each card in `DesignComponent` shows the entry's `id` (e.g., `#1`, `#2`) in the top-left corner. This gives the user and agent a visible reference.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| IDs are not unique across sessions (reset on page reload) | Acceptable: state is in-memory and session-scoped. Documented as non-goal. |
| Agent passes an invalid `design_id` (e.g., ID that doesn't exist) | `modify_design_entry` handler returns an error string. Agent system prompt instructs the agent to check `useCopilotReadable` state before calling. |
| Agent passes an invalid `image_name` | Handler rejects unknown filenames and returns the list of valid names. |
| Neither `image_name` nor `prompt_text` provided | Handler returns an error message requiring at least one field. |
| Existing designs in state created before this change have no `id` | Migration: on first state access, assign IDs to any entries missing them (`max(existingIds, 0) + 1` for each). |

## Current Task Context

## Current Task
- 1.1 Add `id: number` field to the `DesignEntry` interface in `src/lib/types.ts`. Update `add_design_entry` handler and `AddDesignButton` in `src/app/page.tsx` to assign sequential 1-based IDs (`max(existing ids, 0) + 1`). Update the Pydantic `DesignEntry` model in `agent/src/agent.py` to include `id: int`. **Done when:** both the TypeScript and Python `DesignEntry` types have an `id` field; `add_design_entry` and `AddDesignButton` assign sequential IDs; existing app compiles with no type errors. **Verify by:** `npm run build` succeeds. **Stop and hand off if:** CopilotKit shared-state serialization fails with the new field.
