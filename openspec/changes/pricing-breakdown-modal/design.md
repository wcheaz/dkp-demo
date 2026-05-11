## Context

The application has a pricing engine (`agent/src/agent.py` lines 248–296, `generate_quote` tool) that computes deterministic cost estimates from design parameters (floor plan dimensions, roof type). The frontend currently displays only the final formatted price string (e.g. "€1,752") in a green-styled price cell within the design entry parameter grid in `DesignComponent` (`src/components/design-component.tsx` lines 100–105).

The `DesignEntry` type already stores `parameters: DesignParameters` (which includes `floorPlanDimensions` and `roofType`) and `price: string` (e.g. "Estimated price: €1,752 (excl. VAT)"). All data needed to recompute and display the breakdown is already available on the frontend — no new API or backend changes required.

## Goals / Non-Goals

**Goals:**
- Add an info icon ("!" circle) button to the existing price cell that opens a pricing breakdown modal
- Create a self-contained `PricingBreakdownModal` component in its own file
- Display a line-item breakdown matching the backend `generate_quote` formula: joints/gusset plates, timber, assembly, hangers, roof type factor, CZK subtotals, EUR conversion, total
- Keep the pricing computation logic inside the new component file for self-containment

**Non-Goals:**
- No backend changes — the `generate_quote` tool remains unchanged
- No new API endpoints or data streaming from backend to frontend
- No changes to how the price is stored or formatted in `DesignEntry`
- No editing or interactive manipulation of the breakdown values
- No persistence of breakdown data — it is computed on-the-fly each time the modal opens

## Decisions

### Decision 1: Client-side computation using the same formula

**Choice**: Replicate the `generate_quote` formula in a client-side function inside `src/components/pricing-breakdown-modal.tsx`.

**Rationale**: All inputs (`floorPlanDimensions`, `roofType`) are already in `DesignEntry.parameters`. The formula is deterministic with no external dependencies. Computing client-side avoids backend changes, new API routes, and additional state management.

**Alternatives considered**:
- *Return breakdown from backend*: Would require modifying `generate_quote` to return structured data, updating the agent tool handler, adding new fields to `DesignEntry`, and changing the agent prompt to pass breakdown data through. More invasive for a display-only feature.
- *Dedicated API endpoint for breakdown*: Adds network latency and an endpoint to maintain for data already available client-side.

### Decision 2: Separate component file `pricing-breakdown-modal.tsx`

**Choice**: Create `src/components/pricing-breakdown-modal.tsx` as a self-contained component that owns the modal UI, the pricing breakdown computation function, and the table rendering.

**Props interface**:
```typescript
interface PricingBreakdownModalProps {
  open: boolean;
  onClose: () => void;
  parameters: DesignParameters;
  price: string;
}
```

**Rationale**: Keeps the pricing breakdown logic and UI isolated from `DesignComponent`. Easy to modify, test, or replace independently. The parent only needs to manage open/close state and pass the existing data.

### Decision 3: Pricing computation function signature

**Choice**: A pure function `computePricingBreakdown(parameters: DesignParameters)` that returns a structured object:

```typescript
interface PricingBreakdown {
  floorArea: number;
  totalJoints: number;
  timberVolume: number;
  totalTrusses: number;
  gussetPlateCost: number;
  timberCost: number;
  assemblyCost: number;
  hangerCost: number;
  subtotalCZK: number;
  roofType: string;
  roofTypeFactor: number;
  totalCZK: number;
  totalEUR: number;
}
```

**Rationale**: Returning a structured object (not a rendered string) makes the computation testable and allows the component to render each row independently. The formula matches `generate_quote` exactly: same coefficients (1.32, 0.254, 0.147), same CZK rates (40, 4500, 15000/20 trusses, 100), same roof type factors, same EUR conversion (÷25).

### Decision 4: Info icon placement and style

**Choice**: An SVG "!" circle icon (info icon) rendered inline after the price value inside the existing price cell `<div>`. The icon will be small (16×16px), use a muted color, and have `cursor: pointer`. Clicking it sets the modal open state to true.

**Rationale**: Placing it inside the price cell keeps the association clear — the breakdown relates to this specific price. Using a standard info icon ("!" in a circle) is universally understood. No icon library dependency; use an inline SVG.

### Decision 5: Modal follows existing modal pattern

**Choice**: The breakdown modal will use the same fixed-overlay pattern as the existing image enlargement modal in `DesignComponent` (lines 115–130): `position: fixed; inset: 0; z-50` with `bg-black/80` backdrop, centered content, dismissible by backdrop click and Escape key.

**Rationale**: Consistency with existing UI patterns. No new modal library needed.

### Decision 6: Breakdown table layout

**Choice**: A simple table with two columns: line item label and value. Rows:

| Line Item | Value |
|---|---|
| Floor Area | 150 m² |
| Joints | 198 |
| Gusset Plate Cost | 198 × 40 = 7,920 CZK |
| Timber Volume | 38.1 m³ |
| Timber Cost | 38.1 × 4,500 = 171,450 CZK |
| Trusses | 22 |
| Assembly Cost | 22/20 × 15,000 = 16,500 CZK |
| Hanger Cost | 22 × 100 = 2,200 CZK |
| Subtotal | 198,070 CZK |
| Roof Type | Gable (×1.0) |
| Total (CZK) | 198,070 CZK |
| Total (EUR) | €7,923 |

The displayed total EUR value will be compared against the `price` prop as a sanity display (showing the price string as passed by the agent).

**Rationale**: Showing intermediate calculations (e.g. "198 × 40 = 7,920") makes the breakdown transparent and auditable. Displaying both CZK and EUR provides full visibility into the conversion.

## Risks / Trade-offs

- **[Formula drift]** → The client-side formula could diverge from the backend if `generate_quote` is updated. Mitigation: The computation function is isolated in one file and documented as mirroring `generate_quote`. A comment in both files should reference the other.
- **[Missing parameters]** → If `floorPlanDimensions` or `roofType` are missing from the entry, the breakdown cannot be computed. Mitigation: The modal will show a message like "Pricing breakdown unavailable — missing design parameters" and the info icon will only render when the price field exists.
- **[Price string parsing]** → The `price` field is a formatted string, not a number. The breakdown computation generates its own total from parameters. Mitigation: Show both the computed total and the stored price string so any discrepancy is visible.
