## 1. Package Installation

- [ ] 1.1 Install `@mlightcad/cad-simple-viewer` via `pnpm add @mlightcad/cad-simple-viewer`. Verify `pnpm install` completes with no peer dependency warnings related to React, Vue, or other frameworks. Run `pnpm build` to confirm the Next.js production build still succeeds with the new dependency in `node_modules`.
  - **Done when:** `cat package.json | jq '.dependencies[" @mlightcad/cad-simple-viewer"]'` returns a version string, `pnpm build` exits zero, and no peer dep warnings appear during install.

## 2. Web Worker Assets

- [ ] 2.1 Create `scripts/copy-cad-workers.mjs` that discovers worker JS files inside `node_modules/@mlightcad/` using a dynamic glob (e.g., `**/*worker*.js` or `**/*-worker.js`), copies them to `public/workers/`, and exits non-zero with a descriptive error if no worker files are found. Then wire the script into `package.json` as part of the `postinstall` lifecycle (chaining with the existing `install:agent` script). Run `pnpm install` to trigger the postinstall and verify worker files appear in `public/workers/`.
  - **Done when:** `public/workers/` contains at least one `.js` worker file, `node scripts/copy-cad-workers.mjs` exits zero, and running it when `node_modules/@mlightcad/` contains no matching worker files exits non-zero with an error message.

## 3. SSR Configuration and Verification

- [ ] 3.1 Add `webpack.resolve.fallback: { fs: false, path: false }` to `next.config.ts` inside the existing config object. Run `pnpm build` to verify no "Module not found" errors for `fs` or `path`. Run `pnpm dev`, open the application in a browser, and confirm the dev server starts without errors and no HTTP 404 responses appear for requests to `/workers/*.js`.
  - **Done when:** `next.config.ts` contains the fallback entries, `pnpm build` exits zero, `pnpm dev` starts without build errors, and worker files under `/workers/` return HTTP 200 when requested.
