# Frontmatter Generator

Rules for generating valid command frontmatter.

## Field Rules

### description (optional)
- Starts with lowercase verb
- Maximum 60 characters
- No trailing period
- Describes what the command does, not what it is

```yaml
# GOOD
description: analyze test coverage and identify gaps
description: generate API documentation from source

# BAD
description: This command analyzes test coverage.  # sentence, capital, period
description: Test Coverage Analyzer                 # noun phrase, not verb
description: analyze the complete and comprehensive test coverage across all modules  # too long
```

### allowed-tools (optional)
- Only valid Claude Code tool names
- Minimal set needed for the command
- Bash filters for scoped access

Valid tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS, Bash, Task, WebFetch, WebSearch, AskUserQuestion, TodoWrite, KillShell, BashOutput, NotebookEdit

```yaml
# Standard
allowed-tools:
  - Read
  - Bash

# With Bash filters
allowed-tools:
  - Read
  - Bash(git:*)
  - Bash(npm:test)
```

#### Bash Filter Syntax

Bash filters restrict which shell commands a command can execute. Format: `Bash(prefix:pattern)`.

```yaml
# Allow only git commands
- Bash(git:*)

# Allow only specific git subcommands
- Bash(git add:*)
- Bash(git commit:*)
- Bash(git diff:*)

# Allow only npm/pnpm test commands
- Bash(npm:test)
- Bash(pnpm:test)

# Allow only read-only operations
- Bash(cat:*)
- Bash(ls:*)

# Multiple specific filters
allowed-tools:
  - Read
  - Bash(git:*)
  - Bash(npm:test)
  - Bash(pytest:*)
```

**When to use Bash filters:**
- Command needs shell access but should not run arbitrary commands
- Restricting to version control operations only
- Restricting to test/lint runners only
- Preventing destructive commands (rm, chmod, etc.)

**Syntax rules:**
- Pattern is `Bash(command:subcommand_pattern)`
- `*` matches any arguments after the command prefix
- Multiple Bash filters can be listed — any matching filter allows execution
- Without filters, `Bash` alone allows all shell commands

### argument-hint (optional)
- Bracket format: `[description]`
- Matches $1/$2 usage in body
- Concise labels

```yaml
# Single argument
argument-hint: [file-path]

# Multiple arguments
argument-hint: [source] [destination]

# Optional argument
argument-hint: [pattern]
```

### model (optional)
- Only: `opus`, `sonnet`, `haiku`
- Override when specific reasoning needed
- Default is user's configured model

### disable-model-invocation (optional)
- Boolean: `true` or `false`
- Prevents AI from self-invoking the command
- Rare, for safety-critical commands

## Generation Logic

```
GIVEN command_type and features:

IF command_type == "Basic":
    frontmatter = None

IF command_type == "Standard":
    frontmatter = {description, allowed-tools}

IF command_type == "Parameterized":
    frontmatter = {description, allowed-tools, argument-hint}

IF command_type == "Interactive":
    frontmatter = {description, allowed-tools}
    allowed-tools MUST include AskUserQuestion

IF command_type == "Workflow":
    frontmatter = {description, allowed-tools}
    allowed-tools SHOULD include TodoWrite, Task

IF command_type == "Plugin":
    frontmatter = {description, allowed-tools}
```
