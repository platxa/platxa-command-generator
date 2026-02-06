# Basic Command Template

Template for commands with no frontmatter. Pure markdown instructions.

## When to Use

- Simple instructions that don't need tool restrictions
- Commands that work with Claude's default tool set
- Quick reference cards or checklists

## Template

```markdown
# {Command Title}

{One-line purpose statement.}

## Context

{When to use this command and what problem it solves.}

## Instructions

1. {Step 1 with concrete action}
2. {Step 2 with concrete action}
3. {Step 3 with concrete action}

## Output

{What the user should expect when done.}
```

## Example

```markdown
# Code Review Checklist

Review the current changes for quality and correctness.

## Context

Use before creating a pull request to catch common issues.

## Instructions

1. Read all modified files using `git diff`
2. Check for unused imports and variables
3. Verify error handling covers edge cases
4. Ensure tests exist for new functionality
5. Check naming conventions match project style

## Output

Provide a summary with:
- Issues found (with file:line references)
- Suggestions for improvement
- Overall assessment (ready / needs work)
```

## Key Characteristics

- No `---` frontmatter block
- Starts directly with `# Title`
- All Claude Code tools available by default
- Simplest command type
- Best for < 100 lines
