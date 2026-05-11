## Purpose

Defines the simulated design generation flow: entry creation with processing state, configurable artificial delay, roof-type-to-image mapping, and resolution to a static result SVG. This is demo-only functionality.

## Requirements

### Requirement: generate_design frontend tool creates entries with processing status
A frontend tool named `generate_design` SHALL be registered using `useFrontendTool` inside the `YourMainContent` component in `src/app/page.tsx`. The tool SHALL accept one parameter: `prompt_text` (string). The tool handler SHALL create a `DesignEntry` with `status: "processing"`, `imageUrl` set to `"/design-gable.svg"` (fallback), and `promptText` set to `prompt_text`. The entry SHALL be appended to the existing `state.designs` array and `setState` called immediately. All code for this tool SHALL be wrapped in `// DEMO-ONLY` comments indicating it is simulated demo behavior.

#### Scenario: generate_design creates a processing entry
- **WHEN** the agent calls the frontend tool `generate_design` with `prompt_text: "10x15m gable roof house"`
- **THEN** `setState` SHALL be called with a new state where `state.designs` contains a new `DesignEntry` with `status: "processing"`, `imageUrl: "/design-gable.svg"`, and `promptText: "10x15m gable roof house"`

#### Scenario: generate_design does not lose existing designs
- **WHEN** the agent calls `generate_design` and `state.designs` already contains one entry
- **THEN** `setState` SHALL be called with `state.designs` containing two entries: the original entry followed by the new entry with `status: "processing"`

#### Scenario: generate_design handles undefined designs array
- **WHEN** the agent calls `generate_design` and `state.designs` is undefined
- **THEN** the handler SHALL treat `state.designs` as an empty array and append the new entry, resulting in a single-entry array

#### Scenario: DEMO-ONLY markers present in page.tsx
- **WHEN** `src/app/page.tsx` is searched for the string `DEMO-ONLY`
- **THEN** at least 1 occurrence SHALL be found near the `generate_design` frontend tool registration

### Requirement: generate_design resolves processing entries after a configurable delay
After creating the processing entry, the `generate_design` handler SHALL wait for a configurable delay (`DESIGN_GENERATION_DELAY_MS`, default 3000ms), then select the appropriate result image based on `state.parameters.roofType`, update the entry's `status` to `"complete"` and `imageUrl` to the mapped image path, and call `setState`. The delay constant SHALL be marked with a `// DEMO-ONLY` comment.

#### Scenario: Entry resolves to complete after delay with gable roof
- **WHEN** `generate_design` is called and `state.parameters.roofType` is `"Gable"`
- **THEN** after the delay, the entry's `status` SHALL be `"complete"` and `imageUrl` SHALL be `"/design-gable.svg"`

#### Scenario: Entry resolves to complete after delay with hip roof
- **WHEN** `generate_design` is called and `state.parameters.roofType` is `"Hip"`
- **THEN** after the delay, the entry's `status` SHALL be `"complete"` and `imageUrl` SHALL be `"/design-hip.svg"`

#### Scenario: Entry resolves to fallback image for unknown roof type
- **WHEN** `generate_design` is called and `state.parameters.roofType` is undefined or an unrecognized value
- **THEN** after the delay, the entry's `status` SHALL be `"complete"` and `imageUrl` SHALL be `"/design-gable.svg"` (the fallback)

#### Scenario: Delay constant is DEMO-ONLY marked
- **WHEN** `src/app/page.tsx` is inspected for `DESIGN_GENERATION_DELAY_MS`
- **THEN** the constant SHALL be defined with value `3000` and preceded by a `// DEMO-ONLY` comment

### Requirement: Roof-type-to-image mapping table
A constant `ROOF_TYPE_IMAGE_MAP` of type `Record<string, string>` SHALL be defined in `src/app/page.tsx`. It SHALL map the following keys to SVG paths in `public/`:
- `"Gable"` → `"/design-gable.svg"`
- `"Hip"` → `"/design-hip.svg"`
- `"Mono-pitch"` → `"/design-mono.svg"`
- `"Flat"` → `"/design-flat.svg"`

The constant SHALL be marked with a `// DEMO-ONLY` comment.

#### Scenario: All roof types map to correct SVG paths
- **WHEN** `ROOF_TYPE_IMAGE_MAP["Gable"]` is accessed
- **THEN** it SHALL return `"/design-gable.svg"`
- **WHEN** `ROOF_TYPE_IMAGE_MAP["Hip"]` is accessed
- **THEN** it SHALL return `"/design-hip.svg"`
- **WHEN** `ROOF_TYPE_IMAGE_MAP["Mono-pitch"]` is accessed
- **THEN** it SHALL return `"/design-mono.svg"`
- **WHEN** `ROOF_TYPE_IMAGE_MAP["Flat"]` is accessed
- **THEN** it SHALL return `"/design-flat.svg"`

### Requirement: Static roof-type SVG files exist in public directory
The following SVG files SHALL exist in `public/` and be servable by Next.js:
- `public/design-gable.svg` — gable roof schematic
- `public/design-hip.svg` — hip roof schematic
- `public/design-mono.svg` — mono-pitch roof schematic
- `public/design-flat.svg` — flat roof schematic

Each SVG SHALL contain a visually distinct truss/roof schematic appropriate to its type. The SVGs do not need to be parameter-dependent beyond the roof shape.

#### Scenario: All roof-type SVGs are servable
- **WHEN** the application starts
- **THEN** `public/design-gable.svg`, `public/design-hip.svg`, `public/design-mono.svg`, and `public/design-flat.svg` SHALL all exist and return HTTP 200 when served by Next.js

### Requirement: Timer cleanup on component unmount
The `generate_design` handler SHALL store the `setTimeout` timer ID. If the component unmounts before the timer fires, the timer SHALL be cleared to prevent state updates on unmounted components. The entry SHALL remain in `"processing"` state if the timer is cleared early.

#### Scenario: Timer does not fire after unmount
- **WHEN** `generate_design` creates a processing entry and the component unmounts before the delay elapses
- **THEN** `setState` SHALL NOT be called after unmount, and no React state update warning SHALL appear in the console

### Requirement: All code passes lint and type checking
The modified files SHALL pass all lint and type checking commands.

#### Scenario: Frontend passes TypeScript check
- **WHEN** `npx tsc --noEmit` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Frontend passes lint
- **WHEN** `npm run lint` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Agent passes ruff check
- **WHEN** `cd agent && python -m ruff check .` is run
- **THEN** the command SHALL exit zero with no errors

#### Scenario: Agent passes mypy
- **WHEN** `cd agent && python -m mypy .` is run
- **THEN** the command SHALL exit zero with no errors
