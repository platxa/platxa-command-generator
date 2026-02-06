# Sequential Composition

How commands can reference prior outputs to build pipelines.

## Concept

Claude Code maintains conversation context across commands. A command's output (files written, variables set, information gathered) is available to subsequent commands in the same session. This enables composing simple commands into multi-step workflows.

## Pipeline Example

```
/analyze src/         →  Writes analysis to ANALYSIS.md
/generate-tests       →  Reads ANALYSIS.md, generates tests
/review-coverage      →  Reads test files, checks coverage gaps
```

Each command produces an artifact that the next command consumes.

## Composition Patterns

### File-Based Handoff

Commands write results to a known file that subsequent commands read:

```markdown
# Analyze

Analyze the codebase and write findings to `ANALYSIS.md` in the project root.

## Output

Write analysis results to `ANALYSIS.md` with sections:
- ## Summary
- ## Issues Found
- ## Recommendations
```

The next command references the output:

```markdown
# Fix Issues

Read `ANALYSIS.md` and fix each issue listed under `## Issues Found`.
```

### Conversation Context Handoff

Commands can rely on Claude's memory of what happened earlier in the session:

```markdown
# Review

Review the changes made in this session. Summarize what was modified,
what tests were added, and any remaining concerns.
```

This works because Claude remembers all file edits and tool calls from earlier commands.

### Structured Output for Machine Consumption

For reliable handoff, commands can write structured data:

```markdown
# Scan Dependencies

Check for outdated dependencies and write results to `.claude/dep-report.json`:

{
  "outdated": [{"name": "...", "current": "...", "latest": "..."}],
  "vulnerable": [{"name": "...", "severity": "..."}]
}
```

## Design Guidelines

| Guideline | Why |
|-----------|-----|
| Write output to predictable paths | Next command knows where to look |
| Use structured formats (JSON, markdown sections) | Easier to parse programmatically |
| Keep intermediate artifacts in `.claude/` or project root | Avoid cluttering source directories |
| Document expected input/output in each command | Makes composition discoverable |
| Commands should work standalone too | Don't require a prior command to function |

## Anti-Pattern: Tight Coupling

Avoid commands that only work when invoked in a specific sequence. Each command should have a fallback when its expected input doesn't exist:

```markdown
# Fix Issues

Read `ANALYSIS.md` for known issues.

## Default Behavior

If `ANALYSIS.md` does not exist, run a quick analysis of the current
directory before fixing issues.
```
