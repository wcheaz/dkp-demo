## Purpose

The Design Display capability provides a scrollable list of design entries with image preview and modal enlargement, driven by an `AgentState` containing a `designs` array.

## Requirements

### Requirement: DesignComponent renders a scrollable list of design entries
The `DesignComponent` SHALL accept an `AgentState` containing a `designs` array of `DesignEntry` objects and a `parameters` field of type `DesignParameters`. The component SHALL render a parameter display section above the scrollable design cards container (see `design-params-display` capability). Each `DesignEntry` SHALL have an `imageUrl` (string), a `promptText` (string), and a `status` field (`"processing" | "complete"`). The component SHALL render one card per entry inside a scrollable container. Multiple cards SHALL be visible simultaneously. The scrollable container SHALL use `overflow-y: auto` so the user can scroll through the design history. Each card SHALL contain an `<img>` element with `src` set to the entry's `imageUrl` and a text element displaying the entry's `promptText`.

All user-facing text in the component SHALL be sourced from the translation dictionary via `useTranslations('designs')` hook. The following strings SHALL be translation keys, NOT hardcoded: the heading text, empty state message, processing overlay text, `MATERIAL_STAT_LABELS` values, `PARAM_LABELS` values, "Material Estimate" label, "Price:" label, and image alt text. Currency display SHALL use `Intl.NumberFormat('sk-SK', ...)` for formatting, with the currency symbol derived from the translation dictionary.

For entries with `status: "processing"`, the card SHALL render a processing overlay covering the image area instead of the normal image. The overlay SHALL contain a CSS-animated spinner and the translated text from the translation dictionary key `designs.generating`. The image SHALL be hidden during processing. The card ID (`#N`) and prompt text SHALL remain visible above and below the overlay. Clicking the overlay or the processing entry SHALL NOT open the modal.

The component SHALL maintain a `activeViewerIndex` state (type `number`) initialized to the last index in `designs` with `dxfContent`, or `-1` if none exist. This state SHALL reset to the new last DXF index whenever the `designs` array length changes.

For entries with `status: "complete"` (including the default), the card image area rendering SHALL follow this logic:
1. If ANY parameter field on the entry is missing (undefined/null), empty string, or set to `"---"` → render a "Design In Progress" placeholder image (`/design-in-progress.svg`) instead of `entry.imageUrl`. Clicking the placeholder SHALL NOT open the modal.
2. If ALL parameter fields are filled with real (non-`"---"`, non-empty) values AND `entry.dxfContent` is a non-empty string:
   - If `index === activeViewerIndex` → render the `<CadViewer>` component with `dxfContent={entry.dxfContent}` and `key={entry.id}`.
   - If `index !== activeViewerIndex` → render a clickable overlay div with instructional text (e.g., "Click to view") and `cursor: pointer`. Clicking this overlay SHALL update `activeViewerIndex` to `index`. A "Download DXF" button SHALL be rendered below the overlay.
3. If ALL parameter fields are filled with real values AND `entry.dxfContent` is undefined/null/empty → render `entry.imageUrl` as before via `<img>`, allowing click-to-enlarge. A "Generating CAD drawing..." status indicator SHALL be shown below the image.

A static SVG file at `public/design-in-progress.svg` SHALL exist as the placeholder image. It SHALL display "Design In Progress" text with styling consistent with the existing design card aesthetic.

#### Scenario: Empty state when no designs exist
- **WHEN** the `designs` array on `AgentState` is empty or undefined
- **THEN** the component SHALL display the translated empty-state message from key `designs.empty`, and SHALL render zero design cards. The parameter display section SHALL still render above the empty state.

#### Scenario: Single design entry displayed
- **WHEN** the `designs` array contains one `DesignEntry` with `imageUrl` set to `"tmp/next.svg"` and `promptText` set to `"Draw a flowchart of user login"` and `status` omitted (defaults to `"complete"`) and `parameters` contains all filled fields
- **THEN** the component SHALL render exactly one card containing an `<img>` element whose `src` attribute equals `"tmp/next.svg"` and a text element containing `"Draw a flowchart of user login"`. No processing overlay SHALL be shown.

