## Why

The demo script (Step 3) requires the agent to announce "generating design..." and the UI to show a visible processing state before displaying a result. Currently `add_design_entry` creates entries instantly with a `/next.svg` placeholder — no delay, no loading indicator, no parameter-specific output. The audience needs to see a realistic generation workflow to believe the "engineering-ready design in minutes" value proposition. This is demo-only functionality that must be clearly delimited so it can be removed or replaced when real Pamir backend integration arrives.

## What Changes

- Add a `status` field to `DesignEntry` (`"processing"` | `"complete"`) so entries can exist in a loading state before resolution.
- Replace the `add_design_entry` frontend tool with a `generate_design` tool that: creates an entry in `"processing"` status, waits a configurable artificial delay (default ~3s), then resolves it to `"complete"` with a parameter-mapped static image.
- Add a set of static truss/roof schematic SVGs to `public/` mapped to common `roofType` values (`Gable`, `Hip`, `Mono-pitch`, `Flat`).
- Update `DesignComponent` to render a "Generating..." overlay/spinner on entries with `status: "processing"`.
- Update the agent system prompt to announce design generation and call `generate_design` instead of `add_design_entry`.
- Mark all simulated-delay and demo-only code with explicit `DEMO-ONLY` / `TESTING` comments and wrap behind a configurable flag so the artificial wait is visually and programmatically distinguishable from production behavior.
- Remove or retire the old `add_design_entry` tool registration and its associated `TEMPORARY` markers.

## Non-goals

- Real Pamir or backend integration — this is explicitly out of scope per the demo gap analysis.
- Real image generation or CAD output — static SVGs only.
- Progress bar or multi-stage generation simulation — a single processing → complete transition is sufficient.
- Persistent generation state across page reloads.
- Parameter-dependent image complexity beyond roof-type mapping (e.g., pitch angle or floor plan dimensions do not change the selected SVG).
- Removing the `modify_design_entry` or `download_test_image` tools — those remain unchanged.

## Capabilities

### New Capabilities
- `design-generation-processing`: The simulated design generation flow — entry creation with processing state, configurable artificial delay, parameter-to-image mapping, and resolution to a static result image. Covers the `generate_design` frontend tool, the `status` field on `DesignEntry`, the loading overlay in `DesignComponent`, and the static SVG image assets.

### Modified Capabilities
- `design-entry-model`: Adds a `status` field (`"processing"` | `"complete"`) to the `DesignEntry` interface (TypeScript) and Pydantic model (Python), with `"complete"` as the default for backward compatibility.
- `design-display`: `DesignComponent` must render a loading overlay on entries with `status: "processing"`, hiding the image until the entry resolves to `"complete"`.
- `design-auto-creation`: The `add_design_entry` frontend tool is replaced by `generate_design`. The system prompt instruction changes from "call after every response" to "call when design generation is appropriate." The old `TEMPORARY` markers are replaced with `DEMO-ONLY` markers.

## Impact

- `src/lib/types.ts` — `DesignEntry` gains a `status` field.
- `src/app/page.tsx` — `add_design_entry` tool replaced by `generate_design` tool with async delay logic; `modify_design_entry` and `update_design_parameters` unchanged.
- `src/components/design-component.tsx` — rendering logic updated to show processing overlay for entries with `status: "processing"`.
- `agent/src/agent.py` — system prompt updated to reference `generate_design` instead of `add_design_entry`; backend `DesignEntry` model gains `status` field.
- `public/` — new static SVG files added for each roof type variant.
- No new npm or pip dependencies. All delay logic uses standard `setTimeout`/`Promise` on the frontend.
