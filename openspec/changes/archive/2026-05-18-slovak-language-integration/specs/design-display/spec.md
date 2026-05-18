## MODIFIED Requirements

### Requirement: DesignComponent renders a scrollable list of design entries
The `DesignComponent` SHALL accept an `AgentState` containing a `designs` array of `DesignEntry` objects and a `parameters` field of type `DesignParameters`. The component SHALL render a parameter display section above the scrollable design cards container (see `design-params-display` capability). Each `DesignEntry` SHALL have an `imageUrl` (string), a `promptText` (string), and a `status` field (`"processing" | "complete"`). The component SHALL render one card per entry inside a scrollable container. Multiple cards SHALL be visible simultaneously. The scrollable container SHALL use `overflow-y: auto` so the user can scroll through the design history. Each card SHALL contain an `<img>` element with `src` set to the entry's `imageUrl` and a text element displaying the entry's `promptText`.

All user-facing text in the component SHALL be sourced from the translation dictionary via `useTranslations('designs')` hook. The following strings SHALL be translation keys, NOT hardcoded: the heading text, empty state message, processing overlay text, `MATERIAL_STAT_LABELS` values, `PARAM_LABELS` values, "Material Estimate" label, "Price:" label, and image alt text. Currency display SHALL use `Intl.NumberFormat('sk-SK', ...)` for formatting, with the currency symbol derived from the translation dictionary.

#### Scenario: Empty state when no designs exist
- **WHEN** the `designs` array on `AgentState` is empty or undefined
- **THEN** the component SHALL display the translated empty-state message from key `designs.empty`, and SHALL render zero design cards. The parameter display section SHALL still render above the empty state.

#### Scenario: Processing entry shows translated overlay text
- **WHEN** the `designs` array contains one entry with `status: "processing"`
- **THEN** the card SHALL render a processing overlay containing a CSS-animated spinner and the translated text from key `designs.generating`. The text SHALL NOT be the hardcoded English string "Generating truss structure...".

#### Scenario: Material stat labels use translated values
- **WHEN** `DesignComponent` renders material stat labels
- **THEN** each label SHALL come from translation keys `designs.labels.totalTrusses`, `designs.labels.timberVol`, `designs.labels.joints`, `designs.labels.roofArea` — NOT from hardcoded English objects.

#### Scenario: Parameter labels use translated values
- **WHEN** `DesignComponent` renders parameter labels
- **THEN** each label SHALL come from translation keys `designs.params.buildingType`, `designs.params.floorPlanDimensions`, etc. — NOT from hardcoded English objects.

#### Scenario: Price display uses Slovak locale formatting
- **WHEN** a design entry has `price: "1752"` and the locale is `"sk"`
- **THEN** the formatted price SHALL use `Intl.NumberFormat('sk-SK')` with the currency symbol from the translation dictionary

#### Scenario: "Material Estimate" heading is translated
- **WHEN** `DesignComponent` renders the material estimate section
- **THEN** the heading SHALL use the value from translation key `designs.materialEstimate`, NOT the hardcoded string "Material Estimate"

### Requirement: Price display hides info icon when placeholder

When a design entry's `price` field is set to `"---"`, the `DesignComponent` SHALL display the price value as `"---"` but SHALL NOT render the pricing info icon. The "Price:" label SHALL come from the translation dictionary key `designs.price`.

#### Scenario: Price placeholder shows value without info icon
- **GIVEN** a design entry with `price: "---"`
- **WHEN** the `DesignComponent` renders the price section
- **THEN** the price value `"---"` SHALL be displayed with the translated label from `designs.price`
- **AND** the pricing info icon SHALL NOT be rendered
