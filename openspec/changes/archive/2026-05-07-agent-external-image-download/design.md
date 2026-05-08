## Context

The application is a Next.js 16 frontend with a Python PydanticAI backend communicating via the AG-UI protocol through CopilotKit. The frontend renders design entries (image + prompt text) in a `DesignComponent`. Currently, all images are static SVGs in `public/`, and the `modify_design_entry` frontend tool accepts only a hardcoded whitelist of two filenames.

This change adds a test pipeline: a Next.js route serves a preset image, the Python agent downloads it to a temp directory, and the agent then updates a design entry to display that downloaded image. This validates the agent's ability to handle an async download-to-serve workflow before integrating real external image sources.

Key constraints:
- Both the Next.js app and Python agent run on the same machine (localhost).
- The `modify_design_entry` tool currently validates `image_name` against `ALLOWED_IMAGES = ["design-alpha.svg", "design-beta.svg"]`.
- The `DesignEntry.imageUrl` field already accepts any string — no type changes needed.
- The Python agent has no HTTP client library in its current dependencies (no `httpx`, `aiohttp`, or `requests`).

## Goals / Non-Goals

**Goals:**
- Add a Next.js API route that serves a single preset PNG image.
- Add a Python agent tool that downloads the image from that route to a server-side temp directory.
- Make the downloaded image accessible to the browser so it can render in a `DesignComponent` card.
- Allow the agent to call `modify_design_entry` (or equivalent) with the URL of the downloaded image.
- Validate that the agent can complete the full download-to-display flow in one or two turns.

**Non-Goals:**
- Production image pipeline — this is a test/scaffold only.
- Multiple images, image upload, image transformation, or user-provided images.
- Persistent storage or cleanup scheduling for downloaded images.
- Authentication or authorization on any new routes.
- Changing the default `add_design_entry` placeholder behavior (`"/next.svg"`).

## Decisions

### D1: HTTP client library — `httpx`

**Decision**: Use `httpx` for the Python agent's image download.

**Rationale**: `httpx` is async-native (compatible with `async def` PydanticAI tools), supports streaming responses for binary data, and is the standard HTTP client for the FastAPI/Starlette ecosystem already used in this project.

**Alternatives considered**:
- `aiohttp`: Heavier, more boilerplate, less idiomatic alongside FastAPI.
- `requests`: Sync-only — would block the async event loop in a PydanticAI tool.
- `urllib` (stdlib): No async support, verbose API for binary downloads.

### D2: Shared temp directory for downloaded images

**Decision**: Use a shared directory `tmp/downloaded-images/` at the project root. The Python agent writes downloaded files here. A new Next.js API route reads from this directory.

**Rationale**: Both services run on the same host. A shared directory is the simplest mechanism with no additional infrastructure. The `tmp/` prefix makes it clear these are non-production, non-committed files (already `.gitignored` if `tmp/` is in `.gitignore`).

**Alternatives considered**:
- Write to `public/`: Would require Next.js restart or cache invalidation; pollutes the committed static assets.
- In-memory serving via agent route: The Python agent serves on port 8000 and is not directly accessible from the browser (the frontend proxies through CopilotKit). Adding a direct image-serving endpoint on the agent would require CORS config and bypass the standard architecture.
- Base64 data URIs: Would work for small images but bloat the `imageUrl` field and the serialized state. Not a pattern to establish.

### D3: New Next.js API route `/api/serve-image/[filename]` for serving downloaded images

**Decision**: Add a Next.js API route that reads a file from `tmp/downloaded-images/` by filename and returns it with the correct `Content-Type` header.

**Rationale**: This gives the browser a stable URL to use as `<img src>`. The route validates that the filename does not contain path traversal characters (`..`, `/`). It returns a 404 if the file does not exist.

**Alternatives considered**:
- Next.js rewrites to a static file server: More complex configuration for no benefit in a test route.
- Symlinks from `public/`: Fragile, platform-dependent, requires manual setup.

### D4: Extend `modify_design_entry` to accept dynamic image URLs

**Decision**: Add a new optional parameter `image_url` (string) to `modify_design_entry`. When provided, it sets `imageUrl` directly — bypassing the `ALLOWED_IMAGES` whitelist. The existing `image_name` parameter continues to work as before (validated against the whitelist).

**Rationale**: This preserves backward compatibility with the existing two-SVG workflow while allowing the agent to set any URL (including `/api/serve-image/<filename>`). The alternative of a separate tool was rejected because `modify_design_entry` already handles the state update logic — adding a parameter is simpler than duplicating it.

**Alternatives considered**:
- New frontend tool `set_design_image_url`: Duplicates state mutation logic from `modify_design_entry`.
- Expanding `ALLOWED_IMAGES` dynamically: Would require a mutable registry and loses the safety of a fixed whitelist for the static SVGs.
- Removing the whitelist entirely: Too permissive for the existing static image flow.

### D5: Preset test image format — small PNG

**Decision**: Place a single small PNG file (approximately 100×100 pixels, < 10 KB) at `tmp/test-assets/test-image.png` and serve it via `/api/test-image`.

**Rationale**: PNG is a realistic format for external images (as opposed to SVG, which is already covered). A small file keeps the test fast. The file lives outside `public/` to reinforce that it is a test asset, not a production static file.

**Alternatives considered**:
- JPEG: Also reasonable, but PNG is lossless and simpler to generate programmatically.
- Large image: Would slow down the test loop without adding value.

### D6: Agent tool returns the serveable URL, not the filesystem path

**Decision**: The `download_test_image` tool saves the file to `tmp/downloaded-images/<unique-name>.png` and returns the browser-accessible URL `/api/serve-image/<unique-name>` rather than the filesystem path.

**Rationale**: The agent needs to pass a URL to `modify_design_entry.image_url`, which becomes `<img src>`. Returning the serveable URL directly avoids the agent needing to know the URL-construction convention.

### D7: Unique filenames via timestamp

**Decision**: Generate unique filenames using a timestamp pattern: `test-image-<epoch-millis>.png`.

**Rationale**: Simple, deterministic, no external dependencies. For this test scaffold, collisions are not a concern (single-user dev environment).

**Alternatives considered**:
- UUID: More robust but unnecessary for a test route.
- Sequential counter: Requires shared state across tool calls.

## Risks / Trade-offs

- **[Shared filesystem coupling]** The Python agent and Next.js app must agree on the `tmp/downloaded-images/` path. In containerized deployments with separate containers, this directory would not be shared. → Mitigation: This is a test-only change. Production external-image support would use a different architecture (e.g., object storage).

- **[No cleanup]** Downloaded images accumulate in `tmp/downloaded-images/` with no automatic cleanup. → Mitigation: The directory is in `tmp/` which is typically cleared on restart. For test purposes this is acceptable. Add a cleanup task if needed later.

- **[Path traversal]** The `/api/serve-image/[filename]` route must validate filenames to prevent directory traversal. → Mitigation: Reject any filename containing `..`, `/`, or `\`. Only allow alphanumeric, hyphens, underscores, and dots.

- **[Race condition on download]** If the agent calls `modify_design_entry` before the file is fully written, the serve route could return 404. → Mitigation: The `download_test_image` tool writes the file completely before returning. The agent does not call `modify_design_entry` until the tool returns successfully.

- **[New Python dependency]** Adding `httpx` to the agent's dependencies. → Mitigation: `httpx` is a well-maintained, widely-used library with no heavy transitive dependencies.

## Open Questions

None — all design decisions are resolved for this test scaffold. Production external-image support would require revisiting shared storage, cleanup, and authentication.
