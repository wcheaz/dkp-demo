## Purpose

Defines the PricingBreakdownModal component that displays an itemized pricing breakdown table for a design entry. The modal shows how the total price is computed from design parameters, allowing the user to audit intermediate calculations.

## Requirements

### Requirement: PricingBreakdownModal component renders a pricing breakdown table
`PricingBreakdownModal` SHALL be a React component exported from `src/components/pricing-breakdown-modal.tsx`. It SHALL accept props: `open: boolean`, `onClose: () => void`, `parameters: DesignParameters`, `price: string`. When `open` is `true`, it SHALL render a fixed-position modal overlay with a centered content panel containing a breakdown table. The table SHALL display line items computed from `parameters` using the same formula as the backend `generate_quote` tool in `agent/src/agent.py`.

All user-facing text in the component SHALL be sourced from the translation dictionary via `useTranslations('pricing')` hook. The following strings SHALL be translation keys: modal title, all row labels (floor area, joints, gusset plate cost, timber volume, timber cost, trusses, assembly cost, hanger cost, subtotal, roof type, total CZK, total GBP), title tooltips, the "Unknown" fallback for empty roof type, the fallback error message, "Stored price:" label, and "(excl. VAT)" suffix.

Number formatting SHALL use `Intl.NumberFormat('sk-SK')` instead of `toLocaleString("en-US")`.

#### Scenario: Modal renders breakdown table when open
- **WHEN** `PricingBreakdownModal` is rendered with `open: true`, `parameters: { floorPlanDimensions: "10x15m", roofType: "Gable" }`, and `price: "Estimated price: €7,923 (excl. VAT)"`
- **THEN** the modal SHALL display a table with rows for floor area, joints, gusset plate cost, timber volume, timber cost, trusses, assembly cost, hanger cost, subtotal CZK, roof type with factor, total CZK, and total EUR

#### Scenario: Modal renders with translated labels
- **WHEN** `PricingBreakdownModal` is rendered with `open: true` and locale `"sk"`
- **THEN** the modal title SHALL display the Slovak translation from key `pricing.title`
- **AND** each table row label SHALL display the corresponding Slovak translation

#### Scenario: Number formatting uses Slovak locale
- **WHEN** the breakdown table displays numeric values
- **THEN** numbers SHALL be formatted using `Intl.NumberFormat('sk-SK')` — using space as thousands separator and comma as decimal separator

#### Scenario: Tooltips are translated
- **WHEN** the breakdown table renders tooltips on row labels
- **THEN** each tooltip SHALL display the translated description from the corresponding translation key

#### Scenario: Error message is translated
- **WHEN** `PricingBreakdownModal` is rendered with `open: true` and `parameters` missing `floorPlanDimensions` and locale is `"sk"`
- **THEN** the error message SHALL display the Slovak translation from key `pricing.error`

#### Scenario: Modal is hidden when open is false
- **WHEN** `PricingBreakdownModal` is rendered with `open: false`
- **THEN** the modal overlay and content panel SHALL NOT be rendered in the DOM

### Requirement: Client-side computation mirrors backend generate_quote formula
The component SHALL include a pure function `computePricingBreakdown(parameters: DesignParameters)` that returns a structured breakdown object. The function SHALL apply the same formula as `generate_quote` in `agent/src/agent.py`:
1. Parse `floorPlanDimensions` (regex `(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?`) to extract width and height. Floor area = width × height.
2. `totalJoints` = floor_area × 1.32 (rounded).
3. `timberVolume` = floor_area × 0.254.
4. `totalTrusses` = floor_area × 0.147 (rounded).
5. `gussetPlateCost` = totalJoints × 40 (CZK).
6. `timberCost` = timberVolume × 4500 (CZK).
7. `assemblyCost` = (totalTrusses / 20) × 15000 (CZK).
8. `hangerCost` = totalTrusses × 100 (CZK).
9. Roof type factor: Gable = 1.0, Hip = 1.3, Mono-pitch = 0.9, Flat = 0.8, default = 1.0.
10. `totalCZK` = (gussetPlateCost + timberCost + assemblyCost + hangerCost) × roofTypeFactor.
11. `totalEUR` = round(totalCZK / 25).

