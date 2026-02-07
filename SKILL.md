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
  version: "1.1.0"
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

This skill creates production-ready Claude Code slash commands by:

1. **Discovering** domain knowledge through web research and duplicate checking
2. **Architecting** command type and structure
3. **Generating** the command .md file via subagent
4. **Validating** against quality scripts (score >= 7.0/10)

The workflow uses Task tool subagents for each phase, ensuring deep expertise at every step.

## Workflow

### Phase 1: Initialize

```
User: /platxa-command-generator
```

Ask the user for:
- Command description (what should it do?)
- Target users (who will use it?)

### Phase 2: Discovery

Dispatch `Task(subagent_type="Explore")` with a prompt covering:

**Part 1 — Web Research**: Search for domain best practices, recommended libraries, patterns, and standards relevant to the command's domain.

**Part 2 — Duplicate Check**: List filenames in `commands/` directory in this project. Report if any filename matches the command being created. Do not read file contents, do not search other directories.

After subagent returns, evaluate research completeness. Ask user only if gaps exist.

### Phase 3: Architecture

Based on discovery, determine:
- **Command Type**: Basic, Standard, Parameterized, Interactive, Workflow, or Plugin
- **Frontmatter Fields**: Which optional fields are needed
- **Dynamic Features**: $1/$2, @file, inline bash, ${CLAUDE_PLUGIN_ROOT}
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

See `references/patterns/command-types.md` and `references/patterns/frontmatter-generator.md` for field rules.

### Phase 4: Generation

Dispatch `Task(subagent_type="general-purpose")` with a prompt that includes:
- The architecture blueprint from Phase 3
- The relevant template path from `references/templates/`
- The discovery findings from Phase 2
- The output file path: `commands/{command-name}.md`

The subagent writes the command .md file using the template and discovery findings.

### Phase 5: Validation

Run all 4 validation scripts:

```bash
./scripts/validate-structure.sh commands/{name}.md
./scripts/validate-frontmatter.sh commands/{name}.md
python3 scripts/count-tokens.py commands/{name}.md
./scripts/security-check.sh commands/{name}.md
```

All 4 must pass. Then assess content quality score (>= 7.0/10).

If score < 7.0 or any script fails, dispatch Generation subagent again (max 2 rework iterations).

### Phase 6: Installation

Ask user for installation location:
- **User command**: `~/.claude/commands/{name}.md`
- **Project command**: `.claude/commands/{name}.md`
- **Plugin command**: `.claude/plugins/{namespace}/commands/{name}.md`

Copy file and verify installation.

## Examples

### Example 1: Creating a Test Runner Command

```
User: /platxa-command-generator
Assistant: What command would you like to create?
User: A command that runs tests for a specific file with coverage

[Phase 2] Task(subagent_type="Explore")
  → Web: researches pytest/jest coverage patterns
  → Local: lists commands/ filenames, no duplicates

[Phase 3] Architecture (inline):
  → Type: Parameterized, argument-hint: [file-path]
  → Tools: Read, Glob, Bash(pytest:*), Bash(npx:jest)

[Phase 4] Task(subagent_type="general-purpose")
  → Receives blueprint + template path + discovery findings
  → Writes commands/run-tests.md

[Phase 5] Bash: 4 validation scripts → All pass. Score: 8.4/10

[Phase 6] Install to ~/.claude/commands/? (y/n)
```

### Example 2: Creating a Deploy Workflow Command

```
User: /platxa-command-generator
User: A multi-step deploy command with safety checks

[Phase 2] Task(subagent_type="Explore")
  → Web: deployment best practices, rollback patterns
  → Local: no duplicate deploy commands

[Phase 3] Architecture: Workflow type, TodoWrite + AskUserQuestion

[Phase 4] Task(subagent_type="general-purpose")
  → Generates deploy.md with phases: validate, build, deploy, verify

[Phase 5] Bash: 4 validators → All pass. Score: 7.6/10

[Phase 6] Installation prompt
```

## Output Checklist

When generating a command, verify:

- [ ] File is valid .md with proper structure
- [ ] Frontmatter fields are correct (if present)
- [ ] Description starts with lowercase verb, ≤60 characters (if present)
- [ ] argument-hint matches $1/$2 usage (if present)
- [ ] allowed-tools are minimal and valid (if present)
- [ ] Instructions are clear and actionable
- [ ] Arguments have fallback handling (if parameterized)
- [ ] Within token budget (< 2000 recommended)
- [ ] Quality score >= 7.0/10
