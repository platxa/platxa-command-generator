---
description: run tests for a specific file or module
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
argument-hint: [file-or-pattern]
---

# Test File

Run tests related to the specified file or pattern.

Target: $1

## Guardrails

- Read the test configuration before running to understand the test framework
- Never modify test files unless asked

## Workflow

### Step 1: Identify Test Framework

Check for `pytest.ini`, `pyproject.toml`, `jest.config.*`, or `vitest.config.*`
to determine the test runner.

### Step 2: Find Related Tests

Use Glob and Grep to find test files matching `$1`:
- Python: `tests/test_$1.py` or `tests/**/test_$1.py`
- JS/TS: `$1.test.ts`, `$1.spec.ts`, `__tests__/$1.test.ts`

### Step 3: Run Tests

Execute the appropriate test command for the matched files.

## Default Behavior

If no argument provided, auto-detect the test framework and run the full test suite.

## Verification

- Check exit code (0 = all passed)
- Report number of passed/failed/skipped tests

## Output

Show test results with pass/fail counts and any failure details.