#### Scenario: Multiple design entries displayed in order with scroll
- **WHEN** the `designs` array contains five entries in order: A, B, C, D, E (all with `status: "complete"`)
- **THEN** the component SHALL render five cards in the same order inside a scrollable container, each showing its own image and prompt text. At least two cards SHALL be visible without scrolling.

#### Scenario: Processing entry shows translated overlay text
- **WHEN** the `designs` array contains one entry with `status: "processing"`, `imageUrl: "/design-gable.svg"`, and `promptText: "10x15m gable roof"`
- **THEN** the card SHALL render a processing overlay in the image area containing a CSS-animated spinner and the translated text from key `designs.generating`. The `<img>` element SHALL NOT be visible. The card ID (`#N`) and prompt text "10x15m gable roof" SHALL still be visible.

#### Scenario: Processing entry does not open modal on click
- **WHEN** the user clicks on the processing overlay of a design entry with `status: "processing"`
- **THEN** the modal SHALL NOT open. No modal overlay SHALL appear.

#### Scenario: Entry transitions from processing to complete with dxfContent
- **WHEN** a design entry transitions from `status: "processing"` to `status: "complete"` and `dxfContent` changes from `undefined` to a base64 string
- **THEN** the processing overlay SHALL disappear and the `<CadViewer>` component SHALL render with the DXF content

#### Scenario: Entry with all parameters filled and dxfContent renders viewer when active
- **WHEN** the `designs` array contains one entry with `status: "complete"`, all parameters filled, `imageUrl: "/design-gable.svg"`, `dxfContent: "base64string"`, and `activeViewerIndex` equals this entry's index
- **THEN** the card SHALL render `<CadViewer dxfContent="base64string" />` in the image area
- **AND** SHALL NOT render an `<img>` element or clickable overlay

#### Scenario: Inactive design with dxfContent shows clickable overlay
- **WHEN** the `designs` array contains two entries with `dxfContent` and `activeViewerIndex` is `1`
- **THEN** the design at index `0` SHALL render a clickable overlay with instructional text in the viewer area
- **AND** the design at index `1` SHALL render a live `<CadViewer>`

#### Scenario: Clicking overlay switches active viewer
- **WHEN** `activeViewerIndex` is `1` and the user clicks the overlay on the design at index `0`
- **THEN** `activeViewerIndex` SHALL become `0`
- **AND** the `<CadViewer>` SHALL mount for index `0`
- **AND** the design at index `1` SHALL now show the overlay

#### Scenario: New design resets activeViewerIndex
- **WHEN** `activeViewerIndex` is `0` and a new design with `dxfContent` is appended at index `2`
- **THEN** `activeViewerIndex` SHALL become `2` (the new last index with DXF content)

#### Scenario: Single design with DXF is active without overlay
- **WHEN** the `designs` array contains exactly one entry with `dxfContent`
- **THEN** that entry SHALL render a live `<CadViewer>` (no overlay)

#### Scenario: Entry with all parameters filled but no dxfContent renders image
- **WHEN** the `designs` array contains one entry with `status: "complete"`, all parameters filled, `imageUrl: "/design-gable.svg"`, and `dxfContent: undefined`
- **THEN** the card SHALL render `<img src="/design-gable.svg" />` as before
- **AND** SHALL show a "Generating CAD drawing..." status indicator below the image

#### Scenario: Complete entry allows click-to-enlarge
- **WHEN** the user clicks on the `<img>` element of a design entry with `status: "complete"` and all parameters filled
- **THEN** the modal SHALL open as per existing behavior (see modal requirement in base spec).

#### Scenario: Entry with incomplete parameters shows Design In Progress placeholder
- **WHEN** the `designs` array contains one entry with `status: "complete"`, `imageUrl: "/design-gable.svg"`, and `parameters: { buildingType: "House", roofType: "---" }`
- **THEN** the card SHALL render the "Design In Progress" placeholder image (`/design-in-progress.svg`) instead of `entry.imageUrl`. The `<img>` element SHALL have `src="/design-in-progress.svg"`.

#### Scenario: Entry with missing parameters shows placeholder
- **WHEN** the `designs` array contains one entry with `status: "complete"`, `imageUrl: "/design-gable.svg"`, and `parameters: { buildingType: "House" }` (missing other fields)
- **THEN** the card SHALL render the "Design In Progress" placeholder image (`/design-in-progress.svg`).

