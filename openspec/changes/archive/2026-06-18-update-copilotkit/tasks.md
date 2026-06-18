## 1. Pre-flight Baseline

- [x] **1.1 Record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of typescript compilation before upgrading.
  - Done when:
    - `.ralph/baselines/update-copilotkit-typecheck.txt` exists with the full output of `npx tsc --noEmit`
    - the captured gate file ends with a literal `EXIT=0` line
    - `.ralph/baselines/update-copilotkit-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: typecheck gate is nondeterministic across two runs, or the captured baseline file is missing the `EXIT=<integer>` final line.

## 2. Upgrade Packages

- [x] **2.1 Upgrade CopilotKit packages and remove unused dependencies**
  - Scope: `package.json`, `package-lock.json`
  - Change: Upgraded copilotkit packages to version 1.60.2, and removed @copilotkitnext/agent.
  - Done when:
    - package.json shows @copilotkit/react-core, @copilotkit/react-ui, @copilotkit/react-textarea, and @copilotkit/runtime at 1.60.2
    - package.json no longer contains @copilotkitnext/agent
    - npm install command finishes successfully with exit 0
    - `npx tsc --noEmit` exits 0 (or matches pre-flight baseline)
  - Stop and hand off if: npm install fails with unresolvable peer dependency conflicts or if typescript typecheck fails.

## 3. Production Build Validation

- [x] **3.1 Run frontend production build**
  - Scope: frontend codebase (next.js build)
  - Change: Verify that the frontend application compiles and builds successfully for production under the new package versions.
  - Done when:
    - `npm run build` exits 0
  - Stop and hand off if: production build fails with compilation or bundling errors.
