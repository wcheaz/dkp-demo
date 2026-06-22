## Context

The project is currently using CopilotKit packages version `1.60.2`. This change upgrades all `@copilotkit/*` packages to version `1.61.0` to import the latest stability improvements.

## Goals / Non-Goals

**Goals:**
- Upgrade `@copilotkit/react-core`, `@copilotkit/react-ui`, `@copilotkit/react-textarea`, and `@copilotkit/runtime` to version `1.61.0`.
- Verify TypeScript typecheck and frontend production build.

**Non-Goals:**
- Upgrading other major unrelated frameworks or libraries.
- Rewriting/restructuring application components or logic.

## Decisions

- **Npm Legacy Peer Deps**: We will run `npm install` with `--legacy-peer-deps` to ensure that any React 19 or three peer dependency conflicts are bypassed safely.
- **Run validation**: Validate with `npx tsc --noEmit` and `npm run build`.

## Risks / Trade-offs

- **[Risk] Peer Dependency mismatches** → Upgrading may trigger peer dependency conflicts (e.g., due to React 19 or Three.js).
  - *Mitigation*: Run installation with `npm install --legacy-peer-deps` and verify with TypeScript compilation.
