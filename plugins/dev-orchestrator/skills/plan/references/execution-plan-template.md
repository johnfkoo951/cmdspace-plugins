# Execution Plan Template

## Execution Plan: [Title]

### Summary
[1-2 sentence overview of what will be done and why]

### Prerequisites
- [ ] [Context or setup required before starting]
- [ ] [Files to read or understand]
- [ ] [Dependencies to install]

---

### Phase 1: [Phase Name]
**Mode**: parallel | sequential
**Depends on**: — (none)

| # | Task | Agent | Tier | Complexity | Files |
|---|------|-------|------|------------|-------|
| 1.1 | [Specific, actionable description] | [agent-name] | [Opus/Sonnet/Haiku] | [1-10] | [file paths] |
| 1.2 | [Specific, actionable description] | [agent-name] | [Opus/Sonnet/Haiku] | [1-10] | [file paths] |

**Quality Gate**: [What must be true before moving to Phase 2]

---

### Phase 2: [Phase Name]
**Mode**: parallel | sequential
**Depends on**: Phase 1

| # | Task | Agent | Tier | Complexity | Files |
|---|------|-------|------|------------|-------|
| 2.1 | [Description] | [agent] | [tier] | [1-10] | [files] |

**Quality Gate**: [Criteria]

---

### Risks & Mitigations

| Risk | Impact (H/M/L) | Probability (H/M/L) | Mitigation |
|------|----------------|----------------------|------------|
| [What could go wrong] | [H/M/L] | [H/M/L] | [How to prevent or handle] |

### Rollback Strategy
[How to undo all changes if needed]

### Estimates
- Total tasks: [N]
- Parallel groups: [N]
- Tier distribution: Opus [N] / Sonnet [N] / Haiku [N]