#### Scenario: Entry with no parameters shows placeholder
- **WHEN** the `designs` array contains one entry with `status: "complete"`, `imageUrl: "/design-gable.svg"`, and `parameters: undefined` or `parameters: {}`
- **THEN** the card SHALL render the "Design In Progress" placeholder image (`/design-in-progress.svg`).

#### Scenario: Placeholder image does not open modal on click
- **WHEN** the user clicks on the "Design In Progress" placeholder image
- **THEN** the modal SHALL NOT open.

#### Scenario: Entry with all parameters filled shows actual image
- **WHEN** the `designs` array contains one entry with `status: "complete"`, `imageUrl: "/design-gable.svg"`, and all parameter fields filled with real values (none missing, none `"---"`, none empty)
- **THEN** the card SHALL render `<img>` with `src="/design-gable.svg"` (the actual design image).

#### Scenario: Cleared parameter triggers placeholder
- **WHEN** a design entry has all parameters filled and showing `entry.imageUrl`, and then `parameters.roofType` is changed to `"---"` via `reset_design`
- **THEN** the card SHALL re-render showing the "Design In Progress" placeholder image instead of `entry.imageUrl`.

### Requirement: Price display hides info icon when placeholder

When a design entry's `price` field is set to `"---"`, the `DesignComponent` SHALL display the price value as `"---"` but SHALL NOT render the pricing info icon (the circled `!` SVG). The info icon opens the pricing breakdown modal, which is not meaningful when the price is a placeholder. The "Price:" label SHALL come from the translation dictionary key `designs.price`.

#### Scenario: Price placeholder shows value without info icon
- **GIVEN** a design entry with `price: "---"`
- **WHEN** the `DesignComponent` renders the price section
- **THEN** the price value `"---"` SHALL be displayed with the translated label from `designs.price`
- **AND** the pricing info icon SHALL NOT be rendered

#### Scenario: Real price shows value with info icon
- **GIVEN** a design entry with `price: "€1,752"`
- **WHEN** the `DesignComponent` renders the price section
- **THEN** the price value `"€1,752"` SHALL be displayed
- **AND** the pricing info icon SHALL be rendered

### Requirement: design-in-progress.svg placeholder image file

A static SVG file at `public/design-in-progress.svg` SHALL exist. The SVG SHALL display "Design In Progress" text centered within the image area, with styling consistent with the existing design card aesthetic (muted colors, similar dimensions to other design images).

#### Scenario: Placeholder SVG file exists
- **WHEN** the application checks for `public/design-in-progress.svg`
- **THEN** the file SHALL exist and be a valid SVG

#### Scenario: Placeholder SVG renders in browser
- **WHEN** an `<img>` element has `src="/design-in-progress.svg"`
- **THEN** it SHALL render a visible image containing the text "Design In Progress"

### Requirement: DesignComponent accepts standard image formats
The `<img>` element in each design card SHALL accept any standard image format path or URL assigned to `imageUrl`, including but not limited to: jpg, jpeg, png, gif, svg, webp, and bmp. The component SHALL NOT perform format validation or conversion — it SHALL pass `imageUrl` directly to the `<img src>` attribute.

#### Scenario: PNG image renders without error
- **WHEN** a `DesignEntry` has `imageUrl` set to `"tmp/design-output.png"`
- **THEN** the component SHALL render an `<img>` element with `src="tmp/design-output.png"` without throwing or catching format errors.

#### Scenario: SVG image renders without error
- **WHEN** a `DesignEntry` has `imageUrl` set to `"tmp/next.svg"`
- **THEN** the component SHALL render an `<img>` element with `src="tmp/next.svg"` without throwing or catching format errors.

### Requirement: Images have a standard consistent size
Each image in a design card SHALL be sized to `width: 80%` (4/5ths) of the card's natural width and `height: 40vh` (approximately 2/5ths of the viewport height). Images SHALL use `object-fit: contain` to preserve their aspect ratio within these bounds without distortion.

#### Scenario: Image dimensions are consistent across entries
- **WHEN** the `designs` array contains three entries with different source images
- **THEN** all three `<img>` elements SHALL have the same computed width (80% of card width) and the same computed height (40vh), and all SHALL have `object-fit: contain`.

