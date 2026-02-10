---
name: plan
description: >
  Implementation planning skill. When triggered by '/plan', '계획 세워줘', 'create a plan',
  or '구현 계획', this skill analyzes a development request and produces a structured
  execution plan with task decomposition, tier assignments, dependency graphs, and
  time/cost estimates.
---

# Plan — Implementation Planning

Creates a structured execution plan for any development task.

## Workflow

### Step 1: Gather Planning Context

Use `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "What are you planning to build or change?",
      "header": "Scope",
      "options": [
        {"label": "New feature", "description": "Building something new from scratch"},
        {"label": "Refactor", "description": "Restructuring existing code without changing behavior"},
        {"label": "Migration", "description": "Moving between technologies, versions, or architectures"},
        {"label": "Bug fix campaign", "description": "Systematic resolution of multiple related issues"}
      ],
      "multiSelect": false
    },
    {
      "question": "How detailed should the plan be?",
      "header": "Detail Level",
      "options": [
        {"label": "High-level (Recommended)", "description": "Phases, key tasks, and dependencies. Good for getting started."},
        {"label": "Detailed", "description": "Every file to create/modify, specific implementation steps."},
        {"label": "Sprint-ready", "description": "Detailed with effort estimates, broken into sprint-sized chunks."}
      ],
      "multiSelect": false
    }
  ]
}
```

### Step 2: Explore the Codebase

Dispatch **explorer** (Haiku) to:
- Map the current project structure
- Identify relevant files and patterns
- Detect the tech stack and conventions

### Step 3: Create the Plan

Dispatch **planner** (Opus) with the exploration results and user requirements to produce:

1. **Summary**: What will be done and why
2. **Prerequisites**: What must exist before starting
3. **Phases**: Grouped tasks with dependency arrows
4. **Task Details**: For each task — agent, tier, complexity, files involved
5. **Quality Gates**: Checkpoints between phases
6. **Risks**: What could go wrong and how to mitigate
7. **Estimates**: Rough complexity scores (not time predictions)

### Step 4: Present the Plan

Present the plan using the planner agent's output format. Ask the user to approve, modify, or reject the plan before any execution begins.

## Output Format

See the planner agent's execution plan format in `agents/planner.md`.

## Follow-up Actions

After plan approval, the user can:
- Run `/autopilot` to execute the plan autonomously
- Run `/pipeline` to execute the plan stage by stage
- Run individual tasks manually with specific agents
