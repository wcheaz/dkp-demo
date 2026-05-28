## ADDED Requirements

### Requirement: Web Worker files are copied to public/workers
All Web Worker JS files required by `@mlightcad/cad-simple-viewer` SHALL be present in `public/workers/` after `pnpm install` completes. The files SHALL be discoverable by a dynamic glob search inside `node_modules/@mlightcad/` — no file paths SHALL be hardcoded.

#### Scenario: Worker files exist after install
- **WHEN** `pnpm install` completes successfully
- **THEN** `public/workers/` SHALL contain at least one `.js` file matching a worker pattern (e.g., `*-worker.js` or `*.worker.js`)

#### Scenario: Worker files are servable as static assets
- **WHEN** `pnpm dev` is running and a request is made to `/workers/<filename>.js` for any file in `public/workers/`
- **THEN** the server SHALL respond with HTTP 200 and the file content

### Requirement: postinstall script automates worker file copying
`package.json` SHALL include a `postinstall` entry (or extend the existing one) that runs a Node.js script to copy worker files from `node_modules` to `public/workers/`. If no worker files are found, the script SHALL exit non-zero with a descriptive error message.

#### Scenario: postinstall runs the copy script
- **WHEN** `pnpm install` is run
- **THEN** the postinstall hook SHALL execute the worker copy script and the script SHALL exit zero

#### Scenario: Copy script exits non-zero when no workers found
- **WHEN** the copy script is run and the glob pattern inside `node_modules/@mlightcad/` matches zero worker files
- **THEN** the script SHALL exit non-zero and print an error message containing "cad-simple-viewer" and "worker"

### Requirement: Worker copy script is committed to the repository
The copy script (`scripts/copy-cad-workers.mjs`) SHALL be a committed file, not generated at runtime. It SHALL use Node.js built-in modules only (`fs`, `path`, `glob` via `fs/promises` or similar) — no additional dependencies.

#### Scenario: Copy script exists and is executable
- **WHEN** `node scripts/copy-cad-workers.mjs` is run after `pnpm install`
- **THEN** the script SHALL run without errors and `public/workers/` SHALL contain the worker files
