# CMDSPACE Plugins

[![한국어](https://img.shields.io/badge/lang-한국어-green)](README.ko.md) [![English](https://img.shields.io/badge/lang-English-blue)](README.md)

Claude Code plugins by [CMDSPACE](https://cmdspace.work) (Yohan Koo).

## Available Plugins

| Plugin | What it does |
|---|---|
| [lecture-asset](plugins/lecture-asset/) | Turn a finished lecture's transcript into Obsidian knowledge assets: hub note, preserved transcript, atomic claim cards, Bases index, closing gate |
| [research-pipeline](plugins/research-pipeline/) | Research-to-publication pipeline with 5 sub-agents |
| [dev-orchestrator](plugins/dev-orchestrator/) | 3-tier agent system for the full software development lifecycle |

### lecture-asset

Turns a finished lecture into notes you will reuse. One talk becomes a hub note that summarizes and indexes it, the raw transcript kept byte-for-byte, 8 to 16 claim cards (one claim per card, titled as a sentence) linked into the rest of your vault, and one Obsidian Bases view across all talks. A read-only closing gate catches missed steps. Uses only core Obsidian features.

| Skill | Usage |
|-------|-------|
| `lecture-asset` | Say "강의 자산화해줘" or "turn this talk transcript into lecture assets" with a transcript |

Includes a fictional [sample vault](plugins/lecture-asset/examples/sample-vault/). Details: [plugins/lecture-asset](plugins/lecture-asset/).

---

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
/plugin marketplace add johnfkoo951/cmdspace-plugins

# Install plugin
/plugin install lecture-asset@cmdspace-plugins
/plugin install research-pipeline@cmdspace-plugins
/plugin install dev-orchestrator@cmdspace-plugins
```

On Claude Code 2.1.275 or later, one line per plugin also works: `/plugin install lecture-asset --marketplace johnfkoo951/cmdspace-plugins`.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Author

Yohan Koo (CMDSPACE) · <https://cmdspace.work>

## License

MIT
