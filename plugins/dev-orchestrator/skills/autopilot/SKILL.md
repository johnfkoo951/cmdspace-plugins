---
name: autopilot
description: >
  Fully autonomous execution mode. When triggered by '/autopilot', 'autopilot mode',
  '자율 실행', or '알아서 해줘', this skill takes a development task and autonomously plans,
  implements, tests, and delivers without user intervention. Uses the planner agent to
  decompose work, then dispatches appropriate agents in parallel where possible.
---

# Autopilot — Fully Autonomous Execution Mode

Autopilot mode handles a development task end-to-end without user intervention.

## Workflow

### Step 1: Gather Requirements

Use `AskUserQuestion` to understand the task:

```json
{
  "questions": [
    {
      "question": "What task should autopilot handle?",
      "header": "Task",
      "options": [
        {"label": "Implement feature", "description": "Build a new feature from scratch"},
        {"label": "Fix bugs", "description": "Diagnose and fix one or more bugs"},
        {"label": "Refactor code", "description": "Restructure existing code without changing behavior"},
        {"label": "Full cycle", "description": "Plan → Implement → Test → Review → Document"}
      ],
      "multiSelect": false
    },
    {
      "question": "What quality level is required?",
      "header": "Quality",
      "options": [
        {"label": "Production (Recommended)", "description": "Full tests, code review, documentation. Uses Sonnet/Opus."},
        {"label": "Prototype", "description": "Working code, minimal tests. Uses mostly Haiku/Sonnet."},
        {"label": "Maximum", "description": "Production + security review + critic review. Uses Opus heavily."}
      ],
      "multiSelect": false
    }
  ]
}
```

### Step 2: Plan

Dispatch the **planner** agent (Opus) to:
1. Analyze the codebase context
2. Decompose the task into subtasks
3. Assign tiers and agents to each subtask
4. Identify parallel execution opportunities
5. Define quality gates

### Step 3: Execute

Based on the plan, dispatch agents in the optimal order:

**Parallel phase** (independent tasks):
- Dispatch multiple agents simultaneously using parallel `Task` calls
- Explorer (Haiku) for codebase scanning
- Researcher (Sonnet) for technical investigation if needed

**Sequential phase** (dependent tasks):
- Executor (Sonnet) for implementation
- Build-fixer (Sonnet) if build errors occur
- TDD-guide (Haiku) for test writing

### Step 4: Quality Gates

After implementation, run quality checks:
- **Code Review**: Dispatch code-reviewer (Sonnet) on all changed files
- **Tests**: Run test suite via Bash
- **Build**: Verify clean build
- **Security** (if Maximum quality): Dispatch security-reviewer (Opus)

If quality gates fail, dispatch appropriate agents to fix issues and re-check.

### Step 5: Deliver

1. Summarize all changes made
2. List files created/modified
3. Report test results
4. Report quality gate outcomes
5. Suggest next steps if any

## Guardrails

- **Cost awareness**: Track agent dispatches. If exceeding 10 agent calls, pause and summarize progress
- **Safety**: Never auto-push to git. Never modify deployment configs without confirmation
- **Scope control**: If the task grows beyond the original scope, pause and ask the user
- **Rollback**: Keep track of all changes for potential rollback

## Tier Allocation Strategy

| Phase | Default Tier | Escalate to |
|-------|-------------|-------------|
| Planning | Opus | — |
| Exploration | Haiku | Sonnet (complex codebase) |
| Implementation | Sonnet | Opus (complex algorithms) |
| Testing | Haiku | Sonnet (integration tests) |
| Review | Sonnet | Opus (security-critical) |
