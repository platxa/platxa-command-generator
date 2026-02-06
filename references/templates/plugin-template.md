# Plugin Command Template

Template for commands distributed as part of a Claude Code plugin.

## When to Use

- Commands packaged in a plugin (npm/pip distribution)
- Commands that reference plugin-local files
- Commands using `${CLAUDE_PLUGIN_ROOT}` for portable paths

## Template

```markdown
---
description: {lowercase-verb phrase ≤60 chars}
allowed-tools:
  - Read
  - Write
  - Bash
  - {OtherTools}
---

# {Command Title}

{One-line purpose statement.}

## Context

{What this plugin command does and when to use it.}

## Plugin Resources

This command uses files from the plugin directory:
- `${CLAUDE_PLUGIN_ROOT}/templates/{template}` — {purpose}
- `${CLAUDE_PLUGIN_ROOT}/scripts/{script}` — {purpose}
- `${CLAUDE_PLUGIN_ROOT}/references/{ref}` — {purpose}

## Workflow

### Step 1: Load Plugin Resources

Read the template from `${CLAUDE_PLUGIN_ROOT}/templates/{template}`.

### Step 2: {Action}

{Instructions that use plugin resources}

### Step 3: {Action}

{Instructions that produce output in the user's project}

## Output

{Expected output in the user's working directory.}
```

## Example

```markdown
---
description: generate component from plugin templates
allowed-tools:
  - Read
  - Write
  - Glob
argument-hint: [component-name]
---

# Generate Component

Generate a React component using the plugin's template library.

## Context

Creates a new component following the team's conventions defined
in the plugin templates. Component name is provided as $1.

## Plugin Resources

- `${CLAUDE_PLUGIN_ROOT}/templates/component.tsx.md` — Component template
- `${CLAUDE_PLUGIN_ROOT}/templates/test.tsx.md` — Test template
- `${CLAUDE_PLUGIN_ROOT}/references/style-guide.md` — Team conventions

## Workflow

### Step 1: Load Templates

Read the component template from `${CLAUDE_PLUGIN_ROOT}/templates/component.tsx.md`.
Read the team style guide from `${CLAUDE_PLUGIN_ROOT}/references/style-guide.md`.

### Step 2: Generate Component

Create `src/components/$1/$1.tsx` using the template.
Apply style guide conventions.

### Step 3: Generate Test

Create `src/components/$1/$1.test.tsx` using the test template.

### Step 4: Update Index

Add export to `src/components/index.ts`.

## Default Behavior

If no component name provided, ask the user for one.
```

## Key Characteristics

- Uses `${CLAUDE_PLUGIN_ROOT}` for portable plugin-relative paths
- References plugin-bundled templates, scripts, and references
- Output goes to the user's project (not the plugin directory)
- Often combined with parameterized pattern ($1 for target names)
- Plugin commands are namespaced: `/plugin-name:command-name`
