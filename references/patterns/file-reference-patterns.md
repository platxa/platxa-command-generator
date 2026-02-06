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

## Pattern: Glob References

Users can reference multiple files using glob patterns:

```
# Single file
/review @src/auth.ts

# Directory (all files in directory)
/review @src/components/

# Glob pattern (matching files)
/review @./src/**/*.test.ts

# Multiple glob patterns
/review @./src/**/*.ts @./tests/**/*.ts
```

### Example: Glob-Based Analysis

```markdown
---
description: analyze all test files for coverage patterns
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Test Analysis

Analyze the following test files:

@file

For each test file, check:
1. Are all exported functions tested?
2. Are edge cases covered?
3. Are mocks properly cleaned up?
```

Usage: `/test-analysis @./src/**/*.test.ts`

### Supported @file Formats

| Format | Example | Resolves To |
|--------|---------|-------------|
| Single file | `@src/auth.ts` | Contents of one file |
| Directory | `@src/components/` | All files in directory |
| Glob | `@./src/**/*.ts` | All matching files |
| Multiple | `@file1.ts @file2.ts` | Contents of both files |

## Best Practices

- Explain what the referenced content represents
- Provide instructions for what to do with the content
- Handle the case where no file is referenced
- Keep command instructions concise since @file adds tokens
