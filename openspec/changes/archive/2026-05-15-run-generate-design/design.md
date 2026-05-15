## Context

The pydantic-ai agent (`agent/src/agent.py`) is a stateless request-response system. For each user message it:

1. Receives the message text
2. Classifies the user's intent by checking for trigger phrases
3. Extracts any construction parameters from the message
4. Decides which tools to call based on the intent
5. Executes tool calls in sequence (some in parallel)
6. Formats a final response using strict ASCII-only, no-narration rules

This design captures that exact loop as a sequence of OpenSpec tasks. No code is written. The "implementation" is the workflow itself — each task is a decision or action step that produces structured output.

## Goals / Non-Goals

**Goals:**
- Encode the agent's full decision tree as a sequence of tasks that any executor (human or AI) can follow
- Each task has clear input (what to examine) and output (what to produce)
- The final output matches exactly what the pydantic-ai agent would produce for the same input
- Idempotent: can be rerun for new interactions via the reset task

**Non-Goals:**
- Writing any Python code or modifying any source files
- Replacing the agent — this is a documentation/workflow spec, not a runtime replacement
- End-to-end testing of the LLM conversation loop
- Handling multi-turn conversation state (each run is a single-turn simulation)

## Decisions

### D1: Single-turn workflow per run

Each `opsx-apply` run processes one user message. Multi-turn conversations require multiple runs. The spec does not persist state between runs.

**Rationale:** OpenSpec tasks are file-based and session-scoped. Multi-turn state (design entries, parameter accumulation) would require external persistence. For a workflow spec, single-turn is sufficient to demonstrate the agent's logic.

### D2: Tool outputs are simulated via structured templates

Instead of running actual Python tools, each "tool call" task produces output using a template that matches what the real tool returns. For example, `generate_quote` is a deterministic formula — the task provides the formula and the executor computes the result. `query_knowledge_base` returns pre-defined results from the knowledge base files.

**Rationale:** No code execution means no environment dependencies. The workflow is self-contained.

### D3: Intent classification is a single branching task

The first substantive task classifies the user's intent into one of six categories. Subsequent tasks are conditional — only the branch matching the classified intent is executed. In practice, the executor skips tasks that don't match.

**Rationale:** Mirrors the agent's prompt-driven decision tree. Keeps the task sequence linear but with clear skip conditions.

### D4: Parameter extraction uses a field-by-field checklist

The extraction task lists all 9 parameter fields with their trigger patterns. The executor checks each field against the user's message and records matches.

**Rationale:** Makes the extraction logic explicit and auditable, matching how the system prompt instructs the LLM.

### D5: Reset task unchecks all checkboxes in tasks.md

Same pattern as the previous spec — the final task rewrites `tasks.md` replacing `- [x]` with `- [ ]`.

**Rationale:** Proven idempotent mechanism.

## Risks / Trade-offs

- **[Single-turn only]** → Accepted. Multi-turn would require state persistence outside OpenSpec's scope.
- **[Knowledge base results are approximate]** → The task instructs the executor to read `summary.md` and perform keyword matching. Results may differ from the agent's exact scoring. This is acceptable for a workflow spec.
- **[Subjective interpretation in intent classification]** → Mitigated by providing explicit trigger phrases for each intent category, directly from the system prompt.
