---
name: run-generate-design
description: >
  Run the truss/roof engineering agent's decision loop for a single user message.
  Classifies intent, extracts construction parameters, simulates tool outputs
  (knowledge base query, pricing, design generation, modification, reset), and
  formats a final ASCII-only response. Use when processing a user message through
  the agent workflow without executing any Python code.
metadata:
  author: dkp-demo
  version: "1.0"
  source-change: openspec/changes/run-generate-design
---

# Run Generate Design

This skill encodes the pydantic-ai agent's full single-turn decision loop as a
step-by-step workflow. Follow it for each user message to produce the same
output the agent would — without running any Python code.

## Workflow

### Step 1 — Receive User Input

Record the user's message verbatim. This is the input for the entire workflow.

**Stop if** no input is available — prompt the user to provide their message.

### Step 2 — Classify Intent

Analyze the message and classify into one or more intent categories. Match
against both English and Slovak trigger phrases:

| Intent | Trigger phrases (EN) | Trigger phrases (SK) |
|---|---|---|
| `design-generation` | "I need a design", "design for", "show me", "build me", "create", "generate", "plan for", "I want" | "potrebujem návrh", "navrhni", "chcem návrh", "potrebujem strechu", "návrh pre", "chcem" |
| `knowledge-query/summary` | "What projects do you have?", "What do you know?", "what information is available" | "aké projekty máte", "čo viete", "aké informácie máte", "prehľad" |
| `knowledge-query/specific` | Questions about load, materials, truss designs, engineering specs | Otázky o zaťažení, materiáloch, väzníkoch, technických parametroch |
| `pricing-quote` | "price", "cost", "estimated price", "how much" | "cena", "koľko", "odhadovaná cena", "cena za", "stojí" |
| `design-modification` | Requests to change an existing design's image or prompt text | Požiadavky na zmenu existujúceho návrhu |
| `design-reset/partial` | "change X and Y but keep Z" | "zmeň X a Y ale nechaj Z" |
| `design-reset/full` | "scrap this design", "delete this design", "start over completely" | "začnime odznova", "zmazať návrh", "vymazať", "odznova" |
| `general-response` | Anything that doesn't match the above | Čokoľvek, čo nezodpovedá vyššie uvedenému |

If design AND pricing are both present, flag both intents (pricing executes first).

**If ambiguous**, default to `design-generation` if any design trigger is present,
otherwise `general-response`.

### Step 3 — Extract Construction Parameters

Scan the message for all 9 parameter fields. Record extracted values; mark
missing fields as `---`.

| Field | Trigger pattern | Valid values |
|---|---|---|
| `building_type` | "house", "garage", "agricultural", "family house" | — |
| `floor_plan_dimensions` | Pattern like "10x15m", "8 x 12m" | — |
| `roof_type` | — | Gable, Hip, Mono-pitch, Flat |
| `roof_pitch` | Degree value | 2-45 |
| `attic_usage` | — | none, storage, living space |
| `eaves_shape` | — | open, boxed, flush |
| `wall_construction` | — | brick, SIP panels, concrete block, mixed |
| `location` | City/place name | — |
| `overhang` | Dimension like "450mm" | — |

Produce a checklist of the 4 **desirable fields** showing present vs missing:
`building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`.

#### Locale mapping (English — locale `en`)

When the agent locale is `en`, use these English labels and values for all
user-facing output:

**Field labels:**

- Building type
- Floor plan dimensions
- Roof type
- Roof pitch
- Attic usage
- Eaves shape
- Wall construction
- Location
- Overhang

**Parameter values:**

- Building types: Family house, Apartment building, Garage, Agricultural building, Office building, Mixed-use building
- Roof types: Gable, Hip, Mono-pitch, Flat
- Attic usage: None, Storage, Living space
- Eaves shape: Open, Boxed, Flush
- Wall construction: Brick, SIP panels, Concrete block, Mixed

**Status values:**

- Design In Progress / Complete

Example English design summary:

```
## Roof Design

- **Building type:** Family house
- **Floor plan dimensions:** 10x15m
- **Location:** Bratislava
- **Roof type:** Gable
- **Roof pitch:** 30°
- **Overhang:** 450mm
- **Attic usage:** Storage
- **Eaves shape:** Open
- **Wall construction:** Brick
```

#### Locale mapping (Slovak — locale `sk`)

When the agent locale is `sk`, use these Slovak translations for all
user-facing output (field labels, parameter values, status text):

**Field labels:**

| English label | Slovak label |
|---|---|
| Building type | Typ budovy |
| Floor plan dimensions | Rozmery pôdorysu |
| Roof type | Typ strechy |
| Roof pitch | Sklon strechy |
| Attic usage | Využitie podkrovia |
| Eaves shape | Tvar rímsy |
| Wall construction | Konštrukcia stien |
| Location | Umiestnenie |
| Overhang | Previs |

**Parameter values:**

| English | Slovak |
|---|---|
| Family house | Rodinný dom |
| Apartment building | Bytový dom |
| Garage | Garáž |
| Agricultural building | Poľnohospodárska budova |
| Office building | Kancelárska budova |
| Mixed-use building | Zmiešaná budova |
| Gable | Štítová |
| Hip | Valbová |
| Mono-pitch | Jednosklovitá |
| Flat | Plochá |
| none | žiadne |
| storage | skladovací priestor |
| living space | obytný priestor |
| open | otvorené |
| boxed | uzatvorené |
| flush | hladké |
| brick | tehla |
| SIP panels | SIP panely |
| concrete block | betónové tvárnice |
| mixed | zmiešaná |

**Status values:**

| English | Slovak |
|---|---|
| Design In Progress | Návrh v procese |
| complete | dokončené |

**Also recognise these Slovak trigger patterns for extraction:**

| Field | Slovak trigger patterns |
|---|---|
| `building_type` | "dom", "rodinný dom", "bytová budova", "garáž", "poľnohospodárska budova", "kancelárska budova", "zmiešaná budova" |
| `roof_type` | "štítová", "valbová", "jednosklovitá", "plochá" |
| `attic_usage` | "podkrovie", "skladovací priestor", "obytný priestor", "bez využitia", "žiadne" |
| `eaves_shape` | "otvorené okapy", "uzatvorené okapy", "hladké okapy" |
| `wall_construction` | "tehlové steny", "SIP panely", "betónové tvárnice", "zmiešaná konštrukcia" |

### Step 4 — Execute Simulated Tool Actions

Only execute the tasks matching the classified intent. Skip others with a note:
"Intent does not match — skipped."

**Exception:** When design-generation produces a `"complete"` status (all 4
desirable fields present), automatically execute the pricing calculation
(step 4c) as well — even if `pricing-quote` was not in the classified intent.

#### 4a — Knowledge summary (`knowledge-query/summary`)

Read [the knowledge base summary](references/knowledge-summary-path.md) and
return its full contents as output.

#### 4b — Knowledge base search (`knowledge-query/specific`)

Score each of the 33 project subdirectories against the user's query words:

- Name matches: 2 pts per word
- Section content matches in summary.md: 1 pt per word

Select top 3, read their `.md` files, prefix each with
`--- Source: <relative-path> ---`.

Fallback: if no subdirectory scores above zero, use the first 3 alphabetically.

See [knowledge base search reference](references/knowledge-base-search.md) for
the full scoring algorithm.

#### 4c — Pricing calculation (`pricing-quote`)

Compute the deterministic price:

```
floor_area = width * height (from floor_plan_dimensions)
total_joints = round(floor_area * 1.32)
timber_volume = floor_area * 0.254
total_trusses = round(floor_area * 0.147)

CZK costs:
  gusset_plates = joints * 40
  timber = volume * 4500
  assembly = (trusses / 20) * 15000
  hangers = trusses * 100

Roof type factor: Gable=1.0, Hip=1.3, Mono-pitch=0.9, Flat=0.8

total_eur = round(total_czk / 25)
Output: integer (EUR, excl. VAT)
```

