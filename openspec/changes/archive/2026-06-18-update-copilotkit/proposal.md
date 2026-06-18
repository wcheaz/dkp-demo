## Why

The current version of CopilotKit is outdated (v1.54.0), which limits compatibility and doesn't include newer features and bug fixes. We want to update all `@copilotkit/*` dependencies to the recommended version `1.60.2` to resolve compatibility issues and clean up deprecated and unused dependencies like `@copilotkitnext/agent`.

## What Changes

- Update `@copilotkit/react-core` to `1.60.2`
- Update `@copilotkit/react-ui` to `1.60.2`
- Update `@copilotkit/react-textarea` to `1.60.2`
- Update `@copilotkit/runtime` to `1.60.2`
- Remove unused `@copilotkitnext/agent` dependency from `package.json`
- Ensure all existing frontend hooks (`useCoAgent`, `useFrontendTool`, `useCopilotReadable`) and backend runtime adapters build and function correctly with the new version.

## Capabilities

### New Capabilities

- `upgrade-dependencies`: Upgrade CopilotKit and remove unused packages.

### Modified Capabilities

None

## Impact

- `package.json` and `package-lock.json`
- `src/app/page.tsx`
- `src/app/layout.tsx`
- `src/app/api/copilotkit/route.ts`
