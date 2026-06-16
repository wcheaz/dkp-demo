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

This skill is a slim workflow coordinator. Detailed trigger tables, translation
dictionaries, pricing formulas, and formatting examples live in reference files
under `references/`. At each step, call `read_skill_resource` to fetch the
specific rules before producing output — do not guess or hallucinate them.

## Workflow

### Step 1 — Receive User Input

Record the user's message verbatim. This is the input for the entire workflow.

**Stop if** no input is available — prompt the user to provide their message.

### Step 2 — Classify Intent

Call `read_skill_resource('run-generate-design', 'references/intent-classification-spec.md')`
and classify the message against the English and Slovak trigger phrases defined there.

If design AND pricing intents are both present, flag both (pricing executes first).
**If ambiguous**, default to `design-generation` if any design trigger is present,
otherwise `general-response`.

### Step 3 — Extract Construction Parameters

Call `read_skill_resource('run-generate-design', 'references/parameter-extraction-spec.md')`
and scan the message for all 9 parameter fields, recognising both English and Slovak
trigger patterns. Record extracted values; mark missing fields as `---`.

Build a checklist of the 4 **desirable fields** — `building_type`,
`floor_plan_dimensions`, `roof_type`, `roof_pitch` — showing present vs missing.
A design is `"complete"` only when all 4 desirable fields are present.

### Step 4 — Execute Simulated Tool Actions

Call `read_skill_resource('run-generate-design', 'references/tool-execution-simulation-spec.md')`
for the output templates of each tool. Execute only the tasks matching the classified
intent; skip others with a note: "Intent does not match — skipped."

**Exception:** When design-generation produces a `"complete"` status (all 4
desirable fields present), automatically execute pricing (4c) and DXF generation
(4g) — even if `pricing-quote` was not in the classified intent.

Tool sub-actions:
- **4a — Knowledge summary** (`knowledge-query/summary`): return the full contents of the locale-appropriate summary file (path in `references/knowledge-summary-path.md`).
- **4b — Knowledge base search** (`knowledge-query/specific`): score the 33 project subdirectories (algorithm in `references/knowledge-base-search.md`); return top 3 prefixed with `--- Source: <path> ---`; fall back to first 3 alphabetically if none score above zero.
- **4c — Pricing calculation** (`pricing-quote`): compute the deterministic price via `references/pricing-formula.md`. If `floor_plan_dimensions` was not extracted, ask the user for dimensions instead.
- **4d — Design generation** (`design-generation`): produce a design entry with all 9 fields (values or `---`) and status (`"complete"` or `"Design In Progress"`); auto-compute price when complete.
- **4e — Design modification** (`design-modification`): update `image_name` ("design-alpha.svg" / "design-beta.svg") and/or `prompt_text`.
- **4f — Design reset** (`design-reset`): partial (`remove_designs=false`) sets named fields to `---` and keeps the entry; full (`remove_designs=true`) removes entries entirely.
- **4g — DXF generation** (`generate_dxf`): auto-triggered on a `"complete"` design (4d) or modification (4e); produce the DXF download confirmation.

### Step 5 — Format Final Response

Call `read_skill_resource('run-generate-design', 'references/response-formatting-spec.md')`
and compose the final output following those rules. Use the English or Slovak labels
and values from `references/parameter-extraction-spec.md` according to the current locale.

The response must be exactly one of three forms: a design summary (bullet list of
all 9 fields + status + optional price), a concise missing-params question, or a
direct answer. No emojis, no narration.

### Step 6 — Deliver

Present the formatted response. No additional commentary.

## References

- `references/intent-classification-spec.md` — intent trigger phrases (EN/SK)
- `references/parameter-extraction-spec.md` — parameter extraction rules and locale mappings
- `references/tool-execution-simulation-spec.md` — tool output templates
- `references/response-formatting-spec.md` — output rules and forbidden patterns
- `references/pricing-formula.md` — worked pricing examples
- `references/knowledge-base-search.md` — scoring algorithm detail
- `references/knowledge-summary-path.md` — knowledge summary file paths
