## Context

The project is a Next.js 16 + React 19 app that generates roof truss designs as DXF files (via Python `ezdxf` on the agent backend). Currently, completed designs render as static SVG `<img>` elements in `src/components/design-component.tsx`. The next phase replaces that static display with an interactive CAD viewer.

This change (Phase 4a) covers only the build-environment preparation: installing the viewer package, provisioning its Web Worker dependencies as static assets, and configuring Next.js to handle the Three.js/WebGL SSR boundary. No React components or UI changes are included — those follow in Phase 4b.

### Current state

- `package.json` has no CAD viewer dependency.
- `next.config.ts` is minimal: `output: "standalone"`, `trailingSlash: false`, `productionBrowserSourceMaps: false`.
- `public/` contains SVGs and other static assets but no `workers/` directory.
- `DesignEntry.dxfContent` already exists on the TypeScript and Python models (added in Phase 3), but nothing renders it yet.

### Key constraint

`@mlightcad/cad-simple-viewer` is the framework-agnostic core of the `mlightcad/cad-viewer` monorepo. The full `@mlightcad/cad-viewer` package bundles Vue 3 and must NOT be used. `cad-simple-viewer` has no React/Vue peer deps.

## Goals / Non-Goals

**Goals:**

- `@mlightcad/cad-simple-viewer` installs cleanly via `pnpm add` with no peer dependency warnings.
- All Web Worker JS files required by the library are available under `public/workers/` and served as static assets.
- `next.config.ts` is configured so that Three.js/WebGL imports never execute server-side.
- `pnpm build` succeeds with the new dependency and config.
- `pnpm dev` starts without errors and worker files are reachable (no 404s).

**Non-Goals:**

- Creating a `<CadViewer>` React component (Phase 4b).
- Replacing the `<img>` in `design-component.tsx` (Phase 4b).
- Adding download buttons or status indicators (Phase 4b).
- Studying the example repo's initialization API in depth (that is a Phase 4b prerequisite).
- Any change to the agent backend or DXF generation logic.

## Decisions

### D1: Use `@mlightcad/cad-simple-viewer`, not `@mlightcad/cad-viewer`

**Choice:** `cad-simple-viewer` (the framework-agnostic core).
**Rationale:** The full `cad-viewer` package is a Vue 3 component that depends on Vue, Element Plus, and vue-i18n. Our app is React 19. The `cad-simple-viewer` package has no framework peer deps.
**Alternative:** Fork and wrap the Vue component — rejected due to framework incompatibility.

### D2: Web Worker provisioning via `postinstall` script

**Choice:** Add a Node.js script (`scripts/copy-cad-workers.mjs`) that copies worker files from `node_modules` to `public/workers/`, invoked by a `postinstall` script in `package.json`.
**Rationale:** The library requires Web Workers served as static files. They live inside `node_modules` after install and must be copied to `public/` so Next.js serves them. Automating via `postinstall` ensures every `pnpm install` produces correct state.
**Alternative:** Use `copy-webpack-plugin` to copy at build time — rejected because Next.js's webpack config is harder to extend for static asset copying, and `postinstall` is simpler and works for both dev and production builds.

### Worker file locations

The exact worker file paths inside `node_modules` will be determined empirically after `pnpm add` succeeds. The expected files are:

- `dxf-parser-worker.js` (or similar) — parses DXF content
- `dwg-parser-worker.js` (or similar) — parses DWG content (may not be needed but include for completeness)
- `mtext-renderer-worker.js` (or similar) — renders MTEXT entities

The `postinstall` script MUST discover these files dynamically (e.g., via glob inside `node_modules/@mlightcad/`) rather than hardcoding paths, because package updates may change internal file locations.

### D3: SSR safety via Turbopack resolve aliases in `next.config.ts`

**Choice:** Add `turbopack.resolveAlias: { fs: { browser: "" }, path: { browser: "" } }` to `next.config.ts`. Component-level dynamic import (`next/dynamic` with `ssr: false`) will be used in Phase 4b.
**Rationale:** Next.js 16 uses Turbopack by default for both dev (`next dev --turbopack`) and production builds. The traditional `webpack.resolve.fallback` has no effect under Turbopack. The `resolveAlias` approach maps `fs` and `path` to empty strings in the browser context, preventing Three.js and the CAD viewer from attempting Node.js-only imports. The `next/dynamic` approach is complementary and will be applied when the component is created.
**Alternative:** Use `webpack.resolve.fallback` — rejected because Next.js 16 defaults to Turbopack and ignores webpack fallbacks. Use `externals` to exclude the package from SSR entirely — rejected because it would prevent the import from resolving at all; `resolveAlias` is more surgical.

### D4: No changes to `serverExternalPackages`

**Choice:** Do NOT add `@mlightcad/cad-simple-viewer` to `serverExternalPackages`.
**Rationale:** The package should never run on the server. Adding it to `serverExternalPackages` would tell Next.js to keep it out of the server bundle, but since we never import it server-side, no configuration is needed here. The webpack fallbacks handle accidental transitive references.

## Risks / Trade-offs

- **Worker file paths may change across package versions** → Mitigated by using a dynamic glob-based discovery in the copy script rather than hardcoded paths. If the glob returns zero files, the script exits non-zero with a clear error message.
- **`cad-simple-viewer` may have undocumented Node.js imports** → Mitigated by `turbopack.resolveAlias` mapping `fs` and `path` to empty strings for the browser. If additional aliases are needed, they will be discovered during dev server testing and added incrementally.
- **Package may not be compatible with Next.js 16 / React 19 / pnpm** → Mitigated by verifying `pnpm build` succeeds as an explicit task. If it fails, we fall back to a version pin or alternative approach.
- **Worker files may be large** → Acceptable for a demo. Production use would consider CDN hosting, but that is out of scope.
