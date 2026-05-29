## ADDED Requirements

### Requirement: User can click an inactive design to activate its live viewer
The `DesignComponent` SHALL maintain a user-controllable `activeViewerIndex` state (type `number`). When no user interaction has occurred, this index SHALL default to the last index in `designs` that has `dxfContent`. When the user clicks the viewer area of an inactive design card (one with `dxfContent` but where `index !== activeViewerIndex`), the component SHALL update `activeViewerIndex` to the clicked index. The previously active design SHALL stop rendering a live `CadViewer` and instead show a clickable overlay.

#### Scenario: Newest design is active by default
- **WHEN** the `designs` array contains three entries where entries at index 0 and 2 have `dxfContent` and entry at index 1 does not
- **THEN** `activeViewerIndex` SHALL be `2` (the last index with DXF content)
- **AND** only the design at index 2 SHALL render a live `CadViewer`

#### Scenario: Clicking an inactive design activates it
- **WHEN** `activeViewerIndex` is `2` and the user clicks the viewer area of the design at index `0` (which has `dxfContent`)
- **THEN** `activeViewerIndex` SHALL become `0`
- **AND** the design at index `0` SHALL render a live `CadViewer`
- **AND** the design at index `2` SHALL show a clickable overlay instead of a live viewer

#### Scenario: New design generation resets active viewer
- **WHEN** `activeViewerIndex` is `0` and a new design is appended to `designs` with `dxfContent`
- **THEN** `activeViewerIndex` SHALL reset to the new design's index (the last index with DXF content)

### Requirement: Inactive designs with DXF show a clickable overlay
Design entries that have `dxfContent` but are not at `activeViewerIndex` SHALL render a styled overlay div in place of the live `CadViewer`. The overlay SHALL display instructional text indicating the user can click to view the design. The overlay SHALL have `cursor: pointer` and cover the full viewer area. Clicking the overlay SHALL update `activeViewerIndex` to that entry's index.

#### Scenario: Inactive DXF design shows overlay with click prompt
- **WHEN** a design entry at index `0` has `dxfContent` and `activeViewerIndex` is `2`
- **THEN** the design at index `0` SHALL render a clickable overlay in the viewer area with instructional text
- **AND** the overlay SHALL have `cursor: pointer`

#### Scenario: Clicking overlay switches active viewer
- **WHEN** the user clicks the overlay on the inactive design at index `0`
- **THEN** `activeViewerIndex` SHALL become `0`
- **AND** the `CadViewer` SHALL mount for index `0`
- **AND** the design at index `2` (previously active) SHALL now show the overlay

#### Scenario: Design without DXF content is unaffected
- **WHEN** a design entry has no `dxfContent`
- **THEN** it SHALL NOT show the clickable overlay or a `CadViewer`, regardless of `activeViewerIndex`

### Requirement: CadViewer remounts on viewer switch via React key
When `activeViewerIndex` changes, the `CadViewer` component for the previously active design SHALL unmount (triggering `AcApDocManager.instance.destroy()` in its cleanup) and a new `CadViewer` SHALL mount for the newly active design. The component SHALL use `key={entry.id}` on `CadViewer` to force React remounting.

#### Scenario: Switching active viewer unmounts old and mounts new
- **WHEN** `activeViewerIndex` changes from `2` to `0`
- **THEN** the `CadViewer` for the design at index `2` SHALL unmount (calling `destroy()`)
- **AND** a new `CadViewer` SHALL mount for the design at index `0` with its `dxfContent`

#### Scenario: Only one CadViewer exists at a time
- **WHEN** there are three designs with `dxfContent` and `activeViewerIndex` is `1`
- **THEN** exactly one `CadViewer` component SHALL be mounted (for index `1`)
