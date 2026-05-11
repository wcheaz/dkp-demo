## Purpose

Extends the agent's ability to display images in design entries so it can reference externally-sourced images (images downloaded at runtime via `download_test_image`) rather than only the hardcoded static SVG filenames from the whitelist.

## Requirements

### Requirement: Agent can display downloaded image in a design entry
The end-to-end workflow SHALL allow the agent to: (1) call `download_test_image` to download an image, (2) receive a serveable URL, (3) call `modify_design_entry` with the URL, and (4) have the image render in the `DesignComponent`.

#### Scenario: End-to-end download and display
- **WHEN** the user asks the agent to show an external image
- **THEN** the agent SHALL call `download_test_image`, receive a URL matching `/api/serve-image/test-image-*.png`, and call `modify_design_entry` with `image_url` set to that URL
- **AND** the `DesignComponent` SHALL render an `<img>` element whose `src` attribute equals the returned URL
- **AND** the image SHALL load and display without errors in the browser.

#### Scenario: Downloaded image URL renders in DesignComponent
- **WHEN** a `DesignEntry` has `imageUrl` set to `/api/serve-image/test-image-1234567890.png` and that file exists in `tmp/downloaded-images/`
- **THEN** the `DesignComponent` SHALL render the image successfully with the correct content.

### Requirement: Downloaded image is viewable via modal enlargement
Clicking the downloaded image in the `DesignComponent` card SHALL open the modal overlay showing the image at enlarged size, identical to the behavior for static SVG images.

#### Scenario: Click downloaded image opens modal
- **WHEN** a design entry has `imageUrl` set to `/api/serve-image/test-image-1234567890.png` and the user clicks the image
- **THEN** the modal SHALL open with `src="/api/serve-image/test-image-1234567890.png"` at the enlarged size (up to 90vw × 90vh).

### Requirement: Frontend TypeScript compilation passes
The modified `src/app/page.tsx` SHALL pass `npx tsc --noEmit` with zero errors.

#### Scenario: TypeScript check passes
- **WHEN** `npx tsc --noEmit` is run from the project root
- **THEN** the command SHALL exit zero with no errors.

### Requirement: Frontend lint passes
The modified `src/app/page.tsx` SHALL pass `npm run lint` with zero errors.

#### Scenario: Lint check passes
- **WHEN** `npm run lint` is run from the project root
- **THEN** the command SHALL exit zero with no errors.
