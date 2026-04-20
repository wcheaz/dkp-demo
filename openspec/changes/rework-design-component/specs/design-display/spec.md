## ADDED Requirements

### Requirement: DesignComponent renders a scrollable list of design entries
The `DesignComponent` SHALL accept an `AgentState` containing a `designs` array of `DesignEntry` objects. Each `DesignEntry` SHALL have an `imageUrl` (string) and a `promptText` (string). The component SHALL render one card per entry inside a scrollable container. Multiple cards SHALL be visible simultaneously. The scrollable container SHALL use `overflow-y: auto` so the user can scroll through the design history. Each card SHALL contain an `<img>` element with `src` set to the entry's `imageUrl` and a text element displaying the entry's `promptText`.

#### Scenario: Empty state when no designs exist
- **WHEN** the `designs` array on `AgentState` is empty or undefined
- **THEN** the component SHALL display an empty-state message indicating no designs are available, and SHALL render zero design cards.

#### Scenario: Single design entry displayed
- **WHEN** the `designs` array contains one `DesignEntry` with `imageUrl` set to `"tmp/next.svg"` and `promptText` set to `"Draw a flowchart of user login"`
- **THEN** the component SHALL render exactly one card containing an `<img>` element whose `src` attribute equals `"tmp/next.svg"` and a text element containing `"Draw a flowchart of user login"`.

#### Scenario: Multiple design entries displayed in order with scroll
- **WHEN** the `designs` array contains five entries in order: A, B, C, D, E
- **THEN** the component SHALL render five cards in the same order inside a scrollable container, each showing its own image and prompt text. At least two cards SHALL be visible without scrolling.

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
`AgentState` in `src/lib/types.ts` SHALL define a `designs` field of type `DesignEntry[]`. `DesignEntry` SHALL be an exported interface with `imageUrl: string` and `promptText: string`. The old `procurement_codes`-related types and `your_data` field SHALL be removed from `AgentState`.

#### Scenario: AgentState type compiles with designs field
- **WHEN** TypeScript compilation is run on `src/lib/types.ts`
- **THEN** the file SHALL compile without errors and `AgentState` SHALL have exactly one field: `designs: DesignEntry[]`.

#### Scenario: DesignEntry has required fields
- **WHEN** a `DesignEntry` object is created with `{ imageUrl: "tmp/next.svg", promptText: "test prompt" }`
- **THEN** the object SHALL satisfy the `DesignEntry` interface without TypeScript errors.

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

### Requirement: Test images resolve to tmp/next.svg
During testing, all `DesignEntry` instances SHALL have their `imageUrl` set to `"tmp/next.svg"`. This ensures deterministic rendering without depending on external image generation.

#### Scenario: Test entry uses tmp/next.svg
- **WHEN** a test creates a `DesignEntry` with `imageUrl: "tmp/next.svg"`
- **THEN** the rendered `<img>` element SHALL have `src="tmp/next.svg"` and the file `tmp/next.svg` SHALL exist in the repository.
