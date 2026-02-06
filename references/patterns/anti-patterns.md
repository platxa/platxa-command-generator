# Command Anti-Patterns

Common mistakes when writing Claude Code slash commands, with examples and fixes.

## 1. Kitchen-Sink Command

**Problem**: Cramming too many responsibilities into a single command.

**Symptoms**: Over 2000 tokens, 10+ tools in allowed-tools, multiple unrelated workflows.

**Bad**:
```markdown
---
description: lint, test, build, deploy, and notify slack
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - Task
  - TodoWrite
---

# Do Everything

1. Run linter and fix all issues
2. Run test suite
3. Build production bundle
4. Deploy to staging
5. Run smoke tests
6. Deploy to production
7. Post to Slack
```

**Fix**: Split into focused commands (`/lint`, `/test`, `/deploy-staging`, `/deploy-prod`) or create a workflow command that orchestrates them with clear phase boundaries.

## 2. Over-Correcting (Excessive Guardrails)

**Problem**: Adding so many safety checks that the command becomes unusable or painfully slow.

**Symptoms**: More guardrail text than actual instructions, multiple confirmation prompts, excessive pre-checks that rarely fail.

**Bad**:
```markdown
# Deploy

## Pre-Checks
- Verify git is installed
- Verify node is installed
- Verify npm is installed
- Check if user is logged in
- Check if branch exists
- Check if remote exists
- Check if CI passed
- Check disk space
- Verify network connectivity
- Confirm user intent
- Double-confirm user intent

## Actual Work
Deploy the thing.
```

**Fix**: Only guard against realistic failure modes. Trust the environment for basics (git/node installed). One confirmation for destructive actions is enough.

## 3. Trust-Verify Gap

**Problem**: Command makes changes without reading current state first, or reads state but doesn't verify after changes.

**Symptoms**: Overwrites existing work, doesn't detect conflicts, no verification step.

**Bad**:
```markdown
# Update Config

Write the following to config.json:
{"key": "value", "setting": true}
```

**Fix**: Always read before writing, verify after changing:
```markdown
# Update Config

## Step 1: Read Current State
Read config.json to understand existing settings.

## Step 2: Apply Changes
Merge the new settings with existing ones (don't overwrite).

## Verification
Read config.json again and confirm the changes are correct.
```

## 4. Vague Instructions (Under-Specification)

**Problem**: Command gives high-level goals without actionable steps, leaving Claude to guess the approach.

**Symptoms**: Single paragraph of instructions, no specific tool usage, no output format, inconsistent results across runs.

**Bad**:
```markdown
# Improve Code Quality

Look at the code and make it better. Fix any issues you find.
Focus on best practices.
```

**Fix**: Be specific about what to check, which tools to use, and what output to produce:
```markdown
# Lint and Fix

## Step 1: Identify Issues
Run `ruff check .` to find linting violations.

## Step 2: Auto-Fix
Run `ruff check . --fix` for auto-fixable issues.

## Step 3: Manual Fixes
For remaining issues, read each flagged file and apply the fix.

## Output
List all changes made, grouped by file.
```

## 5. Hardcoded Assumptions

**Problem**: Command assumes specific paths, tools, or project structure that won't work in other contexts.

**Symptoms**: Absolute paths, hardcoded tool versions, assumes specific framework or language.

**Bad**:
```markdown
# Run Tests

Run `cd /Users/john/projects/myapp && npm test`.
Open coverage report at /Users/john/projects/myapp/coverage/index.html.
```

**Fix**: Use relative paths, detect the environment, handle missing tools:
```markdown
# Run Tests

## Step 1: Detect Test Runner
Check for `package.json` (npm/pnpm), `pytest.ini`/`pyproject.toml` (pytest),
or `go.mod` (go test) to determine the test command.

## Step 2: Run Tests
Execute the appropriate test command from the project root.

## Default Behavior
If no test configuration is found, report which files were checked
and suggest setting up a test framework.
```

## Quick Reference

| Anti-Pattern | Signal | Fix |
|-------------|--------|-----|
| Kitchen-Sink | >2000 tokens, 10+ tools | Split into focused commands |
| Over-Correcting | More guards than work | Guard realistic failures only |
| Trust-Verify Gap | No read-before-write | Read state, act, verify |
| Under-Specification | Vague single paragraph | Specific steps with tools |
| Hardcoded Assumptions | Absolute paths, specific tools | Detect environment, use relative paths |
