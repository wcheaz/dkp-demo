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
