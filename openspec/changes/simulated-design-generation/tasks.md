## 1. Data Model

- [x] 1.1 Add `status` field to `DesignEntry` in `src/lib/types.ts` and `agent/src/agent.py`. TypeScript: `status?: "processing" | "complete"` (optional, defaults via omitted). Python: `status: str = "complete"`. Remove or update `TEMPORARY` comments to `DEMO-ONLY` on `DesignEntry` and `designs` field in `agent/src/agent.py`. Verify by: `npx tsc --noEmit && cd agent && python -m ruff check . && python -m mypy .`.

## 2. Static Assets

- [ ] 2.1 Create four roof-type schematic SVGs in `public/`: `design-gable.svg`, `design-hip.svg`, `design-mono.svg`, `design-flat.svg`. Each SVG MUST contain a visually distinct truss/roof schematic appropriate to its type. Verify by: confirming all four files exist in `public/` and are valid SVG (contain `<svg>` root element).

## 3. Frontend Tool Replacement

- [ ] 3.1 Replace `add_design_entry` frontend tool with `generate_design` in `src/app/page.tsx`. Add `ROOF_TYPE_IMAGE_MAP` constant and `DESIGN_GENERATION_DELAY_MS` constant (both marked `// DEMO-ONLY`). The `generate_design` handler: creates entry with `status: "processing"`, appends to `state.designs`, calls `setState`, waits `DESIGN_GENERATION_DELAY_MS`, then resolves entry to `status: "complete"` with roof-type-mapped `imageUrl`, calls `setState` again. Use a `useRef` to store timer ID for cleanup. Mark all new code with `// DEMO-ONLY` comments. Remove the old `add_design_entry` `useFrontendTool` registration entirely. Verify by: `npx tsc --noEmit && npm run lint`.

## 4. Processing Overlay UI

- [ ] 4.1 Update `DesignComponent` in `src/components/design-component.tsx` to render a processing overlay for entries with `status: "processing"`. The overlay covers the image area only (not the full card) and contains a CSS-animated spinner and text "Generating truss structure...". Hide the `<img>` during processing. Card ID (`#N`) and prompt text remain visible. Processing entries MUST NOT open the modal on click. Entries with `status: "complete"` (or omitted) render unchanged. Verify by: `npx tsc --noEmit && npm run lint`.

## 5. Agent System Prompt

- [ ] 5.1 Update the agent system prompt in `agent/src/agent.py`: replace the `add_design_entry` instruction block with a `generate_design` instruction that tells the agent to call `generate_design` once after the user confirms all required parameters (not after every response). Remove `CRITICAL REQUIREMENT`, `EVERY SINGLE`, and `non-negotiable` language related to design entry creation. Mark the instruction with `# DEMO-ONLY`. Preserve all existing instructions for `get_knowledge_summary`, `query_knowledge_base`, `update_design_parameters`, `modify_design_entry`, and `download_test_image`. Remove the commented-out `add_design_entry` backend tool function. Verify by: `cd agent && python -m ruff check . && python -m mypy .`.

## 6. Verification

- [ ] 6.1 Run full lint and typecheck across both frontend and backend. Verify by: `npx tsc --noEmit && npm run lint && cd agent && python -m ruff check . && python -m mypy .`. All commands MUST exit zero.
