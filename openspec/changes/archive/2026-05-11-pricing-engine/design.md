## Context

The project is a demo application for timber truss/roof engineering. An AI assistant collects construction parameters from the user (floor plan, roof type, pitch, etc.), generates a simulated design, and displays it in a card-based UI. The current flow is: collect parameters → generate design image → display. There is no pricing capability.

The agent is a Pydantic AI agent (`agent/src/agent.py`) with backend tools (`query_knowledge_base`, `get_knowledge_summary`) and frontend tools registered via CopilotKit's `useFrontendTool` in `src/app/page.tsx` (`generate_design`, `modify_design_entry`, `update_design_parameters`). Frontend state is typed in `src/lib/types.ts`. The design component (`src/components/design-component.tsx`) renders design cards with a 2-column parameter grid using Tailwind v4 CSS custom properties defined in `src/app/globals.css`.

Files involved:
- `agent/src/agent.py` — agent definition, backend tools, system prompt, Pydantic models
- `src/lib/types.ts` — TypeScript interfaces (`DesignEntry`, `DesignParameters`, `AgentState`)
- `src/app/page.tsx` — frontend tool handlers (`generate_design`, etc.)
- `src/components/design-component.tsx` — parameter grid rendering per design entry
- `src/app/globals.css` — `@theme` CSS custom properties for styling

## Goals / Non-Goals

**Goals:**
- Add a `generate_quote` backend tool that computes a deterministic price from design parameters using a fixed formula
- Store the price string on each `DesignEntry` as a top-level field
- Render the price in the design entry's parameter grid as a distinct green cell (vs teal for regular params)
- Define price styling via CSS custom properties in `globals.css`, not inline Tailwind utilities

**Non-Goals:**
- Exact real-world pricing accuracy
- Add-on pricing (roof windows, insulation)
- Currency selection or multi-currency display
- Persistent quote storage or history
- Dedicated quote display component or panel
- PDF/exportable quote documents

## Decisions

### D1: Price stored as top-level field on DesignEntry, not inside DesignParameters

**Choice**: Add `price?: string` directly to `DesignEntry` in `src/lib/types.ts` and `DesignEntry` in `agent/src/agent.py`.

**Rationale**: The price is not a user-collected parameter — it is a computed output derived from the parameters. Mixing it into `DesignParameters` would break the clean separation between "what the user provides" and "what the system computes." Keeping it as a top-level field means:
- The parameter grid's `ALL_PARAM_KEYS` array stays unchanged (9 user-facing fields)
- The price rendering can be handled as a separate conditional block after the parameter grid
- No risk of the price appearing in parameter collection/validation logic

**Alternative considered**: Adding `price` to `DesignParameters`. Rejected because it conflates input and output, would require filtering it out of the collection loop, and would muddy the `PARAM_LABELS` mapping.

### D2: Pricing formula uses simulated structural outputs derived from floor area

**Choice**: The formula derives simulated intermediate values (`totalJoints`, `timberVolume`, `totalTrusses`) from the floor area, then applies cost coefficients to compute the total.

**Formula** (fixed in `agent/src/agent.py`):
```
floor_area = W × H  (parsed from "10x15m")
totalJoints = round(floor_area × 1.32)
timberVolume = floor_area × 0.254
totalTrusses = round(floor_area × 0.147)

gussetPlateCost = totalJoints × 40       (CZK)
timberCost = timberVolume × 4500         (CZK/m³)
assemblyCost = (totalTrusses / 20) × 15000  (CZK)
hangerCost = totalTrusses × 100          (CZK)

totalCZK = (gussetPlateCost + timberCost + assemblyCost + hangerCost) × roofTypeFactor
totalEUR = round(totalCZK / 25)
```

**Roof type factors**: Gable=1.0, Hip=1.3, Mono-pitch=0.9, Flat=0.8.

**Rationale**: The coefficients come from `hidden/DEMO-STRUCTURED-DATA.md` analysis of 33 real projects. The intermediate simulation (joints, timber volume, trusses from floor area) produces plausible-looking numbers without needing a real structural engine. The CZK→EUR conversion at 25:1 matches the document's guidance.

**Alternative considered**: A simpler flat rate (€/m²). Rejected because it would not differentiate by roof type, losing a key demo narrative point (hip roofs cost more than gable).

