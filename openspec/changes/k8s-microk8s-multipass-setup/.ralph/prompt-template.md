# Ralph Wiggum Task Execution - Iteration {{iteration}} / {{max_iterations}}

Change directory: /home/ncheaz/git/dkp-demo/openspec/changes/k8s-microk8s-multipass-setup

## OpenSpec Artifacts Context

Include full context from openspec artifacts in /home/ncheaz/git/dkp-demo/openspec/changes/k8s-microk8s-multipass-setup:
- Read /home/ncheaz/git/dkp-demo/openspec/changes/k8s-microk8s-multipass-setup/proposal.md for the overall project goal
- Read /home/ncheaz/git/dkp-demo/openspec/changes/k8s-microk8s-multipass-setup/design.md for the technical design approach
- Read /home/ncheaz/git/dkp-demo/openspec/changes/k8s-microk8s-multipass-setup/specs/*/spec.md for the detailed specifications

## Invocation-Time PRD Snapshot

{{base_prompt}}

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

## Commit Contract

{{commit_contract}}

{{context}}
