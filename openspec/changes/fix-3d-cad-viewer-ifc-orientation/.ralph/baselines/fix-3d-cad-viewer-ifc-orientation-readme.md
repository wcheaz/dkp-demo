# Quality Gate Baselines

This document lists the baseline status of quality gates for the `fix-3d-cad-viewer-ifc-orientation` change.

## Baseline Summary

| Gate | Command | Exit Code | Status | Exact Failing Identifiers |
|---|---|---|---|---|
| lint | `npm run lint` | 1 | FAILING | `@typescript-eslint/no-unused-expressions`, `@typescript-eslint/no-unused-vars`, `@typescript-eslint/no-this-alias`, `react-hooks/immutability`, `react-hooks/exhaustive-deps`, `react-hooks/set-state-in-effect`, `@next/next/no-img-element` |
