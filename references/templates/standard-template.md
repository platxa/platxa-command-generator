# Standard Command Template

Template for commands with frontmatter that scope tools and provide description.

## When to Use

- Commands that should restrict which tools Claude uses
- Commands that benefit from a description shown in help
- Most production commands

## Template

```markdown
---
description: {lowercase-verb phrase ≤60 chars}
allowed-tools:
  - {Tool1}
  - {Tool2}
---

# {Command Title}

{One-line purpose statement.}

## Context

{When to use this command and what it does.}

## Workflow

### Step 1: {Action Name}

{Specific instructions with tool usage}

### Step 2: {Action Name}

{Specific instructions with tool usage}

### Step 3: {Action Name}

{Specific instructions with tool usage}

## Output

{Expected output format and content.}
```

## Example

```markdown
---
description: analyze test coverage and identify gaps
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Test Coverage Analyzer

Analyze the project's test coverage and identify untested code paths.

## Context

Use when you want to understand which parts of the codebase lack tests
and prioritize test writing efforts.

## Workflow

### Step 1: Discover Test Files

Use Glob to find all test files matching `**/test_*.py` or `**/*.test.ts`.

### Step 2: Map Source to Tests

For each source file, check if a corresponding test file exists.
Report files with no test coverage.

### Step 3: Analyze Coverage Depth

For tested files, check if tests cover:
- Happy path
- Error cases
- Edge cases
- Integration points

## Output

Present findings as a table:

| File | Has Tests | Coverage Level | Priority |
|------|-----------|---------------|----------|
| src/auth.py | Yes | Partial | Medium |
| src/billing.py | No | None | High |
```

## Key Characteristics

- Has `---` frontmatter with description and/or allowed-tools
- description starts with lowercase verb
- Tools are scoped to what the command actually needs
- Most common command type for team workflows
