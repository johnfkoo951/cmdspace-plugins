---
name: code-review
description: >
  Deep code review skill. When triggered by '/code-review', '코드 리뷰', 'review this code',
  or '코드 품질 점검', this skill performs a thorough code quality review with structured
  findings, severity ratings, and actionable recommendations.
---

# Code Review — Deep Quality Analysis

Performs thorough code quality review with structured findings.

## Workflow

### Step 1: Determine Review Scope

Use `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "What should I review?",
      "header": "Scope",
      "options": [
        {"label": "Recent changes (Recommended)", "description": "Review uncommitted changes or recent commits"},
        {"label": "Specific files", "description": "Review specific files or directories you specify"},
        {"label": "Full project", "description": "Broad quality assessment of the entire codebase"},
        {"label": "PR review", "description": "Review changes in a pull request"}
      ],
      "multiSelect": false
    },
    {
      "question": "What aspects should I focus on?",
      "header": "Focus",
      "options": [
        {"label": "All aspects (Recommended)", "description": "Readability, performance, maintainability, best practices"},
        {"label": "Performance", "description": "Focus on performance issues, N+1 queries, memory leaks"},
        {"label": "Architecture", "description": "Focus on design patterns, SOLID principles, coupling"},
        {"label": "Readability", "description": "Focus on naming, structure, clarity"}
      ],
      "multiSelect": false
    }
  ]
}
```

### Step 2: Gather Code

Based on scope:
- **Recent changes**: Run `git diff` and `git status` to identify changed files
- **Specific files**: Read the specified files
- **Full project**: Dispatch explorer (Haiku) first, then review key files
- **PR review**: Use `gh pr diff` to get PR changes

### Step 3: Review

Dispatch **code-reviewer** (Sonnet) with the gathered code and focus area.

For "Full project" or "Architecture" focus, also dispatch **critic** (Opus) for deeper structural analysis.

### Step 4: Present Results

Present the code-reviewer's structured report with severity-rated findings.

If both code-reviewer and critic were dispatched, merge their findings into a single report with clear attribution.
