# Frontmatter Validator

Validation rules for command frontmatter fields.

## Validation Rules

### No Frontmatter (Valid for Basic)
- File starts with `#` heading (no `---`)
- All tools available by default
- No description shown in help

### Invalid Frontmatter (Always Error)
- Malformed YAML between `---` delimiters
- Unknown fields (not in allowed set)
- Wrong types (string where list expected)

### Field Validation

| Field | Type | Constraint | Error Level |
|-------|------|-----------|-------------|
| description | string | ≤60 chars | Error if over |
| description | string | starts with lowercase verb | Warning |
| description | string | no placeholders (TODO, TBD) | Error |
| allowed-tools | list | valid tool names only | Error |
| allowed-tools | list | Bash filter syntax valid | Error |
| argument-hint | string | bracket format [arg] | Error |
| model | string | opus\|sonnet\|haiku | Error |
| disable-model-invocation | boolean | true\|false | Error |

### Allowed Fields Set

```
description
allowed-tools
argument-hint
model
disable-model-invocation
```

Any field not in this set is invalid.

### Bash Filter Validation

Valid formats:
```
Bash           # All bash commands
Bash(git:*)    # All git subcommands
Bash(npm:test) # Only npm test
Bash(pytest:*) # All pytest commands
```

Extract base tool: `Bash(git:*)` → base tool is `Bash`.

### Cross-Field Validation

- If `argument-hint` present, body SHOULD contain `$1` or `$ARGUMENTS`
- If `allowed-tools` includes `AskUserQuestion`, command is Interactive type
- If `allowed-tools` includes `TodoWrite`, command is likely Workflow type
- If `disable-model-invocation` is true, command cannot be invoked by AI
