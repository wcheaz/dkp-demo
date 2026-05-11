## 1. PricingBreakdownModal Component

- [ ] 1.1 Create `src/components/pricing-breakdown-modal.tsx` with the `PricingBreakdown` interface, the `computePricingBreakdown` pure function (mirroring `generate_quote` in `agent/src/agent.py` lines 267–293), and the `PricingBreakdownModal` React component. The component SHALL accept `PricingBreakdownModalProps` (`open`, `onClose`, `parameters`, `price`), render nothing when `open` is false, render a fixed-overlay modal when `open` is true, display a breakdown table with intermediate calculations when parameters are valid, and show an unavailable message when parameters are missing or unparseable. The modal SHALL follow the existing overlay pattern (`position: fixed; inset: 0; z-50`, `bg-black/80` backdrop, centered content, dismissible by backdrop click and Escape key, content click does not dismiss).
  - **Done when**: File exists, `PricingBreakdownModal` is exported, `computePricingBreakdown` returns correct values for known inputs (floor area 150 for "10x15m", totalJoints 198, roof type factors applied), `npm run typecheck` passes, `npm run lint` passes.
  - **Stop and hand off if**: The formula in `agent/src/agent.py` has changed and no longer matches the documented coefficients (1.32, 0.254, 0.147, 40, 4500, 15000/20, 100, ÷25).

## 2. Integration into DesignComponent

- [ ] 2.1 Modify `src/components/design-component.tsx` to add an inline SVG info icon ("!" circle, 16×16px, `cursor: pointer`) after the price value in the price cell, add `useState` for modal open/close state, import and render `PricingBreakdownModal` passing the current entry's `parameters` and `price` as props. The info icon click SHALL set modal open to true. The modal `onClose` SHALL set modal open to false. Each design entry with a price SHALL have its own modal instance scoped to that entry's parameters.
  - **Done when**: Clicking the info icon on a price cell opens the `PricingBreakdownModal` with the correct entry parameters. Dismissing the modal (backdrop click or Escape) closes it. Entries without a price show no info icon. `npm run typecheck` passes, `npm run lint` passes. Browser verification confirms the icon is visible, clickable, and the modal displays the breakdown table.

## 3. Verification

- [ ] 3.1 Run full verification: `npm run typecheck` and `npm run lint` pass with zero errors. Open the application in the browser, generate or load a design entry that has a price, verify the info icon appears in the price cell, click it, verify the breakdown modal opens showing the pricing breakdown table with intermediate calculations, verify dismissing via backdrop click and Escape both work, verify the modal shows an unavailable message for entries with missing floor plan dimensions.
  - **Done when**: All checks pass and the end-to-end flow works in the browser.
