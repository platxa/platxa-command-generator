# Workflow Command Template

Template for multi-phase commands with state tracking and progress.

## When to Use

- Commands with multiple sequential phases
- Long-running tasks that benefit from progress tracking
- Commands that may be interrupted and resumed

## Template

```markdown
---
description: {lowercase-verb phrase ≤60 chars}
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Task
  - TodoWrite
  - AskUserQuestion
---

# {Command Title}

{One-line purpose statement.}

## Context

{When to use this command. Explain the multi-phase nature.}

## Guardrails

- Phase 1 must read and understand current state before any modifications
- Never skip directly to execution without analysis phase

## Phases

### Phase 1: {Analysis / Understanding}

**Goal:** Read and understand current state before making changes

1. {Read relevant files, logs, or data}
2. {Identify what exists and what needs to change}
3. {Assess risks or dependencies}

**Exit criteria:** {Current state documented and understood}

### Phase 2: {Phase Name}

**Goal:** {What this phase accomplishes}

1. {Step 1}
2. {Step 2}

**Exit criteria:** {How to know this phase is complete}

### Phase 3: {Phase Name}

**Goal:** {What this phase accomplishes}

1. {Step 1}
2. {Step 2}

**Exit criteria:** {How to know this phase is complete}

## Progress Tracking

Use TodoWrite to track phase completion:
- Create task list at start
- Mark phases as in_progress when starting
- Mark phases as completed when exit criteria met

## Verification

{How to verify the entire workflow completed correctly:}
- {End-to-end check — e.g., run integration test suite}
- {Phase-level check — e.g., verify each phase exit criteria was met}
- {Final state check — e.g., compare expected vs actual deliverable}

## Error Recovery

If a phase fails:
1. Report what failed and why
2. Suggest corrective action
3. Allow retry from the failed phase

## Output

{Final deliverable when all phases complete.}
```

## Example

```markdown
---
description: migrate database schema with safety checks
allowed-tools:
  - Read
  - Write
  - Bash
  - TodoWrite
  - AskUserQuestion
---

# Database Migration

Safely migrate the database schema through multiple phases.

## Phases

### Phase 1: Analysis

**Goal:** Understand current schema and required changes

1. Read current migration files
2. Identify tables and columns affected
3. Assess risk level (data loss, downtime)

**Exit criteria:** Migration plan documented with risk assessment

### Phase 2: Generate Migration

**Goal:** Create migration files

1. Generate migration script based on analysis
2. Generate rollback script
3. Validate SQL syntax

**Exit criteria:** Migration and rollback scripts created

### Phase 3: Test

**Goal:** Verify migration works on test data

1. Run migration against test database
2. Verify data integrity
3. Run rollback and verify clean state

**Exit criteria:** Migration and rollback both succeed

### Phase 4: Execute

**Goal:** Apply migration to target database

1. Confirm with user before proceeding
2. Create database backup
3. Apply migration
4. Verify post-migration state

**Exit criteria:** Migration applied, data verified

## Progress Tracking

Track each phase with TodoWrite for visibility.

## Verification

After migration completes, verify:
- `SELECT count(*) FROM {affected_tables}` returns expected row counts
- Application health check endpoint returns 200
- Rollback script tested independently in Phase 3

## Error Recovery

If any phase fails:
1. Do NOT proceed to next phase
2. Show error details
3. If Phase 4 fails, run rollback automatically
```

## Multi-Agent Orchestration Pattern

Workflow commands can use the Task tool to dispatch parallel subagents for independent work:

```markdown
### Phase 2: Parallel Analysis

**Goal:** Analyze multiple aspects concurrently

Use the Task tool to launch these analyses in parallel (all in a single message):

1. **Security scan** (subagent_type="general-purpose"):
   "Scan all files in src/ for security vulnerabilities. Report findings as JSON."

2. **Test coverage** (subagent_type="general-purpose"):
   "Analyze test coverage for src/. Report untested files and functions."

3. **Dependency audit** (subagent_type="general-purpose"):
   "Check package.json dependencies for known vulnerabilities and outdated versions."

Wait for all agents to complete, then merge their findings into a unified report.

**Exit criteria:** All three analyses complete and findings merged
```

Key rules for Task tool dispatch:
- Launch independent subagents in a single message (parallel execution)
- Each subagent gets a focused, self-contained prompt
- Collect and merge results after all complete
- Sequential phases must wait for prior phase results

## Key Characteristics

- Multiple phases with clear entry/exit criteria
- Uses TodoWrite for progress tracking
- Includes error recovery instructions
- Task tool for delegating complex sub-tasks
- Each phase is self-contained and verifiable
- Phase 1 always reads/analyzes before later phases modify (guardrail pattern)
