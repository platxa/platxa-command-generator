# Interactive Command Template

Template for commands that use AskUserQuestion for multi-step user input.

## When to Use

- Commands that need user decisions before proceeding
- Commands with multiple configuration options
- Wizards or guided workflows

## Template

```markdown
---
description: {lowercase-verb phrase ≤60 chars}
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
  - {OtherTools}
---

# {Command Title}

{One-line purpose statement.}

## Context

{When to use this command. Explain the interactive flow.}

## Workflow

### Step 1: Gather Requirements

Use AskUserQuestion to determine:

**Question 1: {Topic}**
- Option A: {description}
- Option B: {description}
- Option C: {description}

**Question 2: {Topic}**
- Option A: {description}
- Option B: {description}

### Step 2: Execute Based on Choices

{Branch logic based on user answers}

### Step 3: Confirm and Finalize

Show the user what was created and ask for confirmation.

## Verification

{How to verify the command worked correctly for each choice path:}
- {Test or check 1 — e.g., validate generated files match chosen options}
- {Test or check 2 — e.g., run tests on the output}

## Output

{Expected output based on chosen options.}
```

## Example

```markdown
---
description: scaffold a new API endpoint with tests
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# New API Endpoint

Create a new API endpoint with proper structure, validation, and tests.

## Workflow

### Step 1: Gather Endpoint Details

Ask the user:

**What HTTP method?**
- GET - Read data
- POST - Create data
- PUT - Update data
- DELETE - Remove data

**What resource name?**
(Free text input for the resource, e.g., "users", "orders")

**Include authentication?**
- Yes - Add JWT middleware
- No - Public endpoint

### Step 2: Detect Project Patterns

Read existing endpoints to match:
- Router file structure
- Validation patterns
- Response format conventions

### Step 3: Generate Files

Based on choices, create:
- Route handler in `src/routes/{resource}.py`
- Schema in `src/schemas/{resource}.py`
- Test file in `tests/test_{resource}.py`

### Step 4: Verify

Run `pytest tests/test_{resource}.py -v` to confirm tests pass.

## Verification

After generation, verify:
- `pytest tests/test_{resource}.py -v` passes
- Route is accessible at expected URL path
- Schema validation rejects invalid input (test with malformed data)

## Output

Summary of created files with next steps.
```

## Key Characteristics

- Includes `AskUserQuestion` in allowed-tools
- Structures questions with clear options
- Handles branching based on user choices
- Minimizes questions (2-4 max to avoid prompt fatigue)
- Uses smart defaults where possible
