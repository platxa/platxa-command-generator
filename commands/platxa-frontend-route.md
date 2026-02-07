---
description: add new route with page, layout, loading, and error files
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
argument-hint: [path]
---

# Frontend Route Scaffolder

Scaffold route files for: $1

## Project Context

Framework: !`cat package.json 2>/dev/null | grep -oE '"(next|nuxt|svelte|remix|react-router)":' | head -1 | tr -d '":' || echo "not detected"`
TypeScript: !`test -f tsconfig.json && echo "yes" || echo "no"`
Router: !`test -d app && echo "app-router" || (test -d src/routes && echo "file-router" || (test -d pages && echo "pages" || echo "not detected"))`

## Guardrails

- Never overwrite existing route files — abort if the target directory already exists
- Read existing routes before scaffolding to match project conventions exactly
- Create only skeleton files with minimal boilerplate — no business logic
- Preserve the existing layout hierarchy — do not duplicate parent layouts

## Workflow

### Step 1: Detect Project Stack

Use Glob and Read to determine:

1. **Framework**: Check `package.json` dependencies for next, nuxt, @sveltejs/kit, or remix
2. **Language**: Check for `tsconfig.json` — use `.tsx`/`.ts` if present, `.jsx`/`.js` otherwise
3. **Route directory**: Locate root (`app/`, `src/routes/`, `pages/`, `app/routes/`)
4. **Existing patterns**: Find 2-3 existing route directories to detect conventions

### Step 2: Analyze Existing Route Patterns

Read 2-3 existing routes in the project to match:

- File naming: `page.tsx` vs `+page.svelte` vs `route.tsx`
- Export style: default export vs named export, arrow function vs function declaration
- Layout usage: which routes have their own layout vs inherit parent
- Loading/error: which routes include loading and error files
- Data fetching: server components vs loaders vs server files
- Styling approach: Tailwind classes, CSS modules, or styled-components

### Step 3: Scaffold Route Files

Parse `$1` to determine route type:

| Input Pattern | Route Type | Example |
|---------------|-----------|---------|
| `about` | Static | `/about` |
| `blog/[slug]` | Dynamic segment | `/blog/:slug` |
| `docs/[...slug]` | Catch-all | `/docs/*` |
| `(auth)/login` | Route group | `/login` (grouped) |
| `@modal/(.)photo` | Intercept (Next.js) | Parallel route |

**Next.js App Router** — create `app/{path}/`:

```
page.tsx        — default export, server component shell
layout.tsx      — only if $1 contains a route group or is a top-level section
loading.tsx     — skeleton UI compatible with Suspense boundaries
error.tsx       — 'use client' directive, error + reset props
```

**SvelteKit** — create `src/routes/{path}/`:

```
+page.svelte    — script + markup shell
+page.server.ts — empty load function export
+layout.svelte  — only if route needs its own layout
+error.svelte   — error display using $page.error
```

**Nuxt 3** — create `pages/{path}.vue`:

```
{path}.vue      — template + script setup with definePageMeta
[param].vue     — for dynamic segments
```

**Remix** — create `app/routes/{path}.tsx`:

```
{path}.tsx      — loader, action, meta, default export, ErrorBoundary
```

Each file contains only the minimum skeleton: correct imports, proper exports, a comment marking where implementation goes, and framework-required directives (`'use client'` for error boundaries, `export const dynamic` settings).

### Step 4: Verify

After scaffolding:

1. Run `pnpm typecheck` or `npx tsc --noEmit` to confirm no type errors
2. Confirm each generated file has the correct exports for its framework
3. Verify the route path resolves correctly (check against existing route tree)

## Generated Files

| Framework | Files Created |
|-----------|--------------|
| Next.js App Router | `app/{path}/page.tsx`, `loading.tsx`, `error.tsx`, `layout.tsx` (conditional) |
| SvelteKit | `src/routes/{path}/+page.svelte`, `+page.server.ts`, `+error.svelte`, `+layout.svelte` (conditional) |
| Nuxt 3 | `pages/{path}.vue` |
| Remix | `app/routes/{path}.tsx` |

Layout files are only created when the route is a top-level section or uses a route group. Do not create layouts for leaf routes that inherit from a parent.

## Verification

After scaffolding, verify:
- All generated files pass type checking with zero errors
- Each file has the correct framework-specific exports
- Dynamic segments use the correct bracket syntax for the framework
- No existing files were overwritten
- Route group parentheses are preserved in directory names

## Default Behavior

If no route path provided (`$1` is empty):
1. List existing routes using `Glob` to show the current route tree
2. Report the route structure and ask the user to re-run with a path argument
3. Example: "Re-run as `/platxa-frontend-route dashboard/settings` to scaffold that route"
