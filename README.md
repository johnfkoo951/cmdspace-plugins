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

## Installation

```bash
# Add marketplace
/plugins marketplace add johnfkoo951/cmdspace-plugins

# Install plugin
/plugins install research-pipeline@cmdspace-plugins
```

## License

MIT
