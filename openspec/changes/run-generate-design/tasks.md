## 1. Receive and Record User Input

- [ ] **1.1 Record the user's input message**
  - Scope: Working memory (text output produced during task execution)
  - Change: The user's message is captured verbatim as the input for the entire workflow.
  - Done when:
    - The user's message is recorded in full, including all construction-relevant details, questions, and requests
  - Stop and hand off if: no user input is available — prompt the user to provide their message before continuing.

## 2. Classify Intent

- [ ] **2.1 Determine the primary intent from the user's message**
  - Scope: Working memory
  - Change: The user's message is classified into one or more intent categories by checking for trigger phrases from the agent's system prompt.
  - Done when:
    - The intent is recorded as one (or a combination) of: `design-generation`, `knowledge-query/summary`, `knowledge-query/specific`, `pricing-quote`, `design-modification`, `design-reset/partial`, `design-reset/full`, `general-response`
    - If the user mentions wanting a design AND pricing, both `design-generation` and `pricing-quote` are flagged
  - Stop and hand off if: the message is ambiguous and could match multiple intents — default to `design-generation` if any design-related trigger is present, otherwise `general-response`.

  Trigger phrase reference (from agent system prompt):
  - `design-generation`: "I need a design", "design for", "show me", "build me", "create", "generate", "plan for", "I want", or any description of a construction project
  - `knowledge-query/summary`: "What projects do you have?", "What do you know?", "what information is available"
  - `knowledge-query/specific`: questions about load calculations, materials, truss designs, engineering specifications
  - `pricing-quote`: "price", "cost", "estimated price", "how much"
  - `design-modification`: requests to change an existing design's image or prompt text
  - `design-reset/partial`: "change X and Y but keep Z", or wanting to clear specific parameters without removing the design
  - `design-reset/full`: "scrap this design", "delete this design", "start over completely"

## 3. Extract Construction Parameters

- [ ] **3.1 Scan the user's message for all 9 parameter fields**
  - Scope: Working memory
  - Change: Each parameter field that matches a pattern in the user's message is recorded with its value; unmatched fields are recorded as `---`.
  - Done when:
    - All 9 fields have a recorded value (either extracted or `---`):
      - `building_type` (trigger: "house", "garage", "agricultural", "family house")
      - `floor_plan_dimensions` (trigger: pattern like "10x15m", "8 x 12m")
      - `roof_type` (trigger: "gable", "hip", "mono-pitch", "flat" — must be one of these four)
      - `roof_pitch` (trigger: degree value between 2-45)
      - `attic_usage` (trigger: "none", "storage", "living space")
      - `eaves_shape` (trigger: "open", "boxed", "flush")
      - `wall_construction` (trigger: "brick", "SIP panels", "concrete block", "mixed")
      - `location` (trigger: city/place name)
      - `overhang` (trigger: dimension like "450mm")
    - A checklist of the 4 desirable fields is produced showing present vs. missing: `building_type`, `floor_plan_dimensions`, `roof_type`, `roof_pitch`
  - Stop and hand off if: the user's message contains no extractable parameters at all — proceed with all fields as `---`.

## 4. Execute Simulated Tool Actions

- [ ] **4.1 Execute knowledge summary action if intent is knowledge-query/summary**
  - Scope: `agent/knowledge/trusses-ai-english/summary.md`, working memory
  - Change: Read `summary.md` and record its full contents as the tool output. Skip this task if intent is not `knowledge-query/summary`.
  - Done when:
    - The full text of `summary.md` is recorded as output, OR
    - This task is explicitly skipped with a note: "Intent does not match — skipped"
  - Stop and hand off if: `summary.md` file does not exist.

- [ ] **4.2 Execute knowledge base search action if intent is knowledge-query/specific**
  - Scope: `agent/knowledge/trusses-ai-english/` subdirectories, working memory
  - Change: Score each of the 33 project subdirectories against the user's query words (name matches: 2 pts/word, section content matches in summary.md: 1 pt/word), select top 3, read their `.md` files, and record output with source paths.
  - Done when:
    - Output is recorded with each document prefixed by `--- Source: <relative-path> ---`
    - At least 1 and at most 3 subdirectories are included
    - OR this task is explicitly skipped with a note: "Intent does not match — skipped"
  - Stop and hand off if: `KNOWLEDGE_BASE_DIR` is empty or missing.

