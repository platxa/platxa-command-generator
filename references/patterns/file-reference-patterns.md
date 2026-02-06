# File Reference Patterns

Patterns for using @file references in commands.

## What @file Does

When a user types `/command @somefile.ts`, the contents of `somefile.ts` are injected into the command prompt before Claude processes it.

## Pattern: Analyze Referenced File

```markdown
---
description: review code quality of referenced file
allowed-tools:
  - Read
  - Grep
---

# Code Review

Review the following code for quality issues:

@file

## Review Criteria

1. Check naming conventions
2. Verify error handling
3. Assess test coverage
4. Identify code smells
```

## Pattern: Transform Referenced Content

```markdown
---
description: convert configuration to new format
allowed-tools:
  - Read
  - Write
---

# Config Migrator

Convert the following configuration to the new format:

@file

Write the converted output to the same path with `.new` extension.
```

## Pattern: Use as Context

```markdown
---
description: generate tests based on source file
allowed-tools:
  - Read
  - Write
  - Bash
---

# Generate Tests

Source code to test:

@file

Generate comprehensive tests for the above code.
Write tests to the corresponding test directory.
```

## Pattern: Multiple References

Users can provide multiple @file references:

```markdown
# Compare Files

Compare the following files and highlight differences:

@file

Provide a summary of:
- Structural differences
- Logic differences
- Missing/extra elements
```

## Best Practices

- Explain what the referenced content represents
- Provide instructions for what to do with the content
- Handle the case where no file is referenced
- Keep command instructions concise since @file adds tokens
