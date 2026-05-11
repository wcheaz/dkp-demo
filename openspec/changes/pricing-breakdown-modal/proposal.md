## Why

The pricing engine generates deterministic cost estimates from design parameters, but users only see a final price string (e.g. "€1,752") with no explanation of how it was computed. Users cannot understand what drives the cost — materials, joints, assembly, roof complexity — which reduces trust and makes it harder to compare design options. A breakdown modal will surface the pricing formula's intermediate steps alongside the design entry's price.

## What Changes

- Add a clickable info icon ("!" circle button) next to the existing price cell in the design entry parameter grid within `DesignComponent`.
- Add a new self-contained `PricingBreakdownModal` component (in its own file, e.g. `src/components/pricing-breakdown-modal.tsx`) that opens when the info icon is clicked, displaying a pricing breakdown table that mirrors the backend `generate_quote` formula in `agent/src/agent.py` lines 248–296.
- The breakdown table will show each cost component (joints/gusset plates, timber volume, assembly, hangers), the roof type complexity factor, the CZK subtotals, the EUR conversion, and the final total.
- The breakdown will be computed client-side from the `DesignEntry.parameters` and `DesignEntry.price` fields already available in state, using the same deterministic formula as the backend `generate_quote` tool. The pricing computation logic will live inside the new component file to keep it self-contained and easy to modify.

## Capabilities

### New Capabilities
- `pricing-breakdown-modal`: A self-contained modal component (`src/components/pricing-breakdown-modal.tsx`) triggered by an info icon on the price cell that displays a line-item breakdown of the pricing engine's computation — joints count & cost, timber volume & cost, assembly cost, hanger cost, roof type factor, CZK subtotal, EUR conversion, and total — matching the backend `generate_quote` formula. Includes its own client-side pricing computation logic.

### Modified Capabilities
- `design-params-display`: Adding an info icon ("!" circle) button to the existing price cell in the parameter grid that opens the pricing breakdown modal.

## Impact

- **Frontend**: `src/components/design-component.tsx` — add info icon button to price cell, import and render the new `PricingBreakdownModal` component with open/close state.
- **Frontend**: `src/components/pricing-breakdown-modal.tsx` — **new file**. Self-contained component with the modal UI and client-side pricing breakdown computation logic.
- **Frontend styles**: `src/app/globals.css` — possibly add CSS custom properties for breakdown modal styling (if needed beyond existing theme tokens).
- **Types**: `src/lib/types.ts` — no changes needed (breakdown is computed from existing `DesignEntry.parameters` and `price` fields).
- **Backend**: No changes to `agent/src/agent.py`. The `generate_quote` tool continues to return the formatted price string. The frontend replicates the same deterministic formula for display purposes.
- **Dependencies**: No new dependencies. Uses existing React state and Tailwind CSS.
