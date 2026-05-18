## MODIFIED Requirements

### Requirement: PricingBreakdownModal component renders a pricing breakdown table
`PricingBreakdownModal` SHALL be a React component exported from `src/components/pricing-breakdown-modal.tsx`. It SHALL accept props: `open: boolean`, `onClose: () => void`, `parameters: DesignParameters`, `price: string`. When `open` is `true`, it SHALL render a fixed-position modal overlay with a centered content panel containing a breakdown table.

All user-facing text in the component SHALL be sourced from the translation dictionary via `useTranslations('pricing')` hook. The following strings SHALL be translation keys: modal title, all row labels (floor area, joints, gusset plate cost, timber volume, timber cost, trusses, assembly cost, hanger cost, subtotal, roof type, total CZK, total GBP), title tooltips, the "Unknown" fallback for empty roof type, the fallback error message, "Stored price:" label, and "(excl. VAT)" suffix.

Number formatting SHALL use `Intl.NumberFormat('sk-SK')` instead of `toLocaleString("en-US")`.

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

### Requirement: Modal handles missing parameters gracefully
If `parameters` is missing `floorPlanDimensions` or cannot be parsed, the modal SHALL display the translated message from key `pricing.error` instead of the breakdown table.

#### Scenario: Missing floorPlanDimensions shows translated unavailable message
- **WHEN** `PricingBreakdownModal` is rendered with `open: true` and `parameters: { roofType: "Gable" }` (no `floorPlanDimensions`) and locale `"sk"`
- **THEN** the modal SHALL display the Slovak translation from key `pricing.error`

#### Scenario: Unparseable dimensions shows translated error message
- **WHEN** `PricingBreakdownModal` is rendered with `open: true` and `parameters: { floorPlanDimensions: "invalid", roofType: "Gable" }` and locale `"sk"`
- **THEN** the modal SHALL display the Slovak translation from key `pricing.error`
