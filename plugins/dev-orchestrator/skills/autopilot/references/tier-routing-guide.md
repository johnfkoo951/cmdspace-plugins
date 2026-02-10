# Tier Routing Guide

## 3-Tier Model Strategy

The dev-orchestrator uses a 3-tier agent system to balance cost and quality.

## Tier Assignment Rules

### Tier 1: Opus (Brain)
**Use for**: Complex reasoning, strategic decisions, security-critical analysis

| Signal | Route to Opus |
|--------|---------------|
| Complexity score 7-10 | Yes |
| Architecture/design decisions | Yes |
| Security-sensitive code | Yes |
| Multiple valid approaches need evaluation | Yes |
| Previous tier failed twice | Yes (escalation) |

**Agents**: planner, architect, critic, security-reviewer

### Tier 2: Sonnet (Hand)
**Use for**: Implementation, code review, standard analysis

| Signal | Route to Sonnet |
|--------|-----------------|
| Complexity score 4-6 | Yes |
| Business logic implementation | Yes |
| Code review (non-security) | Yes |
| Bug fixing with context | Yes |
| UI component design | Yes |

**Agents**: executor, code-reviewer, designer, researcher, build-fixer

### Tier 3: Haiku (Eye/Foot)
**Use for**: Search, simple generation, repetitive tasks

| Signal | Route to Haiku |
|--------|----------------|
| Complexity score 1-3 | Yes |
| File/code search | Yes |
| Documentation generation | Yes |
| Boilerplate/CRUD | Yes |
| Test writing (standard) | Yes |

**Agents**: explorer, tdd-guide, qa-tester, writer

## Escalation Rules

```
Haiku fails × 2  →  Escalate to Sonnet
Sonnet fails × 2  →  Escalate to Opus
Opus fails × 2  →  Alert user, request guidance
```

## Cost Optimization

1. **Start low**: Default to the lowest tier that can handle the task
2. **Escalate on failure**: Only move up when the current tier can't handle it
3. **Parallel Haiku over single Sonnet**: For independent simple tasks, 3 Haiku agents are cheaper and faster than 1 Sonnet
4. **Opus for planning only**: Use Opus to plan, then delegate execution to lower tiers
