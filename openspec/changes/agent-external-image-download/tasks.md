## 1. Test Assets and Directory Setup

- [ ] 1.1 Create test image asset and directories. Create `tmp/test-assets/` and `tmp/downloaded-images/` directories. Generate a small valid PNG file (100×100 pixels, < 50 KB) and save it to `tmp/test-assets/test-image.png`. Verify the file exists and has a PNG header. Ensure both directories are listed in `.gitignore` under `tmp/`.

## 2. Next.js API Routes

- [ ] 2.1 Implement `/api/test-image` route. Create `src/app/api/test-image/route.ts` that reads `tmp/test-assets/test-image.png` using `process.cwd()` as the base, sets `Content-Type: image/png`, and returns the file contents. Return 404 with `{ "error": "Test image not found" }` if the file is missing. Verify by running `curl http://localhost:3000/api/test-image` and confirming 200 with PNG content.
- [ ] 2.2 Implement `/api/serve-image/[filename]` route. Create `src/app/api/serve-image/[filename]/route.ts` that reads files from `tmp/downloaded-images/<filename>`. Validate filename contains only `[a-zA-Z0-9._-]`; return 403 for path traversal attempts (`..`, `/`, `\`). Return 404 if the file does not exist. Set `Content-Type` based on extension (`.png` → `image/png`). Verify by placing a test file in `tmp/downloaded-images/`, requesting `/api/serve-image/<filename>`, and confirming correct response.

## 3. Frontend Tool Update

- [ ] 3.1 Add `image_url` parameter to `modify_design_entry`. In `src/app/page.tsx`, add an optional `image_url` (string) parameter to the `modify_design_entry` frontend tool. When `image_url` is provided, set `imageUrl` directly without validating against `ALLOWED_IMAGES`. When both `image_name` and `image_url` are provided, `image_url` takes precedence. Update the "at least one required" error to include `image_url`. Update the tool's parameter description to document `image_url`. Verify by running `npx tsc --noEmit` and `npm run lint` with zero errors.
- [ ] 3.2 Update agent system prompt for `image_url` parameter. In `agent/src/agent.py`, update the `system_prompt` to document the new `image_url` parameter on `modify_design_entry`, explaining that `image_url` should be used for dynamically downloaded images (e.g., `/api/serve-image/...`) while `image_name` is for static preset images. Verify by running `cd agent && python -m ruff check . && python -m mypy .` with zero errors.

## 4. Backend Agent Tool

- [ ] 4.1 Add `httpx` dependency and implement `download_test_image` tool. Add `httpx` to `agent/pyproject.toml` dependencies and run `cd agent && uv sync`. In `agent/src/agent.py`, add a new `@agent.tool` function `download_test_image` that: uses `httpx.AsyncClient` to GET `http://localhost:3000/api/test-image`, saves the response body to `tmp/downloaded-images/test-image-<epoch-millis>.png` (using `Path(__file__).resolve().parent.parent.parent` for the project root), creates `tmp/downloaded-images/` if missing, and returns the URL string `/api/serve-image/test-image-<epoch-millis>.png`. On failure (non-200, connection error, timeout), return `"Error: <description>"` without creating a file. Verify by running `cd agent && python -m ruff check . && python -m mypy .` with zero errors.

## 5. System Prompt Integration

- [ ] 5.1 Add `download_test_image` instructions to system prompt. In `agent/src/agent.py`, append to the `system_prompt` a description of the `download_test_image` tool and a workflow instruction: call `download_test_image` first, then call `modify_design_entry` with the returned URL as `image_url`. Preserve all existing system prompt content. Verify the prompt contains both `download_test_image` and `image_url` strings. Verify by running `cd agent && python -m ruff check . && python -m mypy .` with zero errors.

## 6. End-to-End Verification

- [ ] 6.1 Verify end-to-end download-to-display workflow. Start both the Next.js app (`npm run dev`) and the Python agent (`scripts/run-agent.sh`). In the browser, trigger the agent to perform the download-and-display workflow (e.g., ask it to download and show the test image). Verify: (1) a file appears in `tmp/downloaded-images/`, (2) the agent calls `modify_design_entry` with the `/api/serve-image/...` URL, (3) the `DesignComponent` renders the image, (4) clicking the image opens the modal enlargement. Verify `npx tsc --noEmit`, `npm run lint`, `cd agent && python -m ruff check .`, and `cd agent && python -m mypy .` all pass with zero errors.
