## 1. Types and CSS Foundation

- [x] 1.1 Add `price` field to `DesignEntry` in `src/lib/types.ts` and `DesignEntry` Pydantic model in `agent/src/agent.py`, and add price CSS custom properties to `src/app/globals.css`

  Add `price?: string` to the `DesignEntry` TypeScript interface in `src/lib/types.ts`. Add `price: Optional[str] = None` to the `DesignEntry` Pydantic model in `agent/src/agent.py`. Add three new variables to the `@theme` block in `src/app/globals.css`: `--color-design-price-bg: rgba(34, 197, 94, 0.15)`, `--color-design-price-label: #86efac`, `--color-design-price-value: #ffffff`. Do not modify `DesignParameters` — price is a top-level field on `DesignEntry` only (design decision D1). Do not use inline Tailwind color utilities — follow the existing `--color-design-param-*` pattern (design decision D4).

  **Done when:**
  - `src/lib/types.ts` `DesignEntry` has `price?: string`
  - `agent/src/agent.py` `DesignEntry` has `price: Optional[str] = None`
  - `src/app/globals.css` `@theme` block contains `--color-design-price-bg`, `--color-design-price-label`, `--color-design-price-value`
  - `npm run build` passes with no type errors
  - Existing design entries without `price` still render correctly

  **Stop and hand off if:** TypeScript build fails after adding the field and the error is not in the changed files.

## 2. Backend Pricing Tool

- [x] 2.1 Implement `generate_quote` tool and update agent system prompt in `agent/src/agent.py`

  Add a `generate_quote` async tool decorated with `@agent.tool` in `agent/src/agent.py`. The tool accepts: `floor_plan_dimensions` (str), `roof_type` (str), `roof_pitch` (int, default 30), `building_type` (str, default "Family house"). Implement the pricing formula from design decision D2: parse dimensions string (e.g. "10x15m") to extract width and height, compute floor area, derive simulated structural outputs (totalJoints = round(area × 1.32), timberVolume = area × 0.254, totalTrusses = round(area × 0.147)), apply cost coefficients (gussetPlateCost = joints × 40, timberCost = volume × 4500, assemblyCost = (trusses/20) × 15000, hangerCost = trusses × 100), apply roof type factor (Gable=1.0, Hip=1.3, Mono-pitch=0.9, Flat=0.8), convert CZK to EUR (/25, rounded), return `"Estimated price: €{totalEUR} (excl. VAT)"`. Update the agent system prompt to include `generate_quote` instructions: call when user asks about pricing/cost, pass collected parameters, relay result, and pass price to `generate_design` as the `price` argument (design decision D5).

  **Done when:**
  - `generate_quote` tool exists in `agent/src/agent.py` with `@agent.tool` decorator
  - Calling `generate_quote` with `floor_plan_dimensions="10x15m"`, `roof_type="Gable"`, `roof_pitch=35`, `building_type="Family house"` returns a deterministic price string containing "€"
  - Calling with identical arguments twice produces identical results
  - Hip roof (factor 1.3) produces a higher price than Gable (factor 1.0) for the same floor area
  - Calling with only `floor_plan_dimensions` and `roof_type` (missing optional params) still returns a valid price
  - System prompt includes `generate_quote` description and instructions
  - `agent/src/agent.py` passes Python syntax check (`python -c "import ast; ast.parse(open('agent/src/agent.py').read())"`)

  **Stop and hand off if:** The pricing formula produces negative values or zero for valid inputs, or the dimension parsing fails on standard formats like "10x15m".

## 3. Frontend Integration

