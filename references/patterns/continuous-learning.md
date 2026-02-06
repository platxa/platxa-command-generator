# Continuous Learning Pattern

Pattern for commands that extract and persist session learnings to improve future interactions.

## Concept

Some commands can observe patterns during execution and write insights to persistent memory files (CLAUDE.md, MEMORY.md, or project-specific files). This creates a feedback loop where each session improves the next.

## Pattern: /learn Command

A command that reviews the current session and extracts reusable learnings:

```markdown
---
description: extract session learnings to persistent memory
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Learn

Review the current conversation and extract reusable patterns, preferences, and learnings.

## Guardrails

- Read existing memory files before adding new entries
- Never duplicate existing entries
- Keep entries concise and actionable

## Workflow

### Step 1: Analyze Session

Review the conversation for:
- Patterns that worked well (coding style, tool preferences)
- Mistakes that were corrected (avoid repeating)
- Project-specific conventions discovered
- User preferences expressed

### Step 2: Check Existing Memory

Read CLAUDE.md and any memory files to avoid duplicates.

### Step 3: Persist Learnings

Append new insights to the appropriate file:
- **CLAUDE.md**: Project-wide conventions and rules
- **MEMORY.md**: Session patterns and preferences
- **references/**: Domain-specific knowledge

## Output

List what was learned and where it was saved.
```

## Pattern: /evolve Command

A command that reviews command effectiveness and suggests improvements:

```markdown
# Evolve Commands

Review how commands performed in recent sessions and suggest improvements.

## Workflow

### Step 1: Identify Frequently Used Commands

Use Glob to find commands and check git log for usage patterns.

### Step 2: Analyze Effectiveness

For each command, check:
- Did it produce the desired output?
- Were manual corrections needed after running?
- Are there common follow-up actions that should be automated?

### Step 3: Suggest Improvements

For each finding, suggest:
- Updated instructions for better results
- New commands to automate common follow-ups
- Deprecated commands that are no longer useful
```

## Where to Persist Learnings

| Type of Learning | Where to Store | Example |
|-----------------|----------------|---------|
| Project conventions | `CLAUDE.md` | "Always use ruff for Python formatting" |
| Personal preferences | `~/.claude/CLAUDE.md` | "Prefer concise explanations" |
| Domain knowledge | `references/*.md` | API patterns, error codes |
| Session context | `MEMORY.md` | "Working on auth refactor, 3/5 done" |

## Key Principles

- Learnings must be specific and actionable (not "code should be good")
- Check for duplicates before persisting
- Prefer updating existing entries over creating new ones
- Keep memory files concise — prune outdated entries