If `floor_plan_dimensions` was not extracted, output a message asking the user
for dimensions instead.

See [pricing formula reference](references/pricing-formula.md) for worked examples.

#### 4d — Design generation (`design-generation`)

Produce a design entry with:
- All 9 parameter fields (extracted values or `---`)
- Status: `"complete"` if all 4 desirable fields are present; otherwise
  `"Design In Progress"`
- Price from step 4c — automatically compute if status is `"complete"` (all 4
  desirable fields present); otherwise only if `pricing-quote` was also requested

#### 4e — Design modification (`design-modification`)

Produce a modified design entry with updated `image_name` (one of
"design-alpha.svg", "design-beta.svg") and/or `prompt_text`.

#### 4f — Design reset (`design-reset`)

- **Partial** (`remove_designs=false`): Set specified parameter fields to `---`,
  preserve others, keep the entry.
- **Full** (`remove_designs=true`): Remove targeted entries entirely.

### Step 5 — Format Final Response

Compose the final output following strict rules:

1. **No emojis** — do not use emoji or pictograph characters in any output
2. **No narration** — forbidden: "Let me...", "I'll...", "Great!", "Based on...",
   "The design has been...", "Now generating...", etc. Output must read as a
   direct answer to the user, not a log of actions taken.
3. **Chat-friendly formatting** — use standard markdown (headings, bullet lists).
   Design summaries MUST use a bullet list (`- **Label:** value`) for all 9 fields.
   Do NOT use pipe-delimited tables, reStructuredText-style underlines (`===`, `---`),
   horizontal rules made of dashes, boxed/bordered sections, or any formatting
   that resembles a standalone document/report. The response must look like a
   chat message, not a file.
4. **Exactly one of three forms**:

| Form | When | Content |
|---|---|---|
| Design summary | Design was generated | Bullet list of 9 fields (`- **Label:** value`), status, optional price |
| Missing params question | Design triggered but desirable fields missing | Concise question listing only missing fields |
| Direct answer | Knowledge query or general question | Answer with source citations (relative file paths) |

**When locale is `en`**, use English labels and English parameter values from
the English locale mapping section above. The heading MUST be "Roof Design".
All labels, values, and status text must be in English.

**When locale is `sk`**, use Slovak labels and Slovak parameter values from the
Slovak locale mapping table below. Example Slovak design summary:

```
## Návrh strechy

- **Typ budovy:** Rodinný dom
- **Rozmery pôdorysu:** 10x15m
- **Umiestnenie:** Veľké Lovce
- **Typ strechy:** Štítová
- **Sklon strechy:** 35°
- **Previs:** 400mm
- **Využitie podkrovia:** Obytný priestor
- **Tvar rímsy:** Otvorené
- **Konštrukcia stien:** Tehla
```

When locale is `en`, use the English labels and values from the English
locale mapping section above. Example English design summary:

```
## Roof Design

- **Building type:** Family house
- **Floor plan dimensions:** 10x15m
- **Location:** Bratislava
- **Roof type:** Gable
- **Roof pitch:** 30°
- **Overhang:** 450mm
- **Attic usage:** Storage
- **Eaves shape:** Open
- **Wall construction:** Brick
```

See [response formatting reference](references/response-formatting.md) for
examples and the full list of forbidden narration patterns.

### Step 6 — Deliver

Present the formatted response. No additional commentary.

## References

- [Intent classification spec](references/intent-classification-spec.md) — full scenario definitions
- [Parameter extraction spec](references/parameter-extraction-spec.md) — per-field extraction rules
- [Tool execution simulation spec](references/tool-execution-simulation-spec.md) — tool output templates
- [Response formatting spec](references/response-formatting-spec.md) — output rules and forbidden patterns
- [Pricing formula reference](references/pricing-formula.md) — worked pricing examples
- [Knowledge base search reference](references/knowledge-base-search.md) — scoring algorithm detail