- [x] 3.1 Add `price` parameter to `generate_design` frontend tool and render price cell in `DesignComponent`

  In `src/app/page.tsx`, add a `price` parameter (type string, required false, description "Estimated price (e.g. €1,752)") to the `generate_design` `useFrontendTool` registration. In the handler, when `price` is provided, set it as a top-level `price` field on the new `DesignEntry` object (not inside `parameters`). In `src/components/design-component.tsx`, after the existing parameter grid loop that renders filled `ALL_PARAM_KEYS` entries, add a conditional block: when `entry.price` is truthy, render an additional div in the same `grid-cols-2` grid with label "Price" and value `entry.price`, using `bg-design-price-bg` for background, `text-design-price-label` for the label, and `text-design-price-value` for the value. The price cell must not use inline Tailwind color classes (design decision D4). The price cell is appended after all parameter cells so it fills the 10th position in the grid (design decision D6).

  **Done when:**
  - `generate_design` in `src/app/page.tsx` accepts `price` parameter and stores it on `DesignEntry` as a top-level field
  - `DesignComponent` renders a "Price" cell when `entry.price` is present, with green background (`bg-design-price-bg`)
  - Regular parameter cells still use teal background (`bg-design-param-bg`)
  - When all 9 parameters are filled and price is present, the grid renders exactly 10 cells in a 5×2 layout
  - When `entry.price` is undefined/null, no price cell is rendered
  - The price cell does not contain inline Tailwind color utilities like `bg-green-100`
  - `npm run build` passes

  **Stop and hand off if:** The price value appears inside the `parameters` object instead of as a top-level `DesignEntry` field, or the grid layout breaks (cells wrap incorrectly).

## 4. Runtime Fix — Price Not Persisted on DesignEntry

- [x] 4.1 Fix `generate_design` handler to actually store `price` on the `DesignEntry` object

  The `generate_design` handler in `src/app/page.tsx:344` destructures `price` from the tool arguments, but the `newEntry` object constructed at lines 361-367 never includes it. The `price` value is accepted and then silently discarded. Fix by adding `...(price !== undefined ? { price } : {})` to the `newEntry` object, after the parameters spread and before the closing brace. The price must be stored as a top-level field on `DesignEntry`, not inside `parameters`. The `setTimeout` callback at lines 373-383 uses `{ ...d, ... }` spread so it will automatically preserve the price field once it exists on the entry.

  **Done when:**
  - `newEntry` in `generate_design` handler includes `price` when provided
  - Inspecting the handler shows `price` included in the object literal (not just destructured)
  - After calling `generate_design` with `price: "€1,752"`, the resulting design entry has `entry.price === "€1,752"`
  - After the `setTimeout` completes (design transitions to "complete"), the entry still has its `price` field
  - `npm run build` passes
  - Verified at runtime: agent calls `generate_quote`, then `generate_design` with price, and the green "Price" cell appears in the parameter grid

  **Stop and hand off if:** Adding the price spread causes a TypeScript type error that is not resolved by the existing `price?: string` field on `DesignEntry`.

- [x] 4.2 Add `price` parameter to `modify_design_entry` frontend tool

  The system prompt (agent.py lines 200-201) tells the agent it can use `modify_design_entry` to update the price on an existing design entry, but the `modify_design_entry` handler in `src/app/page.tsx:386-449` does not accept a `price` parameter. Add a `price` parameter (type string, required false, description "The estimated price to set (e.g. €1,752)") to the `modify_design_entry` `useFrontendTool` registration. In the handler, when `price` is provided, include it in the updated entry object alongside existing fields (imageUrl, promptText). This enables the demo flow where the user asks for a price after a design already exists.

  **Done when:**
  - `modify_design_entry` parameter list includes `price` (type string, required false)
  - Handler destructures `price` and includes it in the updated entry when provided
  - Calling `modify_design_entry` with `design_id: 1, price: "€2,000"` updates entry 1's `price` field to `"€2,000"`
  - Calling `modify_design_entry` without `price` leaves the existing price unchanged
  - The updated design entry's price cell appears/updates in `DesignComponent`
  - `npm run build` passes

  **Stop and hand off if:** The handler's existing validation logic (`if (!image_name && !image_url && !prompt_text)`) rejects calls that only provide `price` — this check must be updated to also accept `price` as a valid standalone argument.