#### Scenario: Image does not overflow card bounds
- **WHEN** a design card is rendered with an image
- **THEN** the image SHALL NOT cause horizontal overflow of the card. The image width SHALL be constrained to 80% of the card width.

### Requirement: Clicking an image opens a modal overlay
The component SHALL implement a modal overlay for image enlargement. When the user clicks an `<img>` element in a design card, the component SHALL set internal state to display a modal. The modal SHALL render a fixed-position overlay covering the entire viewport (`position: fixed; inset: 0`) with a semi-transparent dark backdrop (`bg-black/80` or equivalent). The modal SHALL display the clicked image at a larger size constrained by `max-width: 90vw` and `max-height: 90vh` with `object-fit: contain`, centered within the overlay.

#### Scenario: Click image opens modal
- **WHEN** the user clicks on an `<img>` element inside a design card
- **THEN** a modal overlay SHALL appear covering the viewport, displaying the same image at a larger size (up to 90vw × 90vh).

#### Scenario: Modal displays correct image
- **WHEN** the user clicks the image of the second design entry (imageUrl: `"tmp/second.svg"`)
- **THEN** the modal SHALL display an `<img>` with `src="tmp/second.svg"` at the enlarged size.

### Requirement: Modal is dismissible by backdrop click and Escape key
The modal SHALL close and disappear when the user clicks on the backdrop area (outside the enlarged image) or presses the Escape key. Clicking on the enlarged image itself SHALL NOT close the modal.

#### Scenario: Clicking backdrop closes modal
- **WHEN** the modal is open and the user clicks on the dark backdrop area (not on the image)
- **THEN** the modal SHALL close and the overlay SHALL be removed from the DOM.

#### Scenario: Pressing Escape closes modal
- **WHEN** the modal is open and the user presses the Escape key
- **THEN** the modal SHALL close and the overlay SHALL be removed from the DOM.

#### Scenario: Clicking the enlarged image does not close modal
- **WHEN** the modal is open and the user clicks on the enlarged image itself
- **THEN** the modal SHALL remain open.

### Requirement: AgentState carries designs array
`AgentState` in `src/lib/types.ts` SHALL define a `designs` field of type `DesignEntry[]` and a `parameters` field of type `DesignParameters`. `DesignEntry` SHALL be an exported interface with `imageUrl: string` and `promptText: string`. `DesignParameters` SHALL be an exported interface with optional string/number fields for construction parameters. The old `procurement_codes`-related types and `your_data` field SHALL be removed from `AgentState`.

#### Scenario: AgentState type compiles with designs and parameters fields
- **WHEN** TypeScript compilation is run on `src/lib/types.ts`
- **THEN** the file SHALL compile without errors and `AgentState` SHALL have exactly two fields: `designs: DesignEntry[]` and `parameters: DesignParameters`.

#### Scenario: DesignEntry has required fields
- **WHEN** a `DesignEntry` object is created with `{ imageUrl: "tmp/next.svg", promptText: "test prompt" }`
- **THEN** the object SHALL satisfy the `DesignEntry` interface without TypeScript errors.

#### Scenario: AgentState accepts parameters field
- **WHEN** an `AgentState` object is created with `{ designs: [], parameters: { buildingType: "Family house" } }`
- **THEN** the object SHALL satisfy the `AgentState` type without TypeScript errors.

### Requirement: DesignComponent is exported from design-component.tsx
The component SHALL be exported as a named export `DesignComponent` from `src/components/design-component.tsx`. The old file `src/components/procurement-codes.tsx` SHALL NOT exist after this change. The old named export `ProcurementCodes` SHALL NOT exist.

#### Scenario: Import DesignComponent succeeds
- **WHEN** another module imports `{ DesignComponent }` from `@/components/design-component`
- **THEN** the import SHALL resolve without error and `DesignComponent` SHALL be a valid React function component.

#### Scenario: Old procurement-codes file does not exist
- **WHEN** the filesystem is checked for `src/components/procurement-codes.tsx`
- **THEN** the file SHALL NOT exist.

