## ADDED Requirements

### Requirement: Next.js webpack config disables Node.js built-in imports for client bundle
`next.config.ts` SHALL include `webpack.resolve.fallback` entries that set `fs` and `path` to `false`. This prevents Three.js and the CAD viewer library from attempting Node.js-only imports during client-side bundling.

#### Scenario: webpack config includes fs and path fallbacks
- **WHEN** `next.config.ts` is read
- **THEN** it SHALL contain `resolve.fallback` with both `fs: false` and `path: false`

#### Scenario: No SSR crash from Three.js imports
- **WHEN** `pnpm build` is run
- **THEN** the build SHALL complete without "Module not found" errors for `fs` or `path` originating from `@mlightcad/cad-simple-viewer` or its Three.js dependency

### Requirement: Dev server starts without worker loading errors
After all environment changes are applied, `pnpm dev` SHALL start successfully and the browser console SHALL show no 404 errors for worker files under `/workers/`.

#### Scenario: Dev server starts cleanly
- **WHEN** `pnpm dev` is run
- **THEN** the dev server SHALL start without build or compilation errors

#### Scenario: No 404s on worker files
- **WHEN** the application is loaded in a browser and the Network tab is inspected
- **THEN** no request to `/workers/*.js` SHALL return HTTP 404
