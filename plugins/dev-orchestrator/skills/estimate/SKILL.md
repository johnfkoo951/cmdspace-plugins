---
name: estimate
description: >
  Task estimation skill. When triggered by '/estimate', '추정해줘', 'estimate effort',
  or '이거 얼마나 복잡해?', this skill analyzes a development task and estimates complexity,
  agent tier distribution, and provides a confidence level for the estimate.
---

# Estimate — Complexity & Effort Estimation

Analyzes a development task and estimates complexity and resource requirements.

## Workflow

### Step 1: Explore the Scope

Dispatch **explorer** (Haiku) to:
- Count affected files and lines of code
- Identify integration points
- Map dependencies

### Step 2: Analyze Complexity

Dispatch **planner** (Opus) to evaluate:

1. **Scope Complexity**: How many files/components are involved?
2. **Logic Complexity**: How difficult is the business logic?
3. **Integration Complexity**: How many external systems are touched?
4. **Risk Complexity**: How much can go wrong?

### Step 3: Output Estimate

```markdown
## Estimate: [Task Description]

### Complexity Score: [1-10] ([Low/Medium/High/Very High])

### Breakdown
| Factor | Score (1-10) | Notes |
|--------|-------------|-------|
| Scope | [N] | [N files, N components affected] |
| Logic | [N] | [Simple CRUD / Complex algorithms / etc.] |
| Integration | [N] | [N external systems] |
| Risk | [N] | [Data loss risk, breaking changes, etc.] |

### Recommended Approach
- **Execution Mode**: [autopilot / pipeline / focus]
- **Tier Distribution**: Opus [N tasks] / Sonnet [N tasks] / Haiku [N tasks]
- **Agent Count**: [N] agents needed

### Confidence: [High / Medium / Low]
[Explanation of confidence level]

### Caveats
- [What might change the estimate]
```
