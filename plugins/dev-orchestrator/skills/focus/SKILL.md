---
name: focus
description: >
  Deep focus mode using a single high-tier agent for complex problems requiring sustained
  reasoning. When triggered by '/focus', 'focus mode', '집중 모드', or '깊이 생각해줘',
  this skill dedicates a single Opus-tier agent to one problem without context switching,
  multi-agent coordination, or parallelization.
---

# Focus — Single Agent Deep Reasoning Mode

Focus mode applies concentrated, deep reasoning to a single problem. No multi-agent coordination, no context switching — just one powerful agent thinking deeply.

## When to Use

- Architecture decisions requiring careful trade-off analysis
- Complex debugging that needs systematic root cause analysis
- Code that requires understanding deep domain logic
- Decisions with significant long-term consequences

## Workflow

### Step 1: Understand the Problem

Use `AskUserQuestion` to clarify:

```json
{
  "questions": [
    {
      "question": "What kind of deep analysis do you need?",
      "header": "Focus Area",
      "options": [
        {"label": "Architecture decision", "description": "Evaluate trade-offs and design a solution. Uses architect agent."},
        {"label": "Critical review", "description": "Find flaws and risks in existing design/code. Uses critic agent."},
        {"label": "Complex debugging", "description": "Systematic root cause analysis. Uses executor agent with Opus override."},
        {"label": "Security analysis", "description": "Deep security vulnerability assessment. Uses security-reviewer agent."}
      ],
      "multiSelect": false
    }
  ]
}
```

### Step 2: Set Up Context

Before dispatching the focused agent:
1. Read all relevant files to build comprehensive context
2. Gather any related documentation, ADRs, or specifications
3. Identify constraints and requirements

### Step 3: Dispatch Single Agent

Based on the focus area, dispatch ONE agent with **Opus tier**:

- **Architecture decision** → architect (Opus)
- **Critical review** → critic (Opus)
- **Complex debugging** → executor with Opus override
- **Security analysis** → security-reviewer (Opus)

Provide the agent with:
- Complete context (all relevant files already read)
- Clear problem statement
- Specific questions to answer or decisions to make
- Constraints and requirements

### Step 4: Present Results

The focused agent's output should be presented as-is, without additional agent processing. The value of focus mode is the depth of a single agent's analysis, not a pipeline.

## Key Principle

> Less is more. One agent thinking deeply about one problem produces better results than five agents skimming five aspects.

## Differences from Other Modes

| Aspect | Focus | Autopilot | Pipeline |
|--------|-------|-----------|----------|
| Agents | 1 | Many | Sequential chain |
| Tier | Always Opus | Mixed | Mixed |
| Speed | Slow, thorough | Fast, parallel | Medium |
| Best for | Decisions | Execution | Workflows |
