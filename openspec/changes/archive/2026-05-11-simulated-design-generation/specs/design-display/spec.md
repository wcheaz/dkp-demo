## Purpose

The Design Display capability provides a scrollable list of design entries with image preview and modal enlargement, driven by an `AgentState` containing a `designs` array.

## MODIFIED Requirements

### Requirement: DesignComponent renders a scrollable list of design entries
The `DesignComponent` SHALL accept an `AgentState` containing a `designs` array of `DesignEntry` objects and a `parameters` field of type `DesignParameters`. The component SHALL render a parameter display section above the scrollable design cards container (see `design-params-display` capability). Each `DesignEntry` SHALL have an `imageUrl` (string), a `promptText` (string), and a `status` field (`"processing" | "complete"`). The component SHALL render one card per entry inside a scrollable container. Multiple cards SHALL be visible simultaneously. The scrollable container SHALL use `overflow-y: auto` so the user can scroll through the design history. Each card SHALL contain an `<img>` element with `src` set to the entry's `imageUrl` and a text element displaying the entry's `promptText`.

For entries with `status: "processing"`, the card SHALL render a processing overlay covering the image area instead of the normal image. The overlay SHALL contain a CSS-animated spinner and the text "Generating truss structure...". The image SHALL be hidden during processing. The card ID (`#N`) and prompt text SHALL remain visible above and below the overlay. Clicking the overlay or the processing entry SHALL NOT open the modal.

For entries with `status: "complete"` (including the default), the card SHALL render normally as before — showing the image and allowing click-to-enlarge.

#### Scenario: Empty state when no designs exist
- **WHEN** the `designs` array on `AgentState` is empty or undefined
- **THEN** the component SHALL display an empty-state message indicating no designs are available, and SHALL render zero design cards. The parameter display section SHALL still render above the empty state.

#### Scenario: Single design entry displayed
- **WHEN** the `designs` array contains one `DesignEntry` with `imageUrl` set to `"tmp/next.svg"` and `promptText` set to `"Draw a flowchart of user login"` and `status` omitted (defaults to `"complete"`)
- **THEN** the component SHALL render exactly one card containing an `<img>` element whose `src` attribute equals `"tmp/next.svg"` and a text element containing `"Draw a flowchart of user login"`. No processing overlay SHALL be shown.

#### Scenario: Multiple design entries displayed in order with scroll
- **WHEN** the `designs` array contains five entries in order: A, B, C, D, E (all with `status: "complete"`)
- **THEN** the component SHALL render five cards in the same order inside a scrollable container, each showing its own image and prompt text. At least two cards SHALL be visible without scrolling.

#### Scenario: Processing entry shows overlay instead of image
- **WHEN** the `designs` array contains one entry with `status: "processing"`, `imageUrl: "/design-gable.svg"`, and `promptText: "10x15m gable roof"`
- **THEN** the card SHALL render a processing overlay in the image area containing a CSS-animated spinner and the text "Generating truss structure...". The `<img>` element SHALL NOT be visible. The card ID (`#N`) and prompt text "10x15m gable roof" SHALL still be visible.

#### Scenario: Processing entry does not open modal on click
- **WHEN** the user clicks on the processing overlay of a design entry with `status: "processing"`
- **THEN** the modal SHALL NOT open. No modal overlay SHALL appear.

#### Scenario: Entry transitions from processing to complete
- **WHEN** a design entry transitions from `status: "processing"` to `status: "complete"` and `imageUrl` changes from `"/design-gable.svg"` to the resolved image
- **THEN** the processing overlay SHALL disappear and the `<img>` element SHALL become visible with the updated `src`.

#### Scenario: Complete entry allows click-to-enlarge
- **WHEN** the user clicks on the `<img>` element of a design entry with `status: "complete"`
- **THEN** the modal SHALL open as per existing behavior (see modal requirement in base spec).
