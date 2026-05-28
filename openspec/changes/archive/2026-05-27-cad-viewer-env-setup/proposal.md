## Why

The design card currently renders DXF output as a static `<img>`. Phase 4a prepares the frontend build environment so that `@mlightcad/cad-simple-viewer` — a browser-based DXF viewer — can be loaded and rendered inside a React component without SSR or bundling errors. Without this setup step, any attempt to integrate the viewer will fail at build time due to WebGL/Three.js server-side rendering and missing Web Worker assets.

## What Changes

- Add `@mlightcad/cad-simple-viewer` as a production dependency via `pnpm add`.
- Copy the library's required Web Worker files (DXF parser, DWG parser, MTEXT renderer) to `public/workers/` and add a `postinstall` script to automate this on every `pnpm install`.
- Configure `next.config.ts` with webpack fallbacks (`fs: false`, `path: false`) so Three.js-dependent code does not attempt Node.js imports during SSR.
- Verify that `pnpm build` and `pnpm dev` succeed with the new dependency and worker files in place.

## Capabilities

### New Capabilities
- `cad-viewer-package-install`: Installs `@mlightcad/cad-simple-viewer`, verifies the package has no React/Vue peer deps, and confirms the Next.js build succeeds.
- `cad-viewer-worker-assets`: Copies required Web Worker JS files from the installed package to `public/workers/` and adds a `postinstall` automation script so workers are always available after `pnpm install`.
- `cad-viewer-ssr-config`: Configures Next.js webpack fallbacks and documents the SSR-safety strategy so that Three.js/WebGL code never runs server-side.

### Modified Capabilities

_(None — no existing spec-level behavior changes.)_

## Impact

- **Dependencies**: New npm package `@mlightcad/cad-simple-viewer` (MIT, no React/Vue peer deps).
- **Build config**: `next.config.ts` gains `webpack.resolve.fallback` entries.
- **Scripts**: `package.json` gains or extends a `postinstall` script.
- **Static assets**: New `public/workers/` directory with 3+ worker JS files.
- **No runtime behavior change yet** — this change only prepares the environment; the React component and viewer integration follow in Phase 4b.