- [ ] **4.3 Execute pricing calculation if intent is pricing-quote**
  - Scope: Working memory
  - Change: Compute the deterministic price using the agent's formula and record the formatted output string. Skip if intent is not `pricing-quote`.
  - Done when:
    - `floor_area` is computed from extracted `floor_plan_dimensions` (width x height in meters)
    - `total_joints = round(floor_area * 1.32)`, `timber_volume = floor_area * 0.254`, `total_trusses = round(floor_area * 0.147)`
    - CZK costs computed: `gusset_plates = joints * 40`, `timber = volume * 4500`, `assembly = (trusses/20) * 15000`, `hangers = trusses * 100`
    - Roof type factor applied: Gable=1.0, Hip=1.3, Mono-pitch=0.9, Flat=0.8 (default 1.0)
    - `total_eur = round(total_czk / 25)` computed and formatted with comma separators
    - Output recorded as `"Estimated price: EUR {formatted_total} (excl. VAT)"`
    - OR if `floor_plan_dimensions` was not extracted, output is a message asking for dimensions
    - OR this task is explicitly skipped with a note: "Intent does not match — skipped"
  - Stop and hand off if: `floor_plan_dimensions` was not provided and intent is purely `pricing-quote` — the output must ask the user for dimensions.

- [ ] **4.4 Execute design generation if intent is design-generation**
  - Scope: Working memory
  - Change: Produce a design entry with the extracted parameters, status (complete if all desirable fields present, "Design In Progress" otherwise), and optional price from task 4.3.
  - Done when:
    - A design entry is recorded with all 9 parameter fields (values or `---`)
    - Status is `"complete"` if `building_type`, `floor_plan_dimensions`, `roof_type`, and `roof_pitch` are all present; otherwise status is `"Design In Progress"`
    - If pricing was computed in task 4.3, the price is included in the design entry
    - OR this task is explicitly skipped with a note: "Intent does not match — skipped"
  - Stop and hand off if: no parameters were extracted and no design intent detected — skip.

- [ ] **4.5 Execute design modification if intent is design-modification**
  - Scope: Working memory
  - Change: Produce a modified design entry with updated image_name (one of "design-alpha.svg", "design-beta.svg") and/or prompt_text. Skip if intent is not `design-modification`.
  - Done when:
    - A design entry is recorded with the specified modifications applied
    - OR this task is explicitly skipped with a note: "Intent does not match — skipped"
  - Stop and hand off if: no existing design entry ID is referenced.

- [ ] **4.6 Execute design reset if intent is design-reset**
  - Scope: Working memory
  - Change: Produce a reset confirmation listing what was cleared and what was preserved. If `remove_designs=true`, entries are removed. If `remove_designs=false`, only specified fields are set to `---`. Skip if intent is not `design-reset`.
  - Done when:
    - Output confirms which fields were cleared to `---` and which were preserved
    - OR confirms which entries were removed entirely
    - OR this task is explicitly skipped with a note: "Intent does not match — skipped"
  - Stop and hand off if: no design IDs or parameters are specified for reset.

## 5. Format Final Response

- [ ] **5.1 Compose the final output following strict formatting rules**
  - Scope: Working memory
  - Change: All tool outputs from section 4 are composed into a single final response following the agent's three-form output rule.
  - Done when:
    - Output contains ONLY printable ASCII characters (no emojis, no Unicode)
    - Output contains NO narration phrases (no "Let me...", "I'll...", "Great!", "Based on...", "The design has been...")
    - Output is exactly one of:
      - **Form 1 (Design summary)**: A parameters table showing all 9 fields with values/`---`, status, and price if available
      - **Form 2 (Missing params question)**: A concise question listing which desirable fields are missing (only: building_type, floor_plan_dimensions, roof_type, roof_pitch)
      - **Form 3 (Direct answer)**: The knowledge base content with source citations, or a direct response to the user's question
    - Source citations are present if knowledge base content was returned (format: relative file path from knowledge base directory)
  - Stop and hand off if: output does not fit exactly one of the three forms — revise until it does.

- [ ] **5.2 Deliver the final response**
  - Scope: Working memory → output
  - Change: The formatted response from task 5.1 is presented as the final output of the workflow run.
  - Done when:
    - The response text is produced and matches one of the three allowed forms
    - No additional commentary or explanation is appended
  - Stop and hand off if: the response is empty — return to task 5.1 and compose a minimal direct answer.

## 6. Reset for Re-run

- [ ] **6.1 Uncheck all task checkboxes in tasks.md**
  - Scope: `openspec/changes/run-generate-design/tasks.md`
  - Change: Replace every `- [ ]` with `- [ ]` in this file so the spec can be re-applied for a new user interaction.
  - Done when:
    - `rg "\- \[x\]" openspec/changes/run-generate-design/tasks.md` returns no matches
    - `rg "\- \[ \]" openspec/changes/run-generate-design/tasks.md` returns at least 10 matches
  - Stop and hand off if: `tasks.md` file is not writable or does not exist.
