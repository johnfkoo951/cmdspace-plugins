---
name: tdd
description: >
  Test-driven development skill. When triggered by '/tdd', 'TDD로 개발', 'test first',
  or '테스트 먼저 작성', this skill enforces the Red-Green-Refactor cycle — writing failing
  tests first, then implementing to satisfy them, then refactoring with confidence.
---

# TDD — Test-Driven Development

Enforces the Red-Green-Refactor cycle for quality-driven development.

## Workflow

### Step 1: Understand Requirements

Use `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "What are you building with TDD?",
      "header": "Target",
      "options": [
        {"label": "New function/class", "description": "Build a new unit from scratch with tests first"},
        {"label": "New feature", "description": "Build a feature across multiple files with test coverage"},
        {"label": "Add tests to existing code", "description": "Write tests for code that already exists"},
        {"label": "Fix bug with regression test", "description": "Write a test that reproduces the bug, then fix it"}
      ],
      "multiSelect": false
    }
  ]
}
```

### Step 2: RED — Write Failing Tests

Dispatch **tdd-guide** (Haiku) to:
1. Analyze the requirements
2. Identify test scenarios (happy path, edge cases, error cases)
3. Write the test file with all tests
4. Verify tests fail (RED state)

### Step 3: GREEN — Implement

Dispatch **executor** (Sonnet) with:
- The failing test file
- Requirement to make all tests pass
- Instruction to use the simplest possible implementation
- The existing codebase context for convention matching

After implementation, run tests via Bash to verify they pass.

### Step 4: REFACTOR

If tests pass, dispatch **code-reviewer** (Sonnet) to:
- Review the implementation for quality
- Suggest refactoring opportunities
- Verify test quality (are tests testing the right things?)

Apply refactoring suggestions, re-run tests to confirm they still pass.

### Step 5: Report

```markdown
## TDD Cycle Complete

### Tests Written: [N]
- ✅ Happy path: [N] tests
- ✅ Edge cases: [N] tests
- ✅ Error cases: [N] tests

### Coverage: [N]% (if measurable)

### Implementation Files
- [file:line — what was implemented]

### Refactoring Applied
- [What was improved after tests passed]
```
