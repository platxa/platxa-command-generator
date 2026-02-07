---
description: generate frontend component with types, tests, and stories
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
argument-hint: [name]
---

# Frontend Component Generator

Generate a production-ready frontend component for: $1

## Project Context

Framework: !`cat package.json 2>/dev/null | grep -oE '"(react|vue|svelte)":' | head -1 | tr -d '":' || echo "not detected"`
TypeScript: !`test -f tsconfig.json && echo "yes" || echo "no"`
Storybook: !`test -d .storybook && echo "yes" || echo "no"`

## Guardrails

- Read existing components before generating to match project patterns
- Never overwrite existing files without user confirmation
- Follow the project's directory structure and naming conventions
- Use the project's existing CSS/styling approach (Tailwind, CSS Modules, styled-components)

## Workflow

### Step 1: Detect Project Stack

Use Glob and Read to determine:

1. **Framework**: Check `package.json` dependencies for react, vue, or svelte
2. **Language**: Check for `tsconfig.json` (TypeScript) or `.js` components
3. **Test runner**: Check for vitest, jest, or testing-library in devDependencies
4. **Stories**: Check for `.storybook/` directory or `*.stories.*` files
5. **Styling**: Check for tailwind.config, CSS modules, styled-components, or emotion
6. **Component directory**: Find where components live (`src/components/`, `components/`, `app/`)

### Step 2: Gather Requirements

Use AskUserQuestion for choices that cannot be auto-detected:

**Question 1 (only if framework not detected): Which framework?**
- React (Recommended)
- Vue 3
- Svelte

**Question 2: Component category?**
- UI primitive (button, input, badge, card)
- Layout (header, sidebar, grid, container)
- Data display (table, list, chart, stat card)
- Form (input group, select, multi-step form)

**Question 3: Which artifacts to generate? (multiSelect: true)**
- Component file (Recommended)
- Type definitions
- Unit tests
- Storybook stories

### Step 3: Analyze Existing Patterns

Read 2-3 existing components in the project to match:

- File naming: PascalCase vs kebab-case, index barrel exports
- Import style: named vs default exports
- Props pattern: interface vs type, destructured vs props object
- Styling approach: className strings, CSS modules, styled-components
- Test patterns: render approach, assertion style, mock conventions
- Story format: CSF3 vs CSF2, decorator usage

### Step 4: Generate Files

Create files matching detected patterns:

**Component file** (`ComponentName.tsx` / `.vue` / `.svelte`):
- Props interface/type with JSDoc comments
- Component implementation following detected patterns
- Proper accessibility attributes (aria-label, role, keyboard handlers)
- Responsive styling using the project's approach
- Forward ref support (React) or expose (Vue)

**Type definitions** (if selected):
- Props type with required/optional fields documented
- Event handler types
- Variant/size union types where applicable
- Export from component barrel or shared types

**Unit tests** (if selected):
- Render test (component mounts without errors)
- Props test (renders correctly with different prop values)
- Interaction test (click, hover, keyboard events)
- Accessibility test (proper roles, labels)
- Use the project's test runner and patterns

**Stories** (if selected):
- Default story with essential props
- Variant stories (sizes, colors, states)
- Interactive story with controls/args
- Follow CSF3 format with meta and satisfies

### Step 5: Verify

Run project verification:
- Type check: `pnpm typecheck` or `npx tsc --noEmit`
- Tests: Run only the new test file
- Lint: `pnpm lint` on the new files

## Generated Files

| Artifact | Path Pattern |
|----------|-------------|
| Component | `{component-dir}/{Name}/{Name}.tsx` |
| Types | `{component-dir}/{Name}/{Name}.types.ts` |
| Tests | `{component-dir}/{Name}/{Name}.test.tsx` |
| Stories | `{component-dir}/{Name}/{Name}.stories.tsx` |
| Index | `{component-dir}/{Name}/index.ts` |

Paths adapt to the project's detected structure. If the project uses flat files instead of directories, match that convention.

## Verification

After generation, verify:
- Component renders without TypeScript errors
- Test file runs and passes: `pnpm test {Name}` or equivalent
- Story loads without errors (if Storybook present)
- New files follow the same patterns as existing components
- No unused imports or missing dependencies

## Default Behavior

If no component name provided (`$1` is empty):
1. Ask the user for the component name using AskUserQuestion
2. Suggest naming convention based on the detected project pattern (PascalCase for React, kebab-case for Vue)