#### Scenario: Breakdown matches backend output for Gable roof
- **WHEN** `computePricingBreakdown` is called with `{ floorPlanDimensions: "10x15m", roofType: "Gable" }`
- **THEN** floor area SHALL be 150, totalJoints SHALL be 198, totalEUR SHALL equal the value produced by calling `generate_quote` on the backend with the same inputs

#### Scenario: Breakdown matches backend output for Hip roof
- **WHEN** `computePricingBreakdown` is called with `{ floorPlanDimensions: "10x15m", roofType: "Hip" }`
- **THEN** totalEUR SHALL be exactly 1.3× the Gable roof totalEUR (before final rounding)

#### Scenario: Unknown roof type defaults to factor 1.0
- **WHEN** `computePricingBreakdown` is called with `{ floorPlanDimensions: "10x15m", roofType: "Unknown" }`
- **THEN** the roof type factor SHALL be 1.0 and totalEUR SHALL equal the Gable roof totalEUR

### Requirement: Breakdown table shows intermediate calculations
Each cost component row in the breakdown table SHALL display the intermediate calculation (e.g. "198 × 40 = 7,920 CZK") so the user can audit how each value was derived. The table SHALL include rows for: floor area (m²), joints (count), gusset plate cost (CZK with calculation), timber volume (m³), timber cost (CZK with calculation), trusses (count), assembly cost (CZK with calculation), hanger cost (CZK with calculation), subtotal (CZK), roof type with factor, total CZK, and total EUR.

#### Scenario: Cost rows show multiplication breakdown
- **WHEN** the breakdown table is rendered for parameters `{ floorPlanDimensions: "10x15m", roofType: "Gable" }`
- **THEN** the gusset plate cost row SHALL show "198 × 40 = 7,920 CZK"
- **AND** the timber cost row SHALL show a calculation involving timberVolume × 4500
- **AND** the hanger cost row SHALL show trusses × 100

#### Scenario: Roof type row shows factor
- **WHEN** the breakdown table is rendered for `roofType: "Hip"`
- **THEN** the roof type row SHALL display "Hip (×1.3)"

### Requirement: Modal overlay follows existing pattern
The modal SHALL use a fixed-position overlay covering the full viewport (`position: fixed; inset: 0; z-50`) with a semi-transparent dark backdrop (`bg-black/80` or equivalent). The content panel SHALL be centered within the overlay. Clicking the backdrop area (outside the content panel) SHALL close the modal. Pressing the Escape key SHALL close the modal. Clicking inside the content panel SHALL NOT close the modal.

#### Scenario: Clicking backdrop closes modal
- **WHEN** the modal is open and the user clicks the backdrop area (outside the content panel)
- **THEN** `onClose` SHALL be called

#### Scenario: Pressing Escape closes modal
- **WHEN** the modal is open and the user presses the Escape key
- **THEN** `onClose` SHALL be called

#### Scenario: Clicking content panel does not close modal
- **WHEN** the modal is open and the user clicks inside the content panel
- **THEN** `onClose` SHALL NOT be called

### Requirement: Modal handles missing parameters gracefully
If `parameters` is missing `floorPlanDimensions` or cannot be parsed, the modal SHALL display a message indicating the breakdown is unavailable instead of the breakdown table.

#### Scenario: Missing floorPlanDimensions shows unavailable message
- **WHEN** `PricingBreakdownModal` is rendered with `open: true` and `parameters: { roofType: "Gable" }` (no `floorPlanDimensions`)
- **THEN** the modal SHALL display a message like "Pricing breakdown unavailable — missing floor plan dimensions"

#### Scenario: Unparseable dimensions shows error message
- **WHEN** `PricingBreakdownModal` is rendered with `open: true` and `parameters: { floorPlanDimensions: "invalid", roofType: "Gable" }`
- **THEN** the modal SHALL display a message indicating the dimensions could not be parsed
