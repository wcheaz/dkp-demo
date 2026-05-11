## 1. PricingBreakdownModal Component

- [x] 1.1 Create `src/components/pricing-breakdown-modal.tsx` with the `PricingBreakdown` interface, the `computePricingBreakdown` pure function (mirroring `generate_quote` in `agent/src/agent.py` lines 267–293), and the `PricingBreakdownModal` React component. The component SHALL accept `PricingBreakdownModalProps` (`open`, `onClose`, `parameters`, `price`), render nothing when `open` is false, render a fixed-overlay modal when `open` is true, display a breakdown table with intermediate calculations when parameters are valid, and show an unavailable message when parameters are missing or unparseable. The modal SHALL follow the existing overlay pattern (`position: fixed; inset: 0; z-50`, `bg-black/80` backdrop, centered content, dismissible by backdrop click and Escape key, content click does not dismiss).
  - **Done when**: File exists, `PricingBreakdownModal` is exported, `computePricingBreakdown` returns correct values for known inputs (floor area 150 for "10x15m", totalJoints 198, roof type factors applied), `npm run typecheck` passes, `npm run lint` passes.
  - **Stop and hand off if**: The formula in `agent/src/agent.py` has changed and no longer matches the documented coefficients (1.32, 0.254, 0.147, 40, 4500, 15000/20, 100, ÷25).

## 2. Integration into DesignComponent

- [x] 2.1 Modify `src/components/design-component.tsx` to add an inline SVG info icon ("!" circle, 16×16px, `cursor: pointer`) after the price value in the price cell, add `useState` for modal open/close state, import and render `PricingBreakdownModal` passing the current entry's `parameters` and `price` as props. The info icon click SHALL set modal open to true. The modal `onClose` SHALL set modal open to false. Each design entry with a price SHALL have its own modal instance scoped to that entry's parameters.
  - **Done when**: Clicking the info icon on a price cell opens the `PricingBreakdownModal` with the correct entry parameters. Dismissing the modal (backdrop click or Escape) closes it. Entries without a price show no info icon. `npm run typecheck` passes, `npm run lint` passes. Browser verification confirms the icon is visible, clickable, and the modal displays the breakdown table.

## 3. Row Tooltips

- [x] 3.1 Add native HTML `title` attribute tooltips to each breakdown table row label in `src/components/pricing-breakdown-modal.tsx`. Each row label SHALL have a tooltip describing the pricing logic for that line item. The tooltips SHALL be:
  - **Floor Area**: "Width × Height of the floor plan"
  - **Joints**: "Floor Area × 1.32 (simulated joint count)"
  - **Gusset Plate Cost**: "Total Joints × Cost per Joint (40 CZK)"
  - **Timber Volume**: "Floor Area × 0.254 m³/m² (timber volume coefficient)"
  - **Timber Cost**: "Timber Volume × Timber Cost per m³ (4,500 CZK)"
  - **Trusses**: "Floor Area × 0.147 (simulated truss count)"
  - **Assembly Cost**: "Total Trusses ÷ 20 × Assembly Cost per Batch (15,000 CZK)"
  - **Hanger Cost**: "Total Trusses × Hanger Cost per Truss (100 CZK)"
  - **Subtotal**: "Sum of Gusset Plate Cost + Timber Cost + Assembly Cost + Hanger Cost"
  - **Roof Type**: "Complexity factor applied based on roof type (Gable: ×1.0, Hip: ×1.3, Mono-pitch: ×0.9, Flat: ×0.8)"
  - **Total (CZK)**: "Subtotal × Roof Type Factor"
  - **Total (EUR)**: "Total CZK ÷ 25 (CZK to EUR conversion rate)"
  - **Done when**: Hovering over each row label in the breakdown table displays the corresponding tooltip. `npm run typecheck` and `npm run lint` pass.

- [x] 3.2 Add a dotted underline to each breakdown table row label in `src/components/pricing-breakdown-modal.tsx` as a visual indicator that hovering reveals a tooltip. Each row label SHALL use `border-bottom: 1px dotted` or `text-decoration: underline dotted` styling.
  - **Done when**: All row labels in the breakdown table have a visible dotted underline. Row labels show `cursor: pointer` on hover. `npm run typecheck` and `npm run lint` pass.

## 4. Verification

- [x] 4.1 Run full verification: `npm run typecheck` and `npm run lint` pass with zero errors. Open the application in the browser, generate or load a design entry that has a price, verify the info icon appears in the price cell, click it, verify the breakdown modal opens showing the pricing breakdown table with intermediate calculations, verify row label tooltips appear on hover, verify dismissing via backdrop click and Escape both work, verify the modal shows an unavailable message for entries with missing floor plan dimensions.
  - **Done when**: All checks pass and the end-to-end flow works in the browser.
