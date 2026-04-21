# Tasks: agent-modify-design

## 1. Data Model and Test Assets

- [ ] 1.1 Add `id: number` field to the `DesignEntry` interface in `src/lib/types.ts`. Update `add_design_entry` handler and `AddDesignButton` in `src/app/page.tsx` to assign sequential 1-based IDs (`max(existing ids, 0) + 1`). Update the Pydantic `DesignEntry` model in `agent/src/agent.py` to include `id: int`. **Done when:** both the TypeScript and Python `DesignEntry` types have an `id` field; `add_design_entry` and `AddDesignButton` assign sequential IDs; existing app compiles with no type errors. **Verify by:** `npm run build` succeeds. **Stop and hand off if:** CopilotKit shared-state serialization fails with the new field.

- [ ] 1.2 Rename `tmp/next.svg` to `tmp/design-alpha.svg` and `tmp/vercel.svg` to `tmp/design-beta.svg`. Copy both to `public/design-alpha.svg` and `public/design-beta.svg`. **Done when:** `public/design-alpha.svg` and `public/design-beta.svg` exist; `tmp/next.svg` and `tmp/vercel.svg` no longer exist; `tmp/design-alpha.svg` and `tmp/design-beta.svg` exist. **Verify by:** `ls tmp/design-alpha.svg tmp/design-beta.svg public/design-alpha.svg public/design-beta.svg` and confirming the old filenames are gone.

## 2. Frontend Tool — modify_design_entry

- [ ] 2.1 Add `modify_design_entry` frontend tool in `src/app/page.tsx` (via `useFrontendTool`). Parameters: `design_id` (required number), `image_name` (optional string), `prompt_text` (optional string). Handler finds the entry by `id`, updates the provided fields, and returns a confirmation or error. Allowed image names: `"design-alpha.svg"`, `"design-beta.svg"`. Handler resolves `image_name` to `"/" + image_name`. **Done when:** `modify_design_entry` tool is registered; calling it with a valid `design_id` and at least one optional field updates the matching entry in state; calling with invalid `design_id` returns an error string; calling with invalid `image_name` returns an error string; calling without `image_name` or `prompt_text` returns an error string. **Verify by:** `npm run build` succeeds. **Stop and hand off if:** `useFrontendTool` does not support optional parameters in the CopilotKit version used.

- [ ] 2.2 Add ID-backfill logic: before rendering designs or processing `modify_design_entry`, ensure every entry in `state.designs` has an `id`. If any entry lacks an `id`, assign sequential IDs starting from `1`. **Done when:** entries created before this change (without `id`) receive IDs on first access. **Verify by:** manually loading state with an `id`-less entry and confirming it gets an ID assigned.

## 3. UI and Agent Integration

- [ ] 3.1 Update `DesignComponent` (`src/components/design-component.tsx`) to display each design entry's `id` as a visible label (e.g., `#1`) in the card. **Done when:** each rendered card shows the entry's ID. **Verify by:** `npm run build` succeeds and the component renders IDs visibly.

- [ ] 3.2 Update the agent system prompt in `agent/src/agent.py` to document the `modify_design_entry` tool, its parameters, and the list of available images (`design-alpha.svg`, `design-beta.svg`). **Done when:** the system prompt string contains `"modify_design_entry"`, `"design-alpha.svg"`, and `"design-beta.svg"`. **Verify by:** reading `agent/src/agent.py` and confirming the system prompt includes the tool documentation.

## 4. Verification

- [ ] 4.1 Run full build to verify no type errors or compilation failures across all changed files. **Done when:** `npm run build` completes with exit code 0. **Stop and hand off if:** build errors persist after two fix attempts.
