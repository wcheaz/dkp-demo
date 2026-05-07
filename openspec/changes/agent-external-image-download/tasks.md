## 1. Test Assets, Directories, and Next.js Image Routes

Create the test image asset and both Next.js API routes (`/api/test-image` and `/api/serve-image/[filename]`) that the rest of the pipeline depends on.

- [ ] 1.1 Create test image asset, `.gitignore` entries, and both image-serving API routes.
  - Create directories `tmp/test-assets/` and `tmp/downloaded-images/`.
  - Generate a small valid PNG (100×100 px, < 50 KB) at `tmp/test-assets/test-image.png`. One approach: write a 1×1 white pixel PNG using a Node.js script (`Buffer.from([0x89,0x50,0x4e,0x47,...])`) or Python (`PIL`/`Pillow`), or create a minimal valid PNG manually. If no image library is available, copy an existing small PNG from the project and rename it.
  - Verify `tmp/*` is already in `.gitignore` (it is — do not add it again).
  - Create `src/app/api/test-image/route.ts`: reads `tmp/test-assets/test-image.png` using `process.cwd()` as base path, returns it with `Content-Type: image/png`, returns 404 with `{ "error": "Test image not found" }` if missing.
  - Create `src/app/api/serve-image/[filename]/route.ts`: reads from `tmp/downloaded-images/<filename>`, validates filename against `^[a-zA-Z0-9._-]+$` (reject `..`, `/`, `\` with 403 `{ "error": "Invalid filename" }`), sets `Content-Type` by extension (`.png` → `image/png`, `.jpg`/`.jpeg` → `image/jpeg`, `.svg` → `image/svg+xml`), returns 404 with `{ "error": "Image not found" }` if file missing.
  - **Done when**: Both route files exist. `tmp/test-assets/test-image.png` exists and has PNG magic bytes (starts with `\x89PNG`). `npx tsc --noEmit` exits zero. `npm run lint` exits zero (warnings are acceptable — ESLint exits 0 on warnings only).

## 2. Frontend Tool and Backend Agent Tool

Update `modify_design_entry` in `src/app/page.tsx` to accept dynamic image URLs, then add the `download_test_image` backend tool and update the agent system prompt in `agent/src/agent.py`. These all touch the same agent↔frontend contract and should be done together so the tool and its documentation stay consistent.

- [ ] 2.1 Extend `modify_design_entry` with `image_url` parameter, add `download_test_image` agent tool, and update system prompt.
  - **`src/app/page.tsx`**: Add optional `image_url` (string) parameter to `modify_design_entry`. When `image_url` is provided, set `imageUrl` directly — bypass `ALLOWED_IMAGES` validation. When both `image_name` and `image_url` are provided, `image_url` takes precedence. Update the "at least one required" error message to list `image_url` alongside `image_name` and `prompt_text`.
  - **`agent/pyproject.toml`**: Add `httpx` to dependencies, run `cd agent && uv sync`.
  - **`agent/src/agent.py`**: Add `import httpx` at the top with the other imports. Add `@agent.tool` async function `download_test_image` that uses `httpx.AsyncClient` to GET `http://localhost:3000/api/test-image`, saves the response body to `tmp/downloaded-images/test-image-<epoch-millis>.png` (project root via `Path(__file__).resolve().parent.parent.parent`), creates the directory if missing (`parents=True, exist_ok=True`), and returns the URL `/api/serve-image/test-image-<epoch-millis>.png`. On failure (non-200, connection error, timeout), return `"Error: <description>"` without creating any file. Use `int(time.time() * 1000)` for the epoch-millis timestamp (`time` is already imported).
  - **`agent/src/agent.py` system_prompt**: Append documentation for `download_test_image` (what it does, that it returns a serveable URL) and document the `image_url` parameter on `modify_design_entry` (use for dynamically downloaded images, while `image_name` is for static preset SVGs). Add a workflow instruction: call `download_test_image` first, then call `modify_design_entry` with the returned URL as `image_url`. Preserve all existing system prompt content.
  - **Done when**: The system prompt string in `agent.py` contains both `download_test_image` and `image_url`. The `modify_design_entry` tool handler in `page.tsx` accepts `image_url` and sets `imageUrl` without whitelist validation. `npx tsc --noEmit` exits zero. `npm run lint` exits zero. `cd agent && python -m ruff check .` exits zero. `cd agent && python -m mypy .` exits zero.

## 3. Quality Gate

Final verification across all changed files. This task runs after 1.1 and 2.1 are both complete.

**IMPORTANT — use these exact commands. Do NOT use `rtk lint` or `rtk tsc` wrappers:**
- `rtk lint` has a known bug where it fails to parse ESLint JSON output and exits code 2 even when there are zero errors. This causes an infinite loop. Always use `npm run lint` directly.
- ESLint warnings are acceptable — the command exits 0 on warnings. Only a non-zero exit code is a failure.

- [ ] 3.1 Run full quality gate across both frontend and backend.
  - Run `npx tsc --noEmit` — must exit zero.
  - Run `npm run lint` — must exit zero (warnings are expected and OK).
  - Run `cd agent && python -m ruff check .` — must exit zero.
  - Run `cd agent && python -m mypy .` — must exit zero.
  - **Done when**: All four commands exit zero. If any command exits non-zero, fix the issue and re-run all four. Stop and hand off if a command fails and the cause is unclear.

## Human Handoff

The following verification requires a running server and browser interaction. It is NOT a loop task — perform manually after the automated tasks above are complete.

- Start both the Next.js app (`npm run dev`) and the Python agent (`scripts/run-agent.sh`).
- In the browser, ask the agent to download and show the test image.
- Verify: (1) a file appears in `tmp/downloaded-images/`, (2) the agent calls `modify_design_entry` with a `/api/serve-image/...` URL, (3) the `DesignComponent` renders the downloaded image, (4) clicking the image opens the modal enlargement.
