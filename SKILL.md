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

## CRITICAL: Workflow Enforcement Rules

These rules are MANDATORY. They override optimization instincts, shortcut impulses, and "I already know the answer" reasoning.

### Required Subagent Phases

| Phase | Tool Call | Skippable? |
|-------|-----------|------------|
| Phase 2: Discovery | `Task(subagent_type="Explore")` | NEVER |
| Phase 3: Architecture | Inline (main conversation) | — |
| Phase 4: Generation | `Task(subagent_type="general-purpose")` | NEVER |
| Phase 5: Validation | `Bash` (run all 4 scripts) | NEVER |

### Violation Detection

If you find yourself doing ANY of the following, STOP immediately and correct:

- Reading `~/.claude/commands/` or `.claude/commands/` to check for duplicates → **use Discovery subagent**
- Searching for domain best practices or patterns inline → **use Discovery subagent**
- Writing the command `.md` file content directly in the main conversation → **use Generation subagent**
- Assessing quality score mentally without running scripts → **run the 4 validation scripts**
- Discovery subagent browsing unrelated projects or directories → **scope violation — constrain to Part 2 paths only**

### Why Subagents Are Non-Negotiable

- **Context isolation**: Subagents get clean context, producing higher-quality focused output
- **Independent review**: Generation and validation happen in separate contexts, preventing self-confirmation bias
- **Reproducibility**: Consistent results regardless of main conversation state or prior context
- **Auditability**: Each phase has clear inputs and outputs that can be traced

### Enforcement Language Key

Throughout this document:
- **MUST** / **MANDATORY** = non-negotiable, always required
- **SHOULD** = strongly recommended, skip only with explicit user override
- **MAY** = optional, use judgment

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

### Phase 2: Discovery (MANDATORY Subagent)

**MUST** dispatch `Task(subagent_type="Explore")` with a prompt structured in exactly two parts:

**Part 1 — Web Research** (domain best practices):
- Search the web for current best practices relevant to the command's domain
- Identify recommended libraries, patterns, and standards
- Determine tool requirements and argument needs

**Part 2 — Duplicate Check** (filename-only):
- List filenames in `commands/` directory in this project
- Report if any filename matches or is similar to the command being created
- **DO NOT read or open any existing command file — filenames only**
- **DO NOT search any other directory**

**DO NOT** perform any of the above inline. The Discovery subagent MUST run.

**Scope Constraint**: The subagent searches the web (Part 1) and lists filenames in `commands/` (Part 2). Nothing else.

**Sufficiency Check**: After the subagent returns, evaluate research completeness. Only ask user for clarification if gaps exist.

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

### Phase 4: Generation (MANDATORY Subagent)

**MUST** dispatch `Task(subagent_type="general-purpose")` with a prompt that includes:
- The architecture blueprint from Phase 3
- The relevant template path from `references/templates/`
- The discovery findings from Phase 2
- The output file path: `commands/{command-name}.md`

The Generation subagent creates the command .md file:
1. Generate frontmatter from architecture blueprint (if needed)
2. Write command body using template from `references/templates/`
3. Include dynamic features ($1, @file, inline bash) as specified
4. Add realistic examples and edge case handling
5. Write file to output location

**DO NOT** write the command file directly from the main conversation. The subagent gets a clean context for focused, high-quality generation.

### Phase 5: Validation (MANDATORY Scripts)

**MUST** run all 4 validation scripts via Bash. Do NOT self-assess quality.

```bash
./scripts/validate-structure.sh commands/{name}.md
./scripts/validate-frontmatter.sh commands/{name}.md
python3 scripts/count-tokens.py commands/{name}.md
./scripts/security-check.sh commands/{name}.md
```

All 4 MUST pass. Then assess content quality score (>= 7.0/10):
- [ ] File structure is valid (.md, readable, not empty)
- [ ] Frontmatter fields are correct (if present)
- [ ] Token budget within limits (< 4000 hard, < 2000 recommended)
- [ ] Line count within limits (< 600 hard, < 300 recommended)
- [ ] No security issues (dangerous patterns, credentials)
- [ ] Content quality score >= 7.0/10

If score < 7.0 or any script fails, dispatch Generation subagent again (max 2 rework iterations).

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

[Phase 2] Assistant dispatches: Task(subagent_type="Explore")
  → Subagent researches pytest/jest coverage patterns
  → Subagent checks ~/.claude/commands/ for duplicates
  → Returns: domain findings, no duplicates found

[Phase 3] Assistant determines architecture inline:
  → Type: Parameterized, argument-hint: [file-path]
  → Tools: Read, Glob, Bash(pytest:*), Bash(npx:jest)

[Phase 4] Assistant dispatches: Task(subagent_type="general-purpose")
  → Subagent receives blueprint + template path + discovery findings
  → Subagent writes commands/run-tests.md

[Phase 5] Assistant runs 4 validation scripts via Bash
  → All pass. Quality score: 8.4/10

[Phase 6] Assistant asks: Install to ~/.claude/commands/? (y/n)
```

### Example 2: Creating a Deploy Workflow Command

```
User: /platxa-command-generator
User: A multi-step deploy command with safety checks

[Phase 2] Task(subagent_type="Explore")
  → Researches deployment best practices, rollback patterns
  → Finds no duplicate deploy commands

[Phase 3] Architecture (inline):
  → Type: Workflow, Tools: Read, Bash, TodoWrite, AskUserQuestion

[Phase 4] Task(subagent_type="general-purpose")
  → Generates deploy.md with phases: validate, build, deploy, verify

[Phase 5] Bash: 4 validators → All pass. Score: 7.6/10

[Phase 6] Installation prompt
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
