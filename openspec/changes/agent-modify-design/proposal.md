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
