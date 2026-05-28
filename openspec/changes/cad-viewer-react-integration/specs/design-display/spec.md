## MODIFIED Requirements

### Requirement: DesignComponent renders a scrollable list of design entries
The `DesignComponent` SHALL accept an `AgentState` containing a `designs` array of `DesignEntry` objects and a `parameters` field of type `DesignParameters`. The component SHALL render a parameter display section above the scrollable design cards container (see `design-params-display` capability). Each `DesignEntry` SHALL have an `imageUrl` (string), a `promptText` (string), and a `status` field (`"processing" | "complete"`). The component SHALL render one card per entry inside a scrollable container. Multiple cards SHALL be visible simultaneously. The scrollable container SHALL use `overflow-y: auto` so the user can scroll through the design history. Each card SHALL contain an `<img>` element with `src` set to the entry's `imageUrl` and a text element displaying the entry's `promptText`.

All user-facing text in the component SHALL be sourced from the translation dictionary via `useTranslations('designs')` hook. The following strings SHALL be translation keys, NOT hardcoded: the heading text, empty state message, processing overlay text, `MATERIAL_STAT_LABELS` values, `PARAM_LABELS` values, "Material Estimate" label, "Price:" label, and image alt text. Currency display SHALL use `Intl.NumberFormat('sk-SK', ...)` for formatting, with the currency symbol derived from the translation dictionary.

For entries with `status: "processing"`, the card SHALL render a processing overlay covering the image area instead of the normal image. The overlay SHALL contain a CSS-animated spinner and the translated text from the translation dictionary key `designs.generating`. The image SHALL be hidden during processing. The card ID (`#N`) and prompt text SHALL remain visible above and below the overlay. Clicking the overlay or the processing entry SHALL NOT open the modal.

For entries with `status: "complete"` (including the default), the card image area rendering SHALL follow this logic:
1. If ANY parameter field on the entry is missing (undefined/null), empty string, or set to `"---"` → render a "Design In Progress" placeholder image (`/design-in-progress.svg`) instead of `entry.imageUrl`. Clicking the placeholder SHALL NOT open the modal.
2. If ALL parameter fields are filled with real (non-`"---"`, non-empty) values AND `entry.dxfContent` is a non-empty string → render the `<CadViewer>` component with `dxfContent={entry.dxfContent}` instead of the `<img>` element. Clicking the viewer SHALL NOT open the modal. A "Download DXF" button SHALL be rendered below the viewer.
3. If ALL parameter fields are filled with real values AND `entry.dxfContent` is undefined/null/empty → render `entry.imageUrl` as before via `<img>`, allowing click-to-enlarge. A "Generating CAD drawing..." status indicator SHALL be shown below the image.

#### Scenario: Entry transitions from processing to complete with dxfContent
- **WHEN** a design entry transitions from `status: "processing"` to `status: "complete"` and `dxfContent` changes from `undefined` to a base64 string
- **THEN** the processing overlay SHALL disappear and the `<CadViewer>` component SHALL render with the DXF content

#### Scenario: Entry with all parameters filled and dxfContent renders viewer
- **WHEN** the `designs` array contains one entry with `status: "complete"`, all parameters filled, `imageUrl: "/design-gable.svg"`, and `dxfContent: "base64string"`
- **THEN** the card SHALL render `<CadViewer dxfContent="base64string" />` in the image area
- **AND** SHALL NOT render an `<img>` element

#### Scenario: Entry with all parameters filled but no dxfContent renders image
- **WHEN** the `designs` array contains one entry with `status: "complete"`, all parameters filled, `imageUrl: "/design-gable.svg"`, and `dxfContent: undefined`
- **THEN** the card SHALL render `<img src="/design-gable.svg" />` as before
- **AND** SHALL show a "Generating CAD drawing..." status indicator below the image

#### Scenario: Entry with incomplete parameters shows placeholder (unchanged)
- **WHEN** the `designs` array contains one entry with `status: "complete"`, `imageUrl: "/design-gable.svg"`, and `parameters: { buildingType: "House", roofType: "---" }`
- **THEN** the card SHALL render the "Design In Progress" placeholder image (`/design-in-progress.svg`) regardless of `dxfContent` value

#### Scenario: Processing entry shows overlay (unchanged)
- **WHEN** the `designs` array contains one entry with `status: "processing"`, `imageUrl: "/design-gable.svg"`, and `promptText: "10x15m gable roof"`
- **THEN** the card SHALL render a processing overlay in the image area containing a CSS-animated spinner and the translated text. The `<img>` or `<CadViewer>` SHALL NOT be visible.
