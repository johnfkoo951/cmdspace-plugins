---
name: pipeline
description: >
  Sequential pipeline execution mode. When triggered by '/pipeline', 'pipeline mode',
  '파이프라인', or '순차적으로 진행해줘', this skill chains agents in a defined sequence
  where each agent's output becomes the next agent's input. Best for structured workflows
  like plan → implement → review → test.
---

# Pipeline — Sequential Chain Execution Mode

Pipeline mode chains agents in a defined sequence. Each step's output feeds into the next step's input. Best for structured, multi-phase workflows.

## Workflow

### Step 1: Select Pipeline Template

Use `AskUserQuestion` to choose a workflow:

```json
{
  "questions": [
    {
      "question": "Which pipeline workflow do you want to run?",
      "header": "Pipeline",
      "options": [
        {"label": "Full SDLC (Recommended)", "description": "Plan → Implement → Test → Review → Document"},
        {"label": "Quality Gate", "description": "Code Review → Security Review → Critic Review"},
        {"label": "Research & Implement", "description": "Research → Architect → Implement → Test"},
        {"label": "Bug Fix", "description": "Explore → Diagnose → Fix → Test → Review"}
      ],
      "multiSelect": false
    }
  ]
}
```

### Step 2: Configure Pipeline

Based on the selected template, configure the pipeline stages:

#### Full SDLC Pipeline
```
Stage 1: planner (Opus)     → Execution plan
Stage 2: executor (Sonnet)  → Implementation
Stage 3: tdd-guide (Haiku)  → Test suite
Stage 4: code-reviewer (Sonnet) → Quality report
Stage 5: writer (Haiku)     → Documentation
```

#### Quality Gate Pipeline
```
Stage 1: code-reviewer (Sonnet)     → Quality issues
Stage 2: security-reviewer (Opus)   → Security issues
Stage 3: critic (Opus)              → Design issues
  → Aggregate: Combined review report
```

#### Research & Implement Pipeline
```
Stage 1: researcher (Sonnet)  → Research report
Stage 2: architect (Opus)     → Design document
Stage 3: executor (Sonnet)    → Implementation
Stage 4: qa-tester (Haiku)    → Test results
```

#### Bug Fix Pipeline
```
Stage 1: explorer (Haiku)      → Affected files map
Stage 2: build-fixer (Sonnet)  → Root cause analysis
Stage 3: executor (Sonnet)     → Fix implementation
Stage 4: tdd-guide (Haiku)     → Regression tests
Stage 5: code-reviewer (Sonnet) → Fix verification
```

### Step 3: Execute Stages Sequentially

For each stage:
1. Dispatch the agent with the accumulated context from all previous stages
2. Wait for completion
3. Validate the output (quality gate check)
4. If validation fails, retry the stage or escalate tier
5. Pass output to next stage

### Step 4: Pipeline Report

After all stages complete:

```markdown
## Pipeline Execution Report

### Pipeline: [Template Name]
### Task: [Description]

| Stage | Agent | Tier | Status | Duration |
|-------|-------|------|--------|----------|
| 1. Plan | planner | Opus | ✅ Pass | — |
| 2. Implement | executor | Sonnet | ✅ Pass | — |
| 3. Test | tdd-guide | Haiku | ⚠️ 2 failures | — |
| 4. Review | code-reviewer | Sonnet | ✅ Pass | — |

### Key Outputs
- [Link/reference to each stage's output]

### Issues Found
- [Any issues discovered during pipeline execution]

### Next Steps
- [Recommended follow-up actions]
```

## Pipeline Rules

1. **Sequential only** — each stage waits for the previous one to complete
2. **Context accumulation** — each stage receives all previous outputs
3. **Fail-forward** — if a stage fails, report it but continue (don't block the whole pipeline)
4. **Tier escalation** — if a stage fails twice, retry with a higher tier
5. **Output preservation** — every stage's output is preserved for the final report
