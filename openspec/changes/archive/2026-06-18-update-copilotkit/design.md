## Context

The project is currently using CopilotKit packages version `1.54.0` in a Next.js App Router application. The frontend uses hooks like `useCoAgent`, `useFrontendTool`, and `useCopilotReadable` to communicate with a custom FastAPI Python agent. We also have an unused dependency `@copilotkitnext/agent: 1.53.0` which is a deprecated fork of the agent client. 

This change upgrades all `@copilotkit/*` packages to `1.60.2` to ensure access to stability improvements and fixes, and removes `@copilotkitnext/agent`.

## Goals / Non-Goals

**Goals:**
- Upgrade `@copilotkit/react-core`, `@copilotkit/react-ui`, `@copilotkit/react-textarea`, and `@copilotkit/runtime` to version `1.60.2`.
- Safely remove `@copilotkitnext/agent` from `package.json` and `package-lock.json`.
- Ensure TypeScript typechecking and builds complete successfully.
- Verify runtime behavior of the frontend and agent connection.

**Non-Goals:**
- Rewriting/migrating the entire application to CopilotKit V2 hooks (`useAgent` and `@copilotkit/react-core/v2` imports) unless V1 hooks are incompatible or cause compiler/runtime failures.
- Upgrading other major libraries (like Next.js, React, or Tailwind) that are not directly related to CopilotKit.

## Decisions

- **Keep V1 Hooks:** We will continue to use the V1 hooks (`useCoAgent`, `useFrontendTool`, `useCopilotReadable` from `@copilotkit/react-core`) during the initial upgrade step. Research indicates version `1.60.2` retains backwards compatibility for V1 hooks. If they fail, we will selectively migrate to V2 hooks (`useAgent` and Zod-based schemas).
- **Remove `@copilotkitnext/agent`:** Since grep search confirms zero imports in `src/`, this package is completely unused and will be removed to clean up the dependency tree.
- **Npm CLI:** We will run `npm install` as it is the primary package manager defined in `package-lock.json` and referenced in scripts.

## Risks / Trade-offs

- **[Risk] React 19 Compatibility** → React 19 is used (`^19.2.1`). If CopilotKit `1.60.2` has strict peer dependency limits for React 18, `npm install` might fail.
  - *Mitigation*: Run with `npm install --legacy-peer-deps` to bypass strict peer dependency checks if a conflict occurs, then verify the runtime works fine.
- **[Risk] Deprecated UI/hooks runtime issues** → Using V1 hooks might lead to deprecation warnings or minor errors at runtime.
  - *Mitigation*: Run the local development server and verify the chat agent handles input, registers frontend tools, and updates state without errors.
