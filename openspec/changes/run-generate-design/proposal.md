## Why

The pydantic-ai agent in `agent/src/agent.py` follows a deterministic decision-making workflow: parse user input, classify intent, extract construction parameters, decide which tools to call (knowledge base query, pricing, design generation, reset), execute them in sequence, and format output as plain ASCII with no narration. We need to reverse-engineer that workflow into an OpenSpec spec so that an `opsx-apply` run walks a human or AI agent through the exact same decision loop and produces the same output — without writing or running any Python code.

## What Changes

- Create a standalone OpenSpec spec called `run-generate-design` that encodes the agent's full interaction workflow as executable tasks
- Each task represents one step in the agent's decision loop: intent classification, parameter extraction, tool invocation (simulated as structured output steps), and response formatting
- The spec is purely procedural — no code files are created or modified; the "output" is the structured response produced by following the tasks
- A final task unchecks all checkboxes so the spec can be rerun for a new user interaction

## Capabilities

### New Capabilities

- `intent-classification`: Determine whether the user's input requires a knowledge base query, a design generation, a pricing quote, a design modification, a design reset, or a general response
- `parameter-extraction`: Parse the user's input for construction parameters (building_type, floor_plan_dimensions, roof_type, roof_pitch, attic_usage, eaves_shape, wall_construction, location, overhang) using the agent's extraction rules
- `tool-execution-simulation`: For each classified intent, produce the same structured output the agent's tools would return — knowledge base search results, pricing calculation, design entry creation, parameter update, design modification, or design reset
- `response-formatting`: Format the final output according to the agent's strict output rules — plain ASCII, no emojis, no narration, one of three allowed output forms (design summary, missing-parameter question, or direct answer)
- `reset-task`: Final task that unchecks all task checkboxes in tasks.md for idempotent re-runs

### Modified Capabilities

(None — this is a net-new spec)

## Impact

- **Files created**: None (spec-only, no code)
- **Output**: The structured response text that the pydantic-ai agent would produce for the given user input
- **Dependencies**: Requires access to `agent/knowledge/trusses-ai-english/summary.md` for knowledge base simulation; requires the user's input message to process
