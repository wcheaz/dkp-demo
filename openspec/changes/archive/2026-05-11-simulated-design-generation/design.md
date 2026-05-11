## Context

The project is a demo application for an AI-enabled timber truss design assistant. The frontend is a Next.js React app using CopilotKit for agent interaction. The agent backend uses Pydantic AI with an OpenAI-compatible model. State flows from agent → frontend tools → React state → UI components.

Currently, `add_design_entry` (a CopilotKit `useFrontendTool` registered in `src/app/page.tsx`) instantly creates a `DesignEntry` with `imageUrl: "/next.svg"` and appends it to `state.designs`. There is no intermediate state, no delay, and no parameter-specific output. The agent's system prompt mandates calling this tool after every response.

The demo script requires Step 3 to show: agent announces generation → UI shows processing → result appears after a few seconds. This change simulates that flow entirely on the frontend using static assets and an artificial delay.

## Goals / Non-Goals

**Goals:**
- Create a convincing "generating design" experience for live demo audiences
- Introduce a `status` field on `DesignEntry` that gates image visibility
- Map collected `roofType` parameter to a static result SVG
- Make all demo-only code clearly identifiable for future removal
- Keep the change minimally invasive — only touch files that need changing

**Non-Goals:**
- Real backend image generation or Pamir integration
- Multi-stage progress tracking or real progress bars
- Parameter-dependent image selection beyond `roofType`
- Persistence of processing state across page reloads
- Changing `modify_design_entry`, `download_test_image`, or `update_design_parameters` tools

## Decisions

### D1: Status field is a simple string enum, not a state machine

**Decision:** `status: "processing" | "complete"` with `"complete"` as default.

**Rationale:** Only two states exist for this demo. A numeric progress value or a richer state machine adds complexity with no benefit. The default is `"complete"` so all existing code and entries render normally without migration.

**Alternatives considered:**
- `isProcessing: boolean` — rejected because `"complete"` reads more naturally alongside future states (e.g., `"error"`, `"cancelled"`), and a string enum is self-documenting.
- `"pending" | "generating" | "complete"` — rejected because multi-stage simulation is a non-goal; `"processing"` is sufficient for the single loading → done transition.

### D2: Delay is frontend-only, implemented as a setTimeout/Promise in the tool handler

**Decision:** The `generate_design` tool handler creates the entry with `status: "processing"`, then uses `setTimeout` wrapped in a `Promise` to resolve the entry to `"complete"` after the configured delay.

**Rationale:** No backend changes are needed for the delay. The frontend already owns the tool handler and state management. Keeping the delay client-side avoids network round-trips and backend state synchronization issues.

**Configurable delay constant:**
```typescript
const DESIGN_GENERATION_DELAY_MS = 3000; // DEMO-ONLY — artificial wait for demo presentation
```

**Alternatives considered:**
- Server-side delay via a backend tool — rejected because it adds complexity to the agent backend for a demo-only feature, and the frontend tool pattern already has full state control.
- CSS animation-only approach (no real state change) — rejected because the agent and the user need the entry to actually transition from processing to complete; a purely visual animation would not work with the tool flow.

### D3: Roof-type-to-image mapping is a static lookup table

**Decision:** A hardcoded map from `roofType` string to SVG filename:

```typescript
const ROOF_TYPE_IMAGE_MAP: Record<string, string> = {
  "Gable": "/design-gable.svg",
  "Hip": "/design-hip.svg",
  "Mono-pitch": "/design-mono.svg",
  "Flat": "/design-flat.svg",
};
```

Fallback for unknown/missing `roofType`: `"/design-gable.svg"` (most common).

**Rationale:** The TODO specifies at minimum gable, hip, and flat roof variants. A lookup table is the simplest structure that maps parameter to asset. The fallback ensures the demo never shows a broken image.

**Alternatives considered:**
- Dynamic SVG generation — rejected as a non-goal (no real generation).
- Per-combination mapping (roof type × pitch angle) — rejected per non-goals; pitch angle does not change the selected SVG.

### D4: Processing overlay uses a CSS spinner + "Generating..." text over a dimmed placeholder

**Decision:** When `entry.status === "processing"`, the card renders:
- The image hidden (or a dimmed placeholder)
- An overlay div with a CSS-animated spinner and "Generating truss structure..." text
- The overlay covers the image area only, not the full card

**Rationale:** This matches the demo script language and is visually clear. Using CSS animation avoids external spinner libraries. Restricting the overlay to the image area keeps the card ID and prompt text visible during processing.

**Alternatives considered:**
- Full-card overlay — rejected because hiding the prompt text during generation removes context.
- Skeleton placeholder — rejected because a spinner + text is simpler and more clearly communicates "actively working."

### D5: `add_design_entry` is fully replaced, not wrapped

**Decision:** The `add_design_entry` tool registration is removed entirely and replaced by `generate_design`. The old `TEMPORARY` comments are replaced with `DEMO-ONLY` comments.

**Rationale:** The new tool has different parameters and behavior. Wrapping or aliasing would create confusion. Clean replacement is simpler and removes dead code.

### D6: System prompt changes from "call after every response" to "call when parameters are confirmed"

**Decision:** The system prompt instruction for `add_design_entry` (mandatory after every response) is replaced with an instruction to call `generate_design` only after the user has confirmed all required parameters.

**Rationale:** The current mandatory-after-every-response behavior creates noise entries. The demo flow is: collect parameters → confirm → generate design. The tool should only fire at the generation step.

### D7: Demo-only code is marked with `DEMO-ONLY` comments and a namespace constant

**Decision:** All artificial delay logic, the delay constant, and the roof-type-to-image map are marked with `// DEMO-ONLY` comments. A file-level comment block at the top of the relevant section explains the demo nature.

**Rationale:** The user explicitly requested clear marking of demo/testing functionality. `DEMO-ONLY` is visually distinct from the existing `TEMPORARY` markers and signals "this is intentional demo behavior" rather than "this will be replaced soon."

## Risks / Trade-offs

- **[Processing entries lost on page reload]** → Acceptable: non-goal to persist state. The demo presenter runs a single session. If reload happens, the user restarts the flow via `update_design_parameters`.
- **[Timer drift if component unmounts during delay]** → Mitigate by using a cleanup ref: store the `setTimeout` ID and clear it on component unmount. The entry stays in `"processing"` state but the user can reload to reset.
- **[Static SVGs look unrealistic for pitch/angle variations]** → Acceptable: the demo audience sees a schematic, not a production render. Non-goal to vary by pitch.
- **[Agent calls `generate_design` at wrong time]** → Mitigate by precise system prompt instructions and testing the prompt during implementation. The prompt should specify "call only after user confirms parameters."
- **[Multiple `generate_design` calls create overlapping timers]** → Acceptable: each call creates its own entry with its own timer. They resolve independently. No conflict.
