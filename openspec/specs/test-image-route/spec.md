## Purpose

Provides a Next.js API route that serves a single preset PNG image file, simulating an external image source for testing the agent's download-to-display pipeline.

## Requirements

### Requirement: Test image asset exists on disk
A PNG image file SHALL exist at `tmp/test-assets/test-image.png`. The file SHALL be a valid PNG image, smaller than 50 KB.

#### Scenario: Test image file is present
- **WHEN** the filesystem is checked for `tmp/test-assets/test-image.png`
- **THEN** the file SHALL exist and SHALL be a valid PNG image (binary header starts with the PNG magic bytes).

#### Scenario: Test image file is under size limit
- **WHEN** the file size of `tmp/test-assets/test-image.png` is measured
- **THEN** the size SHALL be less than 50 KB.

### Requirement: /api/test-image route serves the preset PNG
A Next.js API route at `src/app/api/test-image/route.ts` SHALL handle GET requests to `/api/test-image`. The route SHALL read `tmp/test-assets/test-image.png` from the project root directory, set the `Content-Type` header to `image/png`, and return the file contents as the response body with HTTP status 200.

The route SHALL compute the project root directory using `process.cwd()` (the Next.js working directory) rather than a hardcoded absolute path.

#### Scenario: GET /api/test-image returns the PNG image
- **WHEN** a GET request is sent to `/api/test-image`
- **THEN** the response SHALL have HTTP status 200, `Content-Type: image/png`, and the response body SHALL be the exact binary contents of `tmp/test-assets/test-image.png`.

#### Scenario: Image is renderable in a browser
- **WHEN** an `<img src="/api/test-image">` element is rendered in the browser
- **THEN** the image SHALL display without errors and SHALL match the content of `tmp/test-assets/test-image.png`.

### Requirement: /api/test-image returns 404 when image file is missing
If the file `tmp/test-assets/test-image.png` does not exist when the route is called, the route SHALL return HTTP status 404 with a JSON body `{ "error": "Test image not found" }`.

#### Scenario: Missing test image file returns 404
- **WHEN** a GET request is sent to `/api/test-image` and `tmp/test-assets/test-image.png` does not exist
- **THEN** the response SHALL have HTTP status 404 and a JSON body containing `"error": "Test image not found"`.

### Requirement: /api/serve-image/[filename] route serves downloaded images
A Next.js API route at `src/app/api/serve-image/[filename]/route.ts` SHALL handle GET requests to `/api/serve-image/<filename>`. The route SHALL read the file from `tmp/downloaded-images/<filename>` and return it with the correct `Content-Type` header based on the file extension (`.png` → `image/png`, `.jpg`/`.jpeg` → `image/jpeg`, `.svg` → `image/svg+xml`).

The route SHALL validate that `filename` contains only alphanumeric characters, hyphens, underscores, and dots. If the filename contains `..`, `/`, or `\`, the route SHALL return HTTP 403 with `{ "error": "Invalid filename" }`.

If the file does not exist, the route SHALL return HTTP 404 with `{ "error": "Image not found" }`.

#### Scenario: Serve a downloaded PNG image
- **WHEN** a GET request is sent to `/api/serve-image/test-image-1234567890.png` and the file `tmp/downloaded-images/test-image-1234567890.png` exists
- **THEN** the response SHALL have HTTP status 200, `Content-Type: image/png`, and the response body SHALL be the exact binary contents of that file.

#### Scenario: Reject path traversal in filename
- **WHEN** a GET request is sent to `/api/serve-image/..%2Fetc%2Fpasswd`
- **THEN** the response SHALL have HTTP status 403 and a JSON body containing `"error": "Invalid filename"`.

#### Scenario: File not found returns 404
- **WHEN** a GET request is sent to `/api/serve-image/nonexistent.png` and the file does not exist in `tmp/downloaded-images/`
- **THEN** the response SHALL have HTTP status 404 and a JSON body containing `"error": "Image not found"`.
