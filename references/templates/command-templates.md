# Command Templates

Selection guide for choosing the right command type and template.

## Command Type Decision Tree

```
Does the command need frontmatter?
├── No → Basic
│   (Simple instructions, all tools available)
│
└── Yes → Does it accept user arguments?
    ├── Yes → Parameterized
    │   (Uses $1/$2/$ARGUMENTS with argument-hint)
    │
    └── No → Does it need user decisions?
        ├── Yes → Interactive
        │   (Uses AskUserQuestion for choices)
        │
        └── No → Is it multi-phase?
            ├── Yes → Workflow
            │   (Multiple phases with state tracking)
            │
            └── No → Is it in a plugin?
                ├── Yes → Plugin
                │   (Uses ${CLAUDE_PLUGIN_ROOT})
                │
                └── No → Standard
                    (Tool-scoped with description)
```

## Type Comparison

| Type | Frontmatter | Arguments | Interactive | Multi-Phase | Plugin |
|------|------------|-----------|-------------|-------------|--------|
| Basic | No | No | No | No | No |
| Standard | Yes | No | No | No | No |
| Parameterized | Yes | $1/$2 | No | No | No |
| Interactive | Yes | Optional | Yes | No | No |
| Workflow | Yes | Optional | Optional | Yes | No |
| Plugin | Yes | Optional | Optional | Optional | Yes |

## Template Selection

| Command Type | Template File | Key Features |
|-------------|---------------|--------------|
| Basic | `basic-template.md` | No frontmatter, pure instructions |
| Standard | `standard-template.md` | allowed-tools, description |
| Parameterized | `parameterized-template.md` | argument-hint, $1/$2 |
| Interactive | `interactive-template.md` | AskUserQuestion |
| Workflow | `workflow-template.md` | TodoWrite, phases, state |
| Plugin | `plugin-template.md` | ${CLAUDE_PLUGIN_ROOT} |

## Frontmatter Fields Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `description` | No | string | ≤60 chars, starts with lowercase verb |
| `allowed-tools` | No | list | Scoped tools (with optional Bash filters) |
| `argument-hint` | No | string | Bracket format: `[arg1] [arg2]` |
| `model` | No | string | `opus`, `sonnet`, or `haiku` |
| `disable-model-invocation` | No | boolean | Prevent AI from self-invoking |

## Dynamic Features Reference

| Feature | Syntax | Purpose |
|---------|--------|---------|
| Positional args | `$1`, `$2` | User-provided arguments |
| All arguments | `$ARGUMENTS` | Full argument string |
| File reference | `@file` | Inject file contents |
| Bash execution | `` !`command` `` | Runtime dynamic content |

## Allowed Tools (Valid Values)

Core tools: `Read`, `Write`, `Edit`, `MultiEdit`, `Glob`, `Grep`, `LS`, `Bash`, `Task`, `WebFetch`, `WebSearch`, `AskUserQuestion`, `TodoWrite`, `KillShell`, `BashOutput`, `NotebookEdit`

### Bash Filters

Restrict Bash to specific commands:

```yaml
allowed-tools:
  - Bash(git:*)        # Only git commands
  - Bash(npm:*)        # Only npm commands
  - Bash(pytest:*)     # Only pytest commands
  - Bash(git:commit)   # Only git commit
```

## Token Budget

| Metric | Recommended | Hard Limit |
|--------|-------------|------------|
| Tokens | 2,000 | 4,000 |
| Lines | 300 | 600 |
