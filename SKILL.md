---
name: platxa-command-generator
description: Autonomous command creator for Claude Code CLI. Uses multi-phase orchestrated workflow with Task tool subagents to research domains, design structure, generate content, and validate quality. Creates production-ready slash commands following Claude Code's command specification.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - Task
  - AskUserQuestion
  - TodoWrite
metadata:
  version: "1.0.0"
  author: "DJ Patel — Founder & CEO, Platxa | https://platxa.com"
  tags:
    - command-creation
    - automation
    - builder
    - claude-code
---

# Platxa Command Generator

Create Claude Code slash commands autonomously using a multi-phase orchestrated workflow.

## Overview

This skill guides you through creating production-ready Claude Code slash commands by:

1. **Discovering** domain knowledge through research and existing command analysis
2. **Architecting** the command type and structure (Basic/Standard/Parameterized/Interactive/Workflow/Plugin)
3. **Generating** the command .md file with proper frontmatter and dynamic features
4. **Validating** against quality standards with scoring (must be >= 7.0/10)

The workflow uses Task tool subagents for each phase, ensuring deep expertise at every step.

## Command Types

| Type | Frontmatter | Dynamic Features | Use Case |
|------|------------|-----------------|----------|
| Basic | None | None | Simple instructions, checklists |
| Standard | description, allowed-tools | None | Tool-scoped team commands |
| Parameterized | + argument-hint | $1, $2 | Commands with user arguments |
| Interactive | + AskUserQuestion | User prompts | Guided wizards |
| Workflow | + TodoWrite, Task | Multi-phase | Complex multi-step tasks |
| Plugin | + ${CLAUDE_PLUGIN_ROOT} | Plugin paths | Distributed plugin commands |

## Workflow

### Phase 1: Initialize

```
User: /platxa-command-generator
```

Ask the user for:
- Command description (what should it do?)
- Target users (who will use it?)

### Phase 2: Discovery (Automatic)

Use Task tool with `subagent_type="Explore"` to:
1. Search for domain best practices
2. Analyze existing commands in `~/.claude/commands/` and `.claude/commands/`
3. Identify tool requirements and argument needs
4. Determine command type classification
5. Check for duplicates or overlap with existing commands

**Sufficiency Check**: Evaluate research completeness. Only ask user for clarification if gaps exist.

### Phase 3: Architecture

Based on discovery, determine:
- **Command Type**: Basic, Standard, Parameterized, Interactive, Workflow, or Plugin
- **Frontmatter Fields**: Which optional fields are needed
- **Dynamic Features**: $1/$2, @file, inline bash execution, ${CLAUDE_PLUGIN_ROOT}
- **Token Budget**: Recommended 2000 tokens / 300 lines

Generate architecture blueprint:
```json
{
  "command_type": "Parameterized",
  "command_name": "generate-tests",
  "frontmatter": {
    "description": "generate unit tests for specified module",
    "allowed_tools": ["Read", "Write", "Bash"],
    "argument_hint": "[module-path]"
  },
  "dynamic_features": ["$1"],
  "estimated_tokens": 800
}
```

### Phase 4: Generation

Create the command .md file:
1. Generate frontmatter from architecture blueprint (if needed)
2. Write command body using template from `references/templates/`
3. Include dynamic features ($1, @file, inline bash) as specified
4. Add realistic examples and edge case handling
5. Write file to output location

### Phase 5: Validation

Run quality checks:
- [ ] File structure is valid (.md, readable, not empty)
- [ ] Frontmatter fields are correct (if present)
- [ ] Token budget within limits (< 4000 hard, < 2000 recommended)
- [ ] Line count within limits (< 600 hard, < 300 recommended)
- [ ] No security issues (dangerous patterns, credentials)
- [ ] Content quality score >= 7.0/10

If score < 7.0, route to rework phase (max 2 iterations).

### Phase 6: Installation

Ask user for installation location:
- **User command**: `~/.claude/commands/{name}.md`
- **Project command**: `.claude/commands/{name}.md`
- **Plugin command**: `.claude/plugins/{namespace}/commands/{name}.md`

Copy file and verify installation.

## Dynamic Features Reference

| Feature | Syntax | Example |
|---------|--------|---------|
| Positional args | `$1`, `$2` | `/deploy staging` → $1 = "staging" |
| All arguments | `$ARGUMENTS` | `/search foo bar` → "foo bar" |
| File reference | `@file` | Content injected from referenced file |
| Bash execution | Exclamation + backtick-wrapped command | Output replaces backtick block |
| Plugin root | `${CLAUDE_PLUGIN_ROOT}` | Absolute path to plugin directory |

## Frontmatter Fields

All frontmatter fields are **optional** for commands:

| Field | Type | Constraint |
|-------|------|-----------|
| `description` | string | ≤60 chars, starts with lowercase verb |
| `allowed-tools` | list | Valid Claude Code tools, Bash filters supported |
| `argument-hint` | string | Bracket format: `[arg1] [arg2]` |
| `model` | string | `opus`, `sonnet`, or `haiku` |
| `disable-model-invocation` | boolean | Prevent AI self-invocation |

## Examples

### Example 1: Creating a Test Runner Command

```
User: /platxa-command-generator
Assistant: What command would you like to create?
User: A command that runs tests for a specific file with coverage
Assistant: [Discovers pytest/jest patterns, coverage tools...]
Assistant: [Classifies as Parameterized type with $1 for file path]
Assistant: [Generates run-tests.md with argument-hint: [file-path]]
Assistant: Quality score: 8.4/10. Install to .claude/commands/? (y/n)
```

### Example 2: Creating a Deploy Workflow Command

```
User: /platxa-command-generator
Assistant: What command would you like to create?
User: A multi-step deploy command with safety checks
Assistant: [Discovers deployment best practices, rollback patterns...]
Assistant: [Classifies as Workflow type with TodoWrite for progress]
Assistant: [Generates deploy.md with phases: validate, build, deploy, verify]
Assistant: Quality score: 7.6/10. Ready to install.
```

## Output Checklist

When generating a command, verify:

- [ ] File is valid .md with proper structure
- [ ] Frontmatter fields are correct (if present)
- [ ] Description starts with lowercase verb (if present)
- [ ] Description ≤60 characters (if present)
- [ ] argument-hint matches $1/$2 usage (if present)
- [ ] allowed-tools are minimal and valid (if present)
- [ ] Instructions are clear and actionable
- [ ] Examples show realistic usage
- [ ] Arguments have fallback handling (if parameterized)
- [ ] Within token budget (< 2000 recommended)
- [ ] Quality score >= 7.0/10
