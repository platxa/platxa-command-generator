# Argument Patterns

Patterns for handling $1, $2, and $ARGUMENTS in commands.

## Argument Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `$1` | First positional argument | `/deploy staging` → $1 = "staging" |
| `$2` | Second positional argument | `/copy src dest` → $2 = "dest" |
| `$ARGUMENTS` | Full argument string | `/search foo bar` → $ARGUMENTS = "foo bar" |

## $1/$2 vs $ARGUMENTS

**Positional (`$1`, `$2`)**: Splits user input on spaces. Each word becomes a separate argument.
- `/deploy staging eu-west` → `$1` = "staging", `$2` = "eu-west"
- Best for: structured input with distinct parameters

**Full string (`$ARGUMENTS`)**: Preserves the entire input as-is, including spaces.
- `/search class UserAuth` → `$ARGUMENTS` = "class UserAuth"
- Best for: search queries, free-text input, messages

**When to use which**:

| Scenario | Use | Why |
|----------|-----|-----|
| Distinct parameters (file, target) | `$1`, `$2` | Each param has a clear role |
| Search queries with spaces | `$ARGUMENTS` | Spaces are part of the input |
| Single argument (file path) | `$1` | Simple, one value |
| Free-form text (commit message) | `$ARGUMENTS` | Preserves original phrasing |
| Mixed: structured + free-text | `$1` + `$ARGUMENTS` | First arg for target, rest for details |

## Pattern: Single Required Argument

```markdown
---
argument-hint: [file-path]
---

# Analyze File

Analyze: $1

Read the file at `$1` and provide analysis.

If no file specified, ask the user which file to analyze.
```

## Pattern: Single Optional Argument

```markdown
---
argument-hint: [pattern]
---

# Run Tests

Run tests matching: $1

If no pattern specified, run all tests.

```bash
pytest tests/ -k "$1" -v    # With pattern
pytest tests/ -v             # Without pattern
```

## Pattern: Multiple Arguments

```markdown
---
argument-hint: [source] [destination]
---

# Migrate Data

Source: $1
Destination: $2

Migrate data from $1 to $2.

If source not specified, use the default database.
If destination not specified, ask the user.
```

## Pattern: Full Argument String

```markdown
---
argument-hint: [search query]
---

# Search Codebase

Search for: $ARGUMENTS

Use Grep to find all occurrences of the search query.
$ARGUMENTS preserves the full string including spaces.
```

## Fallback Handling

Always handle the case where arguments are missing:

```markdown
## Fallback Behavior

1. If $1 is empty → detect automatically from context
2. If $1 is empty → ask the user via AskUserQuestion
3. If $1 is empty → use a sensible default
4. If $1 is invalid → report error and show usage
```

## Best Practices

- Always document what each argument represents
- Provide fallback behavior for missing arguments
- Match argument-hint labels to actual usage
- Use $ARGUMENTS when spaces in input matter
- Validate arguments before using them
