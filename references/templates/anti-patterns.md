# Command Anti-Patterns

Common mistakes to avoid when creating Claude Code slash commands.

## Structure Anti-Patterns

### Unnecessary Frontmatter

```markdown
<!-- BAD: Empty frontmatter adds nothing -->
---
---

# My Command

Do the thing.
```

```markdown
<!-- GOOD: No frontmatter for basic commands -->
# My Command

Do the thing.
```

**Why:** Empty frontmatter wastes tokens. Use Basic type instead.

---

### Over-Scoping Tools

```markdown
<!-- BAD: Requesting every tool -->
---
allowed-tools:
  - Read
  - Write
  - Edit
  - MultiEdit
  - Glob
  - Grep
  - Bash
  - Task
  - WebFetch
  - WebSearch
  - AskUserQuestion
  - TodoWrite
---
```

```markdown
<!-- GOOD: Minimal tools needed -->
---
allowed-tools:
  - Read
  - Glob
  - Grep
---
```

**Why:** Listing all tools is equivalent to no restriction. Only scope what's needed.

---

### Description as Sentence

```markdown
<!-- BAD: Full sentence with capital and period -->
---
description: This command analyzes code for bugs and issues.
---
```

```markdown
<!-- GOOD: Verb phrase, lowercase, no period -->
---
description: analyze code for bugs and issues
---
```

**Why:** Claude Code displays descriptions as short hints. Verb phrases read naturally.

---

## Argument Anti-Patterns

### No Fallback for Missing Arguments

```markdown
<!-- BAD: Breaks when $1 is empty -->
# Deploy

Deploy to $1 immediately.
Run: `deploy.sh $1`
```

```markdown
<!-- GOOD: Handles missing argument -->
# Deploy

Deploy to: $1

If no environment specified, default to staging.
Ask the user to confirm before deploying to production.
```

**Why:** Users may invoke `/deploy` without arguments. Always handle the empty case.

---

### Argument Hint Mismatch

```markdown
<!-- BAD: Hint says [file] but body uses $1 as module name -->
---
argument-hint: [file]
---

# Analyze Module

Analyze the module named $1 for issues.
```

```markdown
<!-- GOOD: Hint matches actual usage -->
---
argument-hint: [module-name]
---

# Analyze Module

Analyze the module named $1 for issues.
```

**Why:** Mismatched hints confuse users about what to provide.

---

## Content Anti-Patterns

### Vague Instructions

```markdown
<!-- BAD: Unclear actions -->
## Instructions

Review the code appropriately.
Handle errors properly.
Make sure everything works well.
```

```markdown
<!-- GOOD: Specific, actionable steps -->
## Instructions

1. Read all files in `src/` matching `*.ts`
2. Check each function for missing return type annotations
3. Add return types based on the function body
4. Run `pnpm typecheck` to verify no type errors
```

**Why:** Vague instructions produce inconsistent behavior.

---

### Hardcoded Paths

```markdown
<!-- BAD: Assumes specific paths -->
Read the config from /home/user/project/.env
Write output to /tmp/results.json
```

```markdown
<!-- GOOD: Relative and flexible -->
Read the config from the project root .env file.
Write output to the current working directory.
```

**Why:** Hardcoded paths break for other users and environments.

---

### Placeholder Content

```markdown
<!-- BAD: Incomplete command -->
## Workflow

1. TODO: Add step 1
2. TBD: Figure out step 2
3. [Add more steps here]
```

**Why:** Commands must be complete. Never commit placeholders.

---

## Security Anti-Patterns

### Piping Untrusted Input

**BAD:** Piping remote downloads directly to a shell, or using `eval` on user arguments.

**GOOD:** Download files first, inspect content, then execute only after review. Never pipe remote content directly to a shell interpreter.

**Why:** Arbitrary code execution is a security vulnerability.

---

### Exposing Credentials

```markdown
<!-- BAD: Hardcoded secrets -->
Use API key: sk-abc123456
Set password to: admin123
```

```markdown
<!-- GOOD: Environment-based -->
Read the API key from ${ANTHROPIC_API_KEY} environment variable.
Never hardcode credentials in commands.
```

**Why:** Credentials in commands are visible to all project collaborators.

---

## Performance Anti-Patterns

### Token Bloat

```markdown
<!-- BAD: Verbose, repetitive content -->
## Very Important Note About This Very Important Thing

This is extremely important. You must absolutely always remember
this critically important information at all times. The importance
of this cannot be overstated. It is vital and essential and
paramount and crucial...
```

```markdown
<!-- GOOD: Concise -->
## Important

Always validate input before processing.
```

**Why:** Every token in a command consumes context window.

---

### Embedding Large Examples

```markdown
<!-- BAD: 200-line example inline -->
## Example Output

```json
{
  // ... 200 lines of JSON ...
}
```

```markdown
<!-- GOOD: Minimal representative example -->
## Example Output

```json
{
  "status": "success",
  "items": [{"id": 1, "name": "..."}],
  "total": 42
}
```

**Why:** Large examples waste budget. Show structure, not volume.

---

## Quick Reference

| Anti-Pattern | Category | Fix |
|-------------|----------|-----|
| Empty frontmatter | Structure | Remove or use Basic type |
| Over-scoped tools | Structure | List only needed tools |
| Full-sentence description | Structure | Use verb phrase |
| No argument fallback | Arguments | Add default behavior |
| Hint mismatch | Arguments | Match hint to usage |
| Vague instructions | Content | Be specific |
| Hardcoded paths | Content | Use relative paths |
| Placeholders | Content | Complete all content |
| Piping untrusted input | Security | Inspect before executing |
| Exposed credentials | Security | Use env vars |
| Token bloat | Performance | Be concise |
| Large examples | Performance | Show structure only |
