## MODIFIED Requirements

### Requirement: DesignComponent renders a scrollable list of design entries
The `DesignComponent` SHALL accept an `AgentState` containing a `designs` array of `DesignEntry` objects and a `parameters` field of type `DesignParameters`. The component SHALL render a parameter display section above the scrollable design cards container (see `design-params-display` capability). Each `DesignEntry` SHALL have an `imageUrl` (string), a `promptText` (string), and a `status` field (`"processing" | "complete"`). The component SHALL render one card per entry inside a scrollable container. Multiple cards SHALL be visible simultaneously. The scrollable container SHALL use `overflow-y: auto` so the user can scroll through the design history. Each card SHALL contain an `<img>` element with `src` set to the entry's `imageUrl` and a text element displaying the entry's `promptText`.

All user-facing text in the component SHALL be sourced from the translation dictionary via `useTranslations('designs')` hook. The following strings SHALL be translation keys, NOT hardcoded: the heading text, empty state message, processing overlay text, `MATERIAL_STAT_LABELS` values, `PARAM_LABELS` values, "Material Estimate" label, "Price:" label, "Download DXF" button label, "Download IFC" button label, and image alt text. Currency display SHALL use `Intl.NumberFormat('sk-SK', ...)` for formatting, with the currency symbol derived from the translation dictionary.

For entries with `status: "processing"`, the card SHALL render a processing overlay covering the image area instead of the normal image. The overlay SHALL contain a CSS-animated spinner and the translated text from the translation dictionary key `designs.generating`. The image SHALL be hidden during processing. The card ID (`#N`) and prompt text SHALL remain visible above and below the overlay. Clicking the overlay or the processing entry SHALL NOT open the modal.

The component SHALL maintain a `activeViewerIndex` state (type `number`) initialized to the last index in `designs` with `dxfContent`, or `-1` if none exist. This state SHALL reset to the new last DXF index whenever the `designs` array length changes.

For entries with `status: "complete"` (including the default), the card image area rendering SHALL follow this logic:
1. If ANY parameter field on the entry is missing (undefined/null), empty string, or set to `"---"` → render a "Design In Progress" placeholder image (`/design-in-progress.svg`) instead of `entry.imageUrl`. Clicking the placeholder SHALL NOT open the modal.
2. If ALL parameter fields are filled with real (non-`"---"`, non-empty) values AND `entry.dxfContent` is a non-empty string:
   - If `index === activeViewerIndex` → render the `<CadViewer>` component with `dxfContent={entry.dxfContent}` and `key={entry.id}`. A "Download DXF" button SHALL be rendered below the viewer. If `entry.ifcContent` is a non-empty string, a "Download IFC" button SHALL be rendered adjacent to the "Download DXF" button.
   - If `index !== activeViewerIndex` → render a clickable overlay div with instructional text (e.g., "Click to view") and `cursor: pointer`. Clicking this overlay SHALL update `activeViewerIndex` to `index`. A "Download DXF" button SHALL be rendered below the overlay. If `entry.ifcContent` is a non-empty string, a "Download IFC" button SHALL be rendered adjacent to the "Download DXF" button.
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

#### Scenario: Complete entry with ifcContent renders Download IFC button
- **WHEN** a design entry has `status: "complete"`, all parameters filled, and `ifcContent` contains a valid base64 string
- **THEN** the component SHALL render a "Download IFC" button containing the translated label from `designs.downloadIfc` adjacent to the "Download DXF" button.
