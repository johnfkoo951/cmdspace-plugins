---
name: deepsearch
description: >
  Multi-strategy deep code search skill. When triggered by '/deepsearch', '깊은 검색',
  'deep search', or '코드 찾아줘', this skill applies multiple search strategies —
  structural (AST-like pattern), textual (regex), semantic (by meaning), and historical
  (git history) — to find code that simple grep can't.
---

# Deep Search — Multi-Strategy Code Search

Applies multiple search strategies to find code that simple text search misses.

## Workflow

### Step 1: Understand Search Intent

Use `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "What are you looking for?",
      "header": "Search Type",
      "options": [
        {"label": "Pattern/Usage", "description": "Find all places where a pattern is used (e.g., all async functions, all API calls)"},
        {"label": "Concept/Feature", "description": "Find code related to a concept (e.g., 'authentication', 'caching')"},
        {"label": "Changed code", "description": "Find code that was recently modified or relates to a specific change"},
        {"label": "Dead code", "description": "Find unused functions, imports, or variables"}
      ],
      "multiSelect": false
    }
  ]
}
```

### Step 2: Apply Search Strategies

Dispatch **explorer** (Haiku) with instructions to apply multiple strategies in parallel:

**Strategy 1: Textual Search**
- Use Grep with regex patterns
- Search for exact names, patterns, and keywords

**Strategy 2: Structural Search**
- Use Glob for file pattern matching
- Trace import/export chains
- Follow function call hierarchies

**Strategy 3: Semantic Search**
- Search by concept (related terms, synonyms)
- Look in comments, docstrings, variable names
- Search for patterns that implement the concept

**Strategy 4: Historical Search** (if applicable)
- Use `git log --all -S "term"` for code that appeared/disappeared
- Use `git log --follow` for file history
- Use `git blame` for authorship and timing

### Step 3: Rank and Present Results

```markdown
## Search Results: [Query]

### Strategy Results Summary
| Strategy | Matches | Top Result |
|----------|---------|------------|
| Textual | [N] | [file:line] |
| Structural | [N] | [file:line] |
| Semantic | [N] | [file:line] |
| Historical | [N] | [commit] |

### Top Results (by relevance)
1. **[file:line]** — [context snippet]
   - Found by: [strategy]
   - Relevance: [why this matches]

2. **[file:line]** — [context snippet]
   ...

### Related Files
- [Files that are connected to the search results]
```
