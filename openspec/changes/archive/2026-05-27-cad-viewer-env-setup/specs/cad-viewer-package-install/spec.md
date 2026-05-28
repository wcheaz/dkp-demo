## ADDED Requirements

### Requirement: cad-simple-viewer package is installed
The project SHALL have `@mlightcad/cad-simple-viewer` listed in `dependencies` in `package.json`. The installed version SHALL have no React, Vue, or other framework peer dependencies.

#### Scenario: Package appears in dependencies
- **WHEN** `cat package.json | jq '.dependencies[" @mlightcad/cad-simple-viewer"]'` is run
- **THEN** the output SHALL be a version string (not null)

#### Scenario: No framework peer dependency conflicts
- **WHEN** `pnpm install` is run
- **THEN** the command SHALL exit zero with no peer dependency warnings related to React or Vue

### Requirement: Next.js build succeeds with the new package
The Next.js production build SHALL succeed with `@mlightcad/cad-simple-viewer` installed and the webpack fallback configuration in place.

#### Scenario: Production build completes without errors
- **WHEN** `pnpm build` is run
- **THEN** the command SHALL exit zero and produce a `.next/` output directory

#### Scenario: No TypeScript errors from the new dependency
- **WHEN** `npx tsc --noEmit` is run
- **THEN** the command SHALL exit zero
