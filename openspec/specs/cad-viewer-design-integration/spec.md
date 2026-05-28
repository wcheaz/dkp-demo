## Purpose

The CAD Viewer Design Integration capability handles the integration of the CadViewer component into the DesignComponent, including dynamic importing for SSR safety, DXF download functionality, and DXF generation status indication.

## Requirements

### Requirement: DesignComponent renders CadViewer for entries with dxfContent

In `src/components/design-component.tsx`, for a completed design entry (`status !== "processing"`) where all parameters are filled and `entry.dxfContent` is a non-empty, non-null string, the component SHALL render the `<CadViewer>` component instead of the `<img>` element. The `CadViewer` SHALL receive `dxfContent={entry.dxfContent}` as a prop. The viewer SHALL be rendered in the same visual position and with the same dimensions (`w-[55%] h-[27vh]`) as the existing `<img>` element it replaces.

#### Scenario: Entry with dxfContent renders CadViewer
- **WHEN** the `designs` array contains one entry with `status: "complete"`, all parameters filled, `imageUrl: "/design-gable.svg"`, and `dxfContent: "base64string"`
- **THEN** the component SHALL render `<CadViewer dxfContent="base64string" />` in the image area
- **AND** SHALL NOT render an `<img>` element with `src="/design-gable.svg"`

#### Scenario: Entry without dxfContent renders image
- **WHEN** the `designs` array contains one entry with `status: "complete"`, all parameters filled, `imageUrl: "/design-gable.svg"`, and `dxfContent: undefined`
- **THEN** the component SHALL render `<img src="/design-gable.svg" />` in the image area (unchanged behavior)
- **AND** SHALL NOT render `<CadViewer>`

#### Scenario: Entry with null or empty dxfContent renders image
- **WHEN** the `designs` array contains one entry with `status: "complete"`, all parameters filled, and `dxfContent: null` or `dxfContent: ""`
- **THEN** the component SHALL render `<img>` (unchanged behavior)

### Requirement: CadViewer is dynamically imported for SSR safety

The `<CadViewer>` component SHALL be imported in `design-component.tsx` using `next/dynamic` with `{ ssr: false }`. This ensures the component and its Three.js/WebGL dependencies are never included in the server-side bundle.

#### Scenario: CadViewer dynamic import prevents SSR
- **WHEN** `next build` runs
- **THEN** the build SHALL succeed without errors related to Three.js, WebGL, or missing browser APIs
- **AND** `@mlightcad/cad-simple-viewer` SHALL NOT appear in the server-side bundle

#### Scenario: CadViewer loads in browser
- **WHEN** the page is loaded in a browser and a design entry has `dxfContent`
- **THEN** the `CadViewer` component SHALL load dynamically and render the DXF viewer

### Requirement: Download DXF button appears for entries with dxfContent

For design entries with a non-empty `dxfContent` field, the component SHALL render a "Download DXF" button below or beside the viewer area. The button SHALL be an `<a>` element with:
- `href` set to a Blob URL created from the decoded base64 DXF content (MIME type `application/dxf`)
- `download="design-{id}.dxf"` attribute (where `{id}` is the entry's `id`)
- Visible text label "Download DXF"

The Blob URL SHALL be created when the entry is rendered and revoked when the component unmounts or the entry is removed.

#### Scenario: Download button renders for entry with dxfContent
- **WHEN** a design entry has `dxfContent: "base64string"` and `id: 1`
- **THEN** a "Download DXF" button SHALL be rendered with `download="design-1.dxf"`
- **AND** clicking the button SHALL trigger a file download of the decoded DXF content

#### Scenario: Download button absent for entry without dxfContent
- **WHEN** a design entry has `dxfContent: undefined`
- **THEN** no "Download DXF" button SHALL be rendered

#### Scenario: Blob URL is revoked on cleanup
- **WHEN** a design entry with `dxfContent` is removed from the `designs` array
- **THEN** the Blob URL for that entry's DXF content SHALL be revoked via `URL.revokeObjectURL()`

### Requirement: DXF generation status indicator shows while dxfContent is absent on completed entry

For a completed design entry with all parameters filled but `dxfContent` is undefined or null, the component SHALL show a brief status indicator: a small spinner with text "Generating CAD drawing..." below the existing design image. This indicator SHALL disappear once `dxfContent` becomes a non-empty string.

#### Scenario: Status indicator shows for completed entry without dxfContent
- **WHEN** a design entry has `status: "complete"`, all parameters filled, and `dxfContent: undefined`
- **THEN** the component SHALL show the existing `<img>` plus a "Generating CAD drawing..." indicator below it

#### Scenario: Status indicator hides when dxfContent arrives
- **WHEN** a design entry transitions from `dxfContent: undefined` to `dxfContent: "base64string"`
- **THEN** the "Generating CAD drawing..." indicator SHALL disappear
- **AND** the `<CadViewer>` SHALL render in place of the `<img>`
