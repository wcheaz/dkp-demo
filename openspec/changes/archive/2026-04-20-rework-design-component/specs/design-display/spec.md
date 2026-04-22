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
