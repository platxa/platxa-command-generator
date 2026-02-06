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
