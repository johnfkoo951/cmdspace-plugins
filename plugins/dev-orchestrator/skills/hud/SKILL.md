---
name: hud
description: >
  Status display and session overview skill. When triggered by '/hud', '상태 표시',
  'show status', or '현재 상황', this skill displays a dashboard-style overview of
  the current project state, active tasks, agent usage, and tier distribution.
---

# HUD — Status Display

Displays a dashboard-style overview of the current development session.

## Workflow

### Step 1: Gather State

Collect information from multiple sources in parallel:

1. **Git status**: Current branch, uncommitted changes, recent commits
2. **Project info**: Tech stack, file counts, dependency status
3. **Task list**: Current tasks and their status (via TaskList)
4. **Active context**: What files have been read/modified in this session

### Step 2: Display Dashboard

```
╔══════════════════════════════════════════════════════════╗
║ dev-orchestrator HUD                                     ║
╠══════════════════════════════════════════════════════════╣
║ Project: [name]          Branch: [branch]                ║
║ Stack: [language/framework]                              ║
╠══════════════════════════════════════════════════════════╣
║ Git Status                                               ║
║ ├── Modified:  [N] files                                 ║
║ ├── Staged:    [N] files                                 ║
║ └── Untracked: [N] files                                 ║
╠══════════════════════════════════════════════════════════╣
║ Task Progress                                            ║
║ ├── Pending:     [N]                                     ║
║ ├── In Progress: [N]                                     ║
║ └── Completed:   [N]                                     ║
╠══════════════════════════════════════════════════════════╣
║ Available Agents (13)                                    ║
║ ├── Tier 1 (Opus):   planner, architect, critic,        ║
║ │                     security-reviewer                   ║
║ ├── Tier 2 (Sonnet):  executor, code-reviewer, designer,║
║ │                     researcher, build-fixer             ║
║ └── Tier 3 (Haiku):  explorer, tdd-guide, qa-tester,    ║
║                       writer                              ║
╠══════════════════════════════════════════════════════════╣
║ Available Skills (12)                                    ║
║ ├── Modes:    /autopilot  /focus  /pipeline              ║
║ ├── Planning: /plan  /decompose  /estimate               ║
║ ├── Quality:  /code-review  /security-review  /tdd       ║
║ └── Utility:  /deepsearch  /deepinit  /hud               ║
╚══════════════════════════════════════════════════════════╝
```

### Step 3: Suggest Next Actions

Based on the current state, suggest relevant next actions:
- If there are uncommitted changes → suggest `/code-review`
- If there are failing tests → suggest dispatching build-fixer
- If the project has no docs → suggest `/deepinit`
- If there are pending tasks → suggest continuing with the next task