### Requirement: Designs list is append-only
The component SHALL render the `designs` array as a read-only display. The component SHALL NOT provide UI for deleting, reordering, or editing entries. New entries are appended to the array by external calling code (the AI agent's post-prompt handler) via `setState`.

#### Scenario: No delete button on entries
- **WHEN** the `designs` array contains one or more entries and the component is rendered
- **THEN** each design card SHALL NOT contain a delete, remove, or close button.

#### Scenario: Appending a new design via setState
- **WHEN** external code calls `setState` with a new `AgentState` where `designs` is `[...existingDesigns, newEntry]`
- **THEN** the component SHALL re-render showing all previous entries plus the new entry at the end of the list.

### Requirement: DesignComponent is rendered in the frontend page
`src/app/page.tsx` SHALL import and render `DesignComponent` instead of `YourComponent`. The `<YourComponent>` reference SHALL be replaced with `<DesignComponent state={state} setState={setState} />`. The old `YourComponent` import SHALL be removed.

#### Scenario: Page imports DesignComponent
- **WHEN** `src/app/page.tsx` is inspected
- **THEN** the file SHALL contain `import { DesignComponent } from "@/components/design-component"` and SHALL NOT contain `import.*YourComponent`.

#### Scenario: Page renders DesignComponent
- **WHEN** `src/app/page.tsx` is rendered in the browser
- **THEN** the page SHALL render `<DesignComponent>` with `state` and `setState` props, and SHALL NOT render `<YourComponent>`.

### Requirement: Agent tool code is commented out and preserved
The `DesignEntry` model, `designs` field on `YourState`, and `add_design_entry` tool in `agent/src/agent.py` SHALL be commented out (not deleted). The agent's `system_prompt` SHALL NOT reference `add_design_entry`. This code is preserved for future reference when real image generation is integrated.

#### Scenario: Agent code is commented out
- **WHEN** `agent/src/agent.py` is inspected for `add_design_entry`
- **THEN** the `DesignEntry` class, `designs` field, and `add_design_entry` function SHALL be present but commented out.
- **AND** the `system_prompt` string SHALL NOT contain `add_design_entry`.

#### Scenario: Agent passes lint and typecheck
- **WHEN** `cd agent && python -m ruff check . && python -m mypy .` is run
- **THEN** both commands SHALL exit zero with no errors.

### Requirement: AddDesignButton component appends test entries
A reusable `AddDesignButton` component SHALL be exported from `src/components/add-design-button.tsx`. It SHALL accept `{ state: AgentState; setState: (state: AgentState) => void }` props. When clicked, the button SHALL append a `DesignEntry` with `imageUrl: "tmp/next.svg"` and `promptText: "Test design #N"` (where N is the new total count) to `state.designs` via `setState`. The component is intentionally generic for reuse in other contexts.

#### Scenario: Button click appends entry
- **WHEN** the user clicks the `AddDesignButton` and the current `state.designs` has 0 entries
- **THEN** `setState` SHALL be called with a new state where `designs` contains one entry with `imageUrl: "tmp/next.svg"` and `promptText: "Test design #1"`.

#### Scenario: Multiple clicks append multiple entries
- **WHEN** the user clicks `AddDesignButton` three times
- **THEN** `state.designs` SHALL contain three entries with prompt texts "Test design #1", "Test design #2", and "Test design #3", in order.

### Requirement: AddDesignButton is rendered in the frontend page
`src/app/page.tsx` SHALL import and render `AddDesignButton` above the `DesignComponent` render within `YourMainContent`. The button SHALL receive `state` and `setState` as props.

#### Scenario: Page imports and renders AddDesignButton
- **WHEN** `src/app/page.tsx` is inspected
- **THEN** the file SHALL contain `import { AddDesignButton } from "@/components/add-design-button"` and SHALL render `<AddDesignButton state={state} setState={setState} />` above `<DesignComponent>`.

### Requirement: Test images resolve to tmp/next.svg
During testing, all `DesignEntry` instances SHALL have their `imageUrl` set to `"tmp/next.svg"`. This ensures deterministic rendering without depending on external image generation.

#### Scenario: Test entry uses tmp/next.svg
- **WHEN** a test creates a `DesignEntry` with `imageUrl: "tmp/next.svg"`
- **THEN** the rendered `<img>` element SHALL have `src="tmp/next.svg"` and the file `tmp/next.svg` SHALL exist in the repository.