### D3: Price formatting — "€{X}" string, formatted by the backend tool

**Choice**: `generate_quote` returns `"Estimated price: €{totalEUR} (excl. VAT)"` as the full string. The `price` field on `DesignEntry` stores the display-ready price portion (e.g. `"€1,752"`).

**Rationale**: The agent needs a human-readable response string AND a machine-passable price value. The tool returns the full response string (for the agent to relay in chat), and the agent extracts or the tool also returns just the formatted price for passing to `generate_design`. For simplicity, the tool returns a string and the agent passes the relevant portion to `generate_design`.

**Implementation**: `generate_quote` returns a structured string. The agent is instructed via system prompt to pass the price to `generate_design`'s `price` parameter. The `price` field stores a pre-formatted display string like `"€1,752"`.

### D4: Price cell styling via CSS custom properties in globals.css @theme block

**Choice**: Add three new `@theme` variables to `src/app/globals.css`:
```css
--color-design-price-bg: rgba(34, 197, 94, 0.15);
--color-design-price-label: #86efac;
--color-design-price-value: #ffffff;
```

The price cell uses `bg-design-price-bg`, `text-design-price-label`, and `text-design-price-value` — following the exact same pattern as the existing `--color-design-param-bg`, `--color-design-param-label`, `--color-design-param-value`.

**Rationale**: The project already uses Tailwind v4 `@theme` for all design token colors. Adding inline Tailwind utilities like `bg-green-100` would break the established pattern and make the price cell inconsistent with the rest of the parameter grid. Using the same CSS variable pattern ensures:
- Consistency with the existing teal parameter cells
- Easy theme adjustments via a single `@theme` block
- No hardcoded color values in component JSX

**Alternative considered**: Using Tailwind's built-in `bg-green-100`. Rejected per project convention — all component colors go through `@theme` custom properties.

### D5: Agent workflow — generate_quote called before or alongside generate_design

**Choice**: The agent calls `generate_quote` when the user asks about price. It can call it before or after `generate_design`. The system prompt instructs the agent to also pass the returned price to `generate_design` as the `price` argument so the price appears in the design entry card.

**Rationale**: The demo flow is flexible — the user might ask for a price before generating a design, or after. By having the agent pass the price to `generate_design`, the price gets stored on the design entry and displayed in the grid. If the user asks for a price after a design already exists, the agent can use `modify_design_entry` to update the price on the existing entry. For the first rollout, the primary flow is: collect params → generate_quote → generate_design (with price).

**Alternative considered**: Auto-computing price inside `generate_design`. Rejected because it couples pricing to design generation and prevents the user from asking for a price estimate independently.

### D6: Price rendering position — last cell in the 2-column grid

**Choice**: The price cell is rendered after all filled parameter cells within the existing `grid-cols-2` grid in `design-component.tsx`. When all 9 parameters are filled and price is present, this creates a perfect 5×2 grid (10 cells).

**Rationale**: The user specifically requested the price fill the "extra slot" in the table. With 9 parameters in a 2-col grid, the last row has one empty cell. Adding price as the 10th cell completes the grid visually. The price cell is appended after the parameter loop, so it naturally fills position 10.

## Risks / Trade-offs

- **[Price formula is approximate]** → Acceptable for demo. The coefficients are plausible but not accurate. No mitigation needed — non-goal is exact pricing.
- **[Price not auto-updated if parameters change after initial quote]** → For the demo, the agent will need to re-call `generate_quote` and `modify_design_entry` if parameters change. The system prompt should mention this. Not a blocker for first rollout.
- **[CSS variable names must not collide with existing ones]** → Mitigated by using a distinct `price` prefix (`--color-design-price-*`) in the `@theme` block.
- **[Large floor plan dimensions could produce very large prices]** → Acceptable for demo. No capping needed.

## Migration Plan

No migration required. This is purely additive:
1. Add `price` field to `DesignEntry` (optional — existing entries without price are unaffected)
2. Add new backend tool (no existing tools are modified)
3. Add new CSS variables (additive, no existing styles change)
4. Update system prompt (additive instructions)

**Rollback**: Remove the `price` field from types, remove the `generate_quote` tool, revert system prompt additions, remove CSS variables. No data migration concerns since all data is in-memory state.
