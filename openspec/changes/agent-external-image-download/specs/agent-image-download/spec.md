## Purpose

Provides a backend agent tool that downloads the preset test image from the `/api/test-image` route to a server-side temporary directory and returns the browser-accessible URL for use in a design entry.

## ADDED Requirements

### Requirement: httpx dependency is added to agent
The `httpx` package SHALL be added to the agent's dependencies in `agent/pyproject.toml`.

#### Scenario: httpx is importable in agent code
- **WHEN** `cd agent && python -c "import httpx"` is run
- **THEN** the command SHALL exit zero without errors.

### Requirement: download_test_image agent tool downloads the test image
The agent SHALL expose a tool named `download_test_image` registered with `@agent.tool` in `agent/src/agent.py`. The tool SHALL download the image from `http://localhost:3000/api/test-image` using `httpx.AsyncClient`, save the response body to `tmp/downloaded-images/test-image-<epoch-millis>.png` (relative to the project root), and return the browser-accessible URL string `/api/serve-image/test-image-<epoch-millis>.png`.

The project root directory SHALL be computed as `Path(__file__).resolve().parent.parent.parent` (i.e., three levels up from `agent/src/agent.py`).

The `tmp/downloaded-images/` directory SHALL be created automatically if it does not exist (using `mkdir(parents=True, exist_ok=True)`).

#### Scenario: Tool downloads and returns serveable URL
- **WHEN** the agent calls `download_test_image` and the Next.js app is running on `localhost:3000`
- **THEN** a file named `test-image-<timestamp>.png` SHALL exist in `tmp/downloaded-images/` with the exact binary contents of `tmp/test-assets/test-image.png`
- **AND** the tool SHALL return a string matching the pattern `/api/serve-image/test-image-<timestamp>.png`.

#### Scenario: Downloaded file matches source
- **WHEN** the tool completes successfully
- **THEN** the SHA-256 hash of `tmp/downloaded-images/test-image-<timestamp>.png` SHALL match the SHA-256 hash of `tmp/test-assets/test-image.png`.

### Requirement: download_test_image handles download failure gracefully
If the HTTP request to `http://localhost:3000/api/test-image` fails (non-200 status, connection error, or timeout), the tool SHALL return an error string starting with `"Error:"` describing the failure. The tool SHALL NOT create any file in `tmp/downloaded-images/` on failure.

#### Scenario: Server unreachable returns error string
- **WHEN** the agent calls `download_test_image` and the Next.js app is not running on `localhost:3000`
- **THEN** the tool SHALL return a string starting with `"Error:"`
- **AND** no new file SHALL be created in `tmp/downloaded-images/`.

#### Scenario: Non-200 status returns error string
- **WHEN** the agent calls `download_test_image` and the route returns HTTP 404
- **THEN** the tool SHALL return a string starting with `"Error:"` and including the status code.

### Requirement: System prompt includes download_test_image instructions
The agent's `system_prompt` in `agent/src/agent.py` SHALL include an instruction for the `download_test_image` tool. The instruction SHALL describe:
- That the tool downloads the test image to a temp directory
- That the tool returns a URL the agent can pass to `modify_design_entry` via the `image_url` parameter
- That after calling `download_test_image`, the agent SHALL call `modify_design_entry` with the returned URL to display the image

#### Scenario: System prompt references download_test_image
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL contain the text `download_test_image`.

#### Scenario: System prompt instructs agent to chain download with modify
- **WHEN** `agent/src/agent.py` is inspected for the `system_prompt` string
- **THEN** the prompt SHALL describe a workflow where `download_test_image` is called first, then `modify_design_entry` is called with the returned URL.

### Requirement: Agent code passes lint and type checking
The modified `agent/src/agent.py` SHALL pass `cd agent && python -m ruff check .` and `cd agent && python -m mypy .` with zero errors.

#### Scenario: Ruff check passes
- **WHEN** `cd agent && python -m ruff check .` is run
- **THEN** the command SHALL exit zero with no errors.

#### Scenario: Mypy check passes
- **WHEN** `cd agent && python -m mypy .` is run
- **THEN** the command SHALL exit zero with no errors.
