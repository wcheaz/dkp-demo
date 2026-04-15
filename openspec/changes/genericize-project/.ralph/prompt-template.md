# Ralph Wiggum Task Execution - Iteration {{iteration}} / {{max_iterations}}

Change directory: /home/ncheaz/git/dkp-demo/openspec/changes/genericize-project

## OpenSpec Artifacts Context

Include full context from openspec artifacts in /home/ncheaz/git/dkp-demo/openspec/changes/genericize-project:
- Read /home/ncheaz/git/dkp-demo/openspec/changes/genericize-project/proposal.md for the overall project goal
- Read /home/ncheaz/git/dkp-demo/openspec/changes/genericize-project/design.md for the technical design approach
- Read /home/ncheaz/git/dkp-demo/openspec/changes/genericize-project/specs/*/spec.md for the detailed specifications

## Task List

{{tasks}}

## Fresh Task Context

{{task_context}}

## Instructions

1. **Identify** current task:
   - Find any task marked as [/] (in progress)
   - If no task is in progress, pick the first task marked as [ ] (incomplete)
   - Mark the task as [/] in the tasks file before starting work

2. **Implement** the current task directly:
   - Read the relevant OpenSpec artifacts for context (proposal.md, design.md, specs)
   - Make the smallest maintainable change that fully satisfies the current task
   - Run the most relevant validation or tests for the task before claiming completion

3. **Complete** task:
   - Verify that the implementation meets the requirements
   - When the task is successfully completed, mark it as [x] in the tasks file
   - Create a git commit using the required format below
   - Output: `<promise>{{task_promise}}</promise>`

4. **Continue** to the next task:
   - The loop will continue with the next iteration
   - Find the next incomplete task and repeat the process

## Critical Rules

- Work on ONE task at a time from the task list
- Read the full tasks file every iteration; do not rely on memory from prior iterations
- Do not rely on editor-specific slash commands or local-only skills; follow this prompt directly
- Treat tasks.md as the only source of truth for task state
- ONLY output `<promise>{{task_promise}}</promise>` when the current task is complete and marked as [x]
- ONLY output `<promise>{{completion_promise}}</promise>` when ALL tasks are [x]
- Output promise tags DIRECTLY - do not quote them, explain them, or say you "will" output them
- Do NOT lie or output false promises to exit the loop
- If stuck, try a different approach
- Check your work before claiming completion

## CRITICAL: Git Commit Format (MANDATORY)

When making git commits, you MUST use this EXACT format:

```
Ralph iteration <N>: <brief description of work completed>

Tasks completed:
- [x] <task.number> <task description text>
- [x] <task.number> <task description text>
...
```

**Requirements:**
1. Use iteration number from Ralph's state (e.g., "Ralph iteration 7")
2. Include a BRIEF description summarizing what was done
3. List ALL completed tasks with their numbers and full descriptions
4. Use the EXACT format: "- [x] <task.number> <task description>"
5. Read the "## Completed Tasks for Git Commit" section from the PRD for the task list

**FORBIDDEN:**
- DO NOT use generic messages like "work in progress" or "iteration N"
- DO NOT skip task numbers
- DO NOT truncate task descriptions
- DO NOT create commits without task information

**Example:**
```
Ralph iteration 7: Implement unit tests for response processing

Tasks completed:
- [x] 11.6 Write unit test for personality state management
- [x] 11.7 Write unit test for personality validation
- [x] 11.8 Write unit test for system prompt validation
```

{{context}}
