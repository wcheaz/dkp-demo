## Why

The agent currently serves only hardcoded static SVGs (`design-alpha.svg`, `design-beta.svg`) from `public/` via a hardcoded `ALLOWED_IMAGES` whitelist in `modify_design_entry`. This change adds a test route that hosts a preset image, enabling the agent to download that image from an external source into a temporary server-side directory and then display it inside a `DesignComponent` card — validating that the agent can handle an asynchronous download-to-serve pipeline seamlessly (either by blocking its response until the download completes, or by sending a follow-up response with the image).

## What Changes

- Add a new Next.js API route (`/api/test-image`) that serves a single preset image file to the client.
- Add a new backend agent tool (`download_test_image`) that downloads the preset image from `/api/test-image` to a server-side temporary directory and returns the local file path.
- Update `modify_design_entry` (or introduce a new frontend tool) so the agent can set a `DesignEntry`'s `imageUrl` to the newly served image path after a download completes.
- Update the agent's system prompt to include instructions for the new download-to-display workflow.
- Place a single test image (e.g., a small PNG) in a location the API route can serve.

## Capabilities

### New Capabilities
- `test-image-route`: A Next.js API route that serves one preset image file at a stable URL, simulating an external image source for testing the agent's download capability.
- `agent-image-download`: A backend agent tool that downloads the preset image from the test route to a server-side temporary directory, returning the local path so the agent can reference it in a design entry.
- `design-entry-external-image`: Extends the agent's ability to create or modify design entries so it can reference externally-sourced images (images downloaded at runtime) rather than only hardcoded static SVG filenames from the whitelist.

### Modified Capabilities
- `design-entry-modify`: The `modify_design_entry` frontend tool's `ALLOWED_IMAGES` whitelist and/or `image_name` parameter handling must be extended to accept dynamically-served image URLs in addition to the existing hardcoded SVG filenames.

## Impact

- **Frontend** (`src/app/page.tsx`): `modify_design_entry` tool handler updated to accept dynamic image URLs or a new frontend tool added for external image display.
- **Backend** (`agent/src/agent.py`): New `download_test_image` agent tool added; system prompt updated with download-and-display instructions.
- **New API route** (`src/app/api/test-image/route.ts`): Serves a static test image file.
- **New test asset**: A small PNG image placed in the project for the API route to serve.
- **Types** (`src/lib/types.ts`): No structural changes needed — `DesignEntry.imageUrl` already accepts any string.
- **Dependencies**: The Python agent may need `httpx` or `aiohttp` for downloading images (check existing dependencies first).

## Non-goals

- This is a **test/scaffold** change — it validates the download-to-serve pipeline, not production image handling.
- No support for multiple images, image upload by users, or image processing/transformation.
- No persistent storage of downloaded images — temporary directory only, cleaned up on server restart.
- No changes to the existing `add_design_entry` tool's default behavior (placeholder `"/next.svg"` remains).
- No agent streaming/partial-response handling — the agent either blocks until the download completes or sends a second message after download.
- No authentication or authorization on the test image route.
