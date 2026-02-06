# Parameterized Command Template

Template for commands that accept user arguments via $1, $2, or $ARGUMENTS.

## When to Use

- Commands that operate on a user-specified target (file, module, pattern)
- Commands that need runtime configuration
- Commands invoked as `/command-name some-argument`

## Template

```markdown
---
description: {lowercase-verb phrase ≤60 chars}
allowed-tools:
  - {Tool1}
  - {Tool2}
argument-hint: [{arg1 description}]
---

# {Command Title}

Target: $1

## Context

{When to use this command. Explain what $1 represents.}

## Workflow

### Step 1: Validate Input

Verify that `$1` is valid:
- {Validation check 1}
- {Validation check 2}

### Step 2: Process Target

{Instructions using $1}

### Step 3: Report Results

{Output format}

## Default Behavior

If no argument provided:
{What to do when $1 is empty — detect automatically or ask user}
```

## Example

```markdown
---
description: generate unit tests for specified module
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
argument-hint: [module-path]
---

# Generate Tests

Generate comprehensive unit tests for: $1

## Context

Creates pytest test files for the specified Python module.
Argument is a path relative to the project root.

## Workflow

### Step 1: Read Source Module

Read the file at `$1` and identify all public functions and classes.

### Step 2: Analyze Dependencies

Check imports and identify what needs mocking vs real execution.

### Step 3: Generate Test File

Create a test file at `tests/test_{basename}.py` with:
- One test class per source class
- Tests for happy path, error cases, and edge cases
- Proper fixtures and parametrize decorators

### Step 4: Validate

Run `pytest tests/test_{basename}.py -v` to verify tests pass.

## Default Behavior

If no module path provided, ask the user which module to test.
```

## Multiple Arguments

For commands with multiple arguments:

```markdown
argument-hint: [source] [destination]
---

# Copy and Transform

Source: $1
Destination: $2
Full args: $ARGUMENTS
```

## Key Characteristics

- Uses `argument-hint` in frontmatter for user guidance
- References `$1`, `$2`, or `$ARGUMENTS` in body
- Always includes fallback behavior for missing arguments
- argument-hint uses bracket notation: `[arg]` for optional, `<arg>` avoided
