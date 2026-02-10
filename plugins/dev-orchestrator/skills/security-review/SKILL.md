---
name: security-review
description: >
  Security audit skill. When triggered by '/security-review', '보안 검사', 'security audit',
  or '취약점 분석', this skill performs a thorough security analysis including OWASP Top 10
  checks, dependency vulnerability scanning, and attack surface mapping.
---

# Security Review — Vulnerability Analysis

Performs comprehensive security analysis with OWASP Top 10 methodology.

## Workflow

### Step 1: Define Audit Scope

Use `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "What is the security audit scope?",
      "header": "Scope",
      "options": [
        {"label": "Full audit (Recommended)", "description": "OWASP Top 10 + dependency check + configuration review"},
        {"label": "Code only", "description": "Focus on code-level vulnerabilities (injection, auth, data exposure)"},
        {"label": "Dependencies", "description": "Check for known CVEs in project dependencies"},
        {"label": "Specific area", "description": "Focus on a specific security concern you describe"}
      ],
      "multiSelect": false
    }
  ]
}
```

### Step 2: Map Attack Surface

Dispatch **explorer** (Haiku) to identify:
- All input sources (API endpoints, form inputs, file uploads)
- All data sinks (database, file system, external services)
- Authentication and authorization boundaries
- Third-party integrations

### Step 3: Security Analysis

Dispatch **security-reviewer** (Opus) with:
- Attack surface map from Step 2
- All files containing input handling, auth, and data processing
- Package manifest (package.json, requirements.txt, etc.)
- Configuration files (environment, CORS, security headers)

### Step 4: Dependency Check

Run dependency vulnerability check via Bash:
- `npm audit` for Node.js projects
- `pip-audit` or `safety check` for Python projects
- `cargo audit` for Rust projects

Include results in the final report.

### Step 5: Present Security Report

Present the security-reviewer's structured report with:
- Severity-rated vulnerabilities (Critical/High/Medium/Low)
- OWASP category mapping
- Attack scenarios for each vulnerability
- Remediation code snippets
- Dependency vulnerability findings
