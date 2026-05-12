## MODIFIED Requirements

### Requirement: DesignComponent renders a scrollable list of design entries
The `DesignComponent` SHALL accept an `AgentState` containing a `designs` array of `DesignEntry` objects and a `parameters` field of type `DesignParameters`. The component SHALL render a parameter display section above the scrollable design cards container (see `design-params-display` capability). Each `DesignEntry` SHALL have an `imageUrl` (string), a `promptText` (string), and a `status` field (`"processing" | "complete"`). The component SHALL render one card per entry inside a scrollable container. Multiple cards SHALL be visible simultaneously. The scrollable container SHALL use `overflow-y: auto` so the user can scroll through the design history. Each card SHALL contain an image area and a text element displaying the entry's `promptText`.

For entries with `status: "processing"`, the card SHALL render a processing overlay covering the image area instead of the normal image. The overlay SHALL contain a CSS-animated spinner and the text "Generating truss structure...". The image SHALL be hidden during processing. The card ID (`#N`) and prompt text SHALL remain visible above and below the overlay. Clicking the overlay or the processing entry SHALL NOT open the modal.

For entries with `status: "complete"` (including the default), the card image area rendering SHALL follow this logic:
1. If ANY parameter field on the entry is missing (undefined/null), empty string, or set to `"---"` → render a "Design In Progress" placeholder image (`/design-in-progress.svg`) instead of `entry.imageUrl`. Clicking the placeholder SHALL NOT open the modal.
2. If ALL parameter fields are filled with real (non-`"---"`, non-empty) values → render `entry.imageUrl` as before, allowing click-to-enlarge.

A static SVG file at `public/design-in-progress.svg` SHALL exist as the placeholder image. It SHALL display "Design In Progress" text with styling consistent with the existing design card aesthetic.

#### Scenario: Empty state when no designs exist
- **WHEN** the `designs` array on `AgentState` is empty or undefined
- **THEN** the component SHALL display an empty-state message indicating no designs are available, and SHALL render zero design cards. The parameter display section SHALL still render above the empty state.

#### Scenario: Single design entry displayed
- **WHEN** the `designs` array contains one `DesignEntry` with `imageUrl` set to `"tmp/next.svg"` and `promptText` set to `"Draw a flowchart of user login"` and `status` omitted (defaults to `"complete"`) and `parameters` contains all filled fields
- **THEN** the component SHALL render exactly one card containing an `<img>` element whose `src` attribute equals `"tmp/next.svg"` and a text element containing `"Draw a flowchart of user login"`. No processing overlay SHALL be shown.

#### Scenario: Multiple design entries displayed in order with scroll
- **WHEN** the `designs` array contains five entries in order: A, B, C, D, E (all with `status: "complete"` and all parameters filled)
- **THEN** the component SHALL render five cards in the same order inside a scrollable container, each showing its own image and prompt text. At least two cards SHALL be visible without scrolling.

#### Scenario: Processing entry shows overlay instead of image
- **WHEN** the `designs` array contains one entry with `status: "processing"`, `imageUrl: "/design-gable.svg"`, and `promptText: "10x15m gable roof"`
- **THEN** the card SHALL render a processing overlay in the image area containing a CSS-animated spinner and the text "Generating truss structure...". The `<img>` element SHALL NOT be visible. The card ID (`#N`) and prompt text "10x15m gable roof" SHALL still be visible.

#### Scenario: Processing entry does not open modal on click
- **WHEN** the user clicks on the processing overlay of a design entry with `status: "processing"`
- **THEN** the modal SHALL NOT open. No modal overlay SHALL appear.

#### Scenario: Entry transitions from processing to complete
- **WHEN** a design entry transitions from `status: "processing"` to `status: "complete"` and `imageUrl` changes from `"/design-gable.svg"` to the resolved image
- **THEN** the processing overlay SHALL disappear and the `<img>` element SHALL become visible with the updated `src` (provided all parameters are filled; otherwise the placeholder image is shown).

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

## ADDED Requirements

### Requirement: design-in-progress.svg placeholder image file

A static SVG file at `public/design-in-progress.svg` SHALL exist. The SVG SHALL display "Design In Progress" text centered within the image area, with styling consistent with the existing design card aesthetic (muted colors, similar dimensions to other design images).

#### Scenario: Placeholder SVG file exists

- **WHEN** the application checks for `public/design-in-progress.svg`
- **THEN** the file SHALL exist and be a valid SVG

#### Scenario: Placeholder SVG renders in browser

- **WHEN** an `<img>` element has `src="/design-in-progress.svg"`
- **THEN** it SHALL render a visible image containing the text "Design In Progress"
