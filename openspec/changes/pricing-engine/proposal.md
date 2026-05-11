## Why

The demo script (Step 4a, Scenario A) requires the user to ask "What is the estimated price?" and receive a structured cost estimate. There is currently zero pricing logic in the project — the demo stops at "we generated a design image" with no business outcome. Pricing is half of the demo's value proposition ("from 2 hours + 15–20 min pricing down to 5 minutes"). The audience needs to see a number to complete the narrative.

## What Changes

- Add a `generate_quote` backend tool to `agent/src/agent.py` that takes design parameters and returns a deterministic cost estimate using a formulaic pricing model.
- Add a `price` field to `DesignEntry` in `src/lib/types.ts` so each design entry can carry its computed price.
- Add a `price` parameter to the `generate_design` frontend tool in `src/app/page.tsx` so the agent can pass the computed price when creating a design entry.
- Update `DesignComponent` in `src/components/design-component.tsx` to render the price as the 10th cell in the 2-column parameter grid, completing the 5×2 layout when all 9 parameters plus price are present.
- Style the price cell with a light green background using CSS custom properties defined in `src/app/globals.css`, following the existing `@theme` pattern (e.g. `--color-design-price-bg`, `--color-design-price-label`, `--color-design-price-value`). The price cell SHALL use these CSS class-based variables, not inline Tailwind utility classes, consistent with how the teal parameter cells use `bg-design-param-bg`.

## Capabilities

### New Capabilities

- `pricing-calculation`: Backend pricing engine that computes a deterministic cost estimate from design parameters (floor plan area, roof type, roof pitch, building type). Uses formulaic coefficients derived from the pricing model in `hidden/DEMO-STRUCTURED-DATA.md`. Returns a structured price breakdown (timber cost, assembly cost, hardware cost, total).

### Modified Capabilities

- `design-params-self-contained`: The `generate_design` frontend tool SHALL accept an optional `price` argument and store it on the `DesignEntry`. The `DesignParameters` type is extended or a separate `price` field is added to `DesignEntry`.
- `design-params-display`: The `DesignComponent` SHALL render the price value as an additional cell in the parameter grid with a light green background using CSS custom properties in `src/app/globals.css`, distinct from the teal styling of other parameter cells.

## Impact

- **Backend** (`agent/src/agent.py`): New `generate_quote` tool, pricing formula logic, updated system prompt to instruct the agent when to call it.
- **Frontend types** (`src/lib/types.ts`): `DesignEntry` gains a `price` field (string or number). `DesignParameters` may gain a `price` key, or price is stored directly on `DesignEntry`.
- **Frontend tool** (`src/app/page.tsx`): `generate_design` handler accepts and stores `price` argument.
- **Frontend component** (`src/components/design-component.tsx`): Parameter grid renders price cell with green background using CSS custom property classes.
- **Frontend styles** (`src/app/globals.css`): New `@theme` variables for price cell colors (`--color-design-price-bg`, `--color-design-price-label`, `--color-design-price-value`), following the existing `--color-design-param-*` pattern.
- **Backend model** (`agent/src/agent.py`): `DesignEntry` Pydantic model gains a `price` field.
- **No new dependencies**: All pricing is computed in-process with hardcoded coefficients.

## Non-goals

- Exact real-world pricing accuracy — formulaic approximation is sufficient for demo purposes.
- Add-on pricing (roof windows, insulation, etc.) — deferred to a follow-up change.
- Currency selection or conversion — present a single currency (EUR) for demo clarity.
- Persistent quote storage or quote history — prices are computed on-the-fly and displayed inline.
- Dedicated quote display component (separate card/panel) — price is displayed within the existing parameter grid.
- PDF or exportable quote documents.

## Scope boundaries

- **In scope**: One pricing formula, one new backend tool, one new frontend parameter cell, green styling.
- **Out of scope**: Multiple pricing tiers, add-ons, discounts, tax calculations, currency conversion, external pricing API integration, quote PDFs, quote comparison between designs.
- **First rollout**: Agent computes price via `generate_quote`, passes it to `generate_design`, and the price appears in the design entry's parameter grid with green background.
