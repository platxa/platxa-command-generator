---
description: generate form with validation, error handling, and a11y
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
argument-hint: "[form-name]"
---

# Frontend Form Generator

Generate a production-ready form with validation, error handling, and accessibility for: $1

## Project Context

Framework: !`cat package.json 2>/dev/null | grep -oE '"(react|next|vue|svelte|remix)":' | head -1 | tr -d '":' || echo "not detected"`
Form library: !`cat package.json 2>/dev/null | grep -oE '"(react-hook-form|formik)":' | head -1 | tr -d '":' || echo "native"`
Validation: !`cat package.json 2>/dev/null | grep -oE '"(zod|yup|joi)":' | head -1 | tr -d '":' || echo "none"`
TypeScript: !`test -f tsconfig.json && echo "yes" || echo "no"`

## Guardrails

- Read existing forms before generating to match project patterns
- Never overwrite existing files without user confirmation
- Follow the project's directory structure and naming conventions
- Use the project's existing form library and validation library
- If no form library is installed, use react-hook-form + zod patterns

## Workflow

### Step 1: Detect Project Stack

Use Glob and Read to determine:

1. **Framework**: Check `package.json` for next, react, vue, svelte, remix
2. **Form library**: Check for react-hook-form, formik, or native controlled inputs
3. **Validation**: Check for zod, yup, or joi in dependencies
4. **Submission pattern**: Next.js App Router (Server Actions with `useActionState`), Remix (`action()` + `Form`), or standard fetch/axios
5. **Styling**: Check for tailwind, CSS modules, styled-components
6. **Form directory**: Find where forms live (search for existing `*Form*` or `*form*` components)

### Step 2: Analyze Existing Patterns

Read 2-3 existing forms or components to match:

- File naming and directory structure
- Import style and export conventions
- Props/types pattern: interface vs type
- Error display approach: inline, toast, summary
- Submit handler pattern: async/await, loading states

### Step 3: Generate Files

Create files matching detected patterns:

**Schema file** (`{name}.schema.ts`):
- Zod/Yup schema defining all field validations
- Inferred TypeScript type from schema (`z.infer<typeof schema>`)
- Export both schema and type for reuse

**Form component** (`{Name}Form.tsx` / `.vue` / `.svelte`):
- Form library integration (react-hook-form `useForm` with zodResolver, or detected equivalent)
- All fields with proper `<label htmlFor>` associations
- Field-level inline errors with `aria-invalid` and `aria-describedby`
- `aria-required="true"` on required fields
- `<fieldset>` + `<legend>` for grouped inputs (radio, checkbox groups)
- Loading state with disabled submit button during submission
- Double-submit prevention
- Focus first errored field on validation failure
- Form-level error summary with `role="alert"` for server errors

**Submit handler**:
- Next.js App Router: Server Action with `useActionState`
- Remix: `action()` export with `Form` component
- Standard: async handler with fetch/axios, try/catch
- Server error mapping: `{ field: "message" }` format with `setError()`

### Step 4: Verify

Run project verification:
- Type check: `pnpm typecheck` or `npx tsc --noEmit`
- Lint: `pnpm lint` on the new files

## Generated Files

| Artifact | Path Pattern |
|----------|-------------|
| Schema | `{form-dir}/{Name}/{Name}.schema.ts` |
| Form | `{form-dir}/{Name}/{Name}Form.tsx` |
| Index | `{form-dir}/{Name}/index.ts` |

Paths adapt to the project's detected structure. If the project uses flat files instead of directories, match that convention.

## Verification

After generation, verify:
- Form renders without TypeScript errors
- All fields have explicit `<label>` elements (never rely on hint text alone)
- Error states display correctly with aria attributes
- Submit handler includes loading state and error handling
- New files follow the same patterns as existing components
- No unused imports or missing dependencies

## Default Behavior

If no form name provided (`$1` is empty):
1. Search the project for existing forms using Glob (`**/*Form*`, `**/*form*`)
2. List found forms and suggest a name based on project conventions
3. Default to generating a "Contact" form as a starting template
