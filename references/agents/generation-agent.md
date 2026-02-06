# Generation Agent

Subagent prompt for command content generation phase.

## Purpose

Generate the complete command .md file based on the architecture blueprint.

## Task Prompt

```
You are a Command Generation Agent. Create the command .md file based on the architecture blueprint.

## Input

Architecture blueprint: {architecture_json}
Discovery findings: {discovery_json}
Output path: {output_path}

## Generation Steps

1. **Generate Frontmatter** (if command type requires it)
   - Only include fields that add value
   - description: Starts with lowercase verb, ≤60 characters
   - allowed-tools: Minimal set needed
   - argument-hint: Clear bracket format [arg1] [arg2]
   - Bash filters if needed: Bash(git:*), Bash(npm:*)

2. **Generate Command Body**
   - H1 title matching command purpose
   - Context paragraph explaining when/why to use
   - Clear step-by-step instructions
   - Concrete examples with realistic scenarios
   - Edge case handling

3. **Integrate Dynamic Features** (if specified)
   - $1/$2 with fallback handling
   - @file references with context explanation
   - !`bash` for runtime information

   **Prefer dynamic over static**: When the command needs context that changes
   at runtime (current branch, file contents, project structure), use `!`bash``
   or `@file` instead of asking Claude to read/run at execution time. Dynamic
   features inject context before Claude processes the prompt, reducing token
   usage and improving reliability.

   | Need | Use | Not |
   |------|-----|-----|
   | Current git branch | `!`git branch --show-current`` | "Run git branch" |
   | File contents for review | `@file` | "Read the file at $1" |
   | Project metadata | `!`cat package.json \| jq .version`` | "Check package.json" |
   | List of changed files | `!`git diff --name-only`` | "Run git diff" |

## Command Template

### Basic (no frontmatter)
```markdown
# {Command Title}

{Context and purpose}

## Instructions

{Step-by-step instructions}

## Examples

{Usage examples}
```

### Standard (with frontmatter)
```markdown
---
description: {verb-phrase ≤60 chars}
allowed-tools:
  - Tool1
  - Tool2
---

# {Command Title}

{Context and purpose}

## Workflow

{Step-by-step instructions}

## Output

{Expected output format}
```

### Parameterized (with arguments)
```markdown
---
description: {verb-phrase ≤60 chars}
allowed-tools:
  - Tool1
  - Tool2
argument-hint: [{arg description}]
---

# {Command Title}

Target: $1

{Instructions using $1}

## Default Behavior

If no argument provided:
{Fallback behavior}
```

### Plugin (with ${CLAUDE_PLUGIN_ROOT})
```markdown
---
description: {verb-phrase ≤60 chars}
allowed-tools:
  - Read
  - Write
  - {OtherTools}
---

# {Command Title}

## Plugin Resources

- `${CLAUDE_PLUGIN_ROOT}/templates/{template}` — {purpose}
- `${CLAUDE_PLUGIN_ROOT}/references/{ref}` — {purpose}

## Workflow

### Step 1: Load Plugin Resources

Read templates from `${CLAUDE_PLUGIN_ROOT}/templates/`.

### Step 2: {Generate Output}

{Use plugin resources to produce files in user's project}
```

**Key rule**: `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's install directory at runtime. Use it for all plugin-relative paths. Output files go to the user's project, never the plugin directory.

## Quality Requirements

- [ ] Frontmatter fields are valid (if present)
- [ ] Description starts with lowercase verb (if present)
- [ ] Description ≤60 characters (if present)
- [ ] argument-hint uses bracket format (if present)
- [ ] Command body has clear instructions
- [ ] Examples are realistic and actionable
- [ ] Token count < 2000 (recommended), < 4000 (hard limit)
- [ ] Line count < 300 (recommended), < 600 (hard limit)
- [ ] No placeholder content (TODO, TBD, ...)
- [ ] No hardcoded secrets or credentials
```

## Usage

```
Task tool with subagent_type="general-purpose"
Prompt: [Generation Agent prompt with inputs filled in]
```
