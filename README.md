# CMDSPACE Plugins

Claude Code plugins by [CMDSPACE](https://cmdspace.kr) (Yohan Koo).

## Available Plugins

### research-pipeline

Research-to-Publication Pipeline following the CMDS Process (Connect - Merge - Develop - Share).

Orchestrates the full academic research workflow from literature discovery to journal submission using 5 specialized sub-agents.

| Phase | Agent | Model | Role |
|-------|-------|-------|------|
| 1. Connect | literature-scout | haiku | PubMed/Scholar/Pinecone literature search |
| 2. Merge | literature-analyst | sonnet | Paper analysis, synthesis matrix, literature review |
| 3. Develop | manuscript-architect | opus | Manuscript structure design and drafting |
| 4. Edit | manuscript-editor | sonnet | 5-pass review and revision |
| 5. Share | publication-formatter | sonnet | Journal-specific formatting and submission prep |

**Skills included:**

| Skill | Usage |
|-------|-------|
| `/research-pipeline` | Main orchestrator (full 5-phase pipeline) |
| `/lit-search` | Standalone literature search |
| `/lit-review` | Standalone literature review |
| `/citation-manager` | Citation formatting and audit |
| `/journal-formatter` | Journal-specific submission formatting |

**MCP integrations:** PubMed, Firecrawl, Pinecone

---

### dev-orchestrator

Autonomous Development Orchestrator with 3-Tier agent system (Opus/Sonnet/Haiku).

Provides 13 specialized agents and 12 skills for the full SDLC — from planning and architecture through implementation, testing, review, and documentation.

| Tier | Agents | Model | Role |
|------|--------|-------|------|
| 1. Brain | planner, architect, critic, security-reviewer | opus | Strategic planning, architecture, security |
| 2. Hand | executor, code-reviewer, designer, researcher, build-fixer | sonnet | Implementation, review, design |
| 3. Eye | explorer, tdd-guide, qa-tester, writer | haiku | Search, testing, documentation |

**Skills included:**

| Category | Skills |
|----------|--------|
| Execution Modes | `/autopilot`, `/focus`, `/pipeline` |
| Planning | `/plan`, `/decompose`, `/estimate` |
| Quality | `/code-review`, `/security-review`, `/tdd` |
| Exploration | `/deepsearch`, `/deepinit`, `/hud` |

## Installation

```bash
# Add marketplace
/plugins marketplace add johnfkoo951/cmdspace-plugins

# Install plugin
/plugins install research-pipeline@cmdspace-plugins
/plugins install dev-orchestrator@cmdspace-plugins
```

## License

MIT
