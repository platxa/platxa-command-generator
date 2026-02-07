---
description: generate full page with layout, SEO, and error handling
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
argument-hint: [page-name]
---

# Frontend Page Generator

Generate a production-ready page with layout, SEO, and error handling for: $1

## Project Context

Framework: !`cat package.json 2>/dev/null | grep -oE '"(next|nuxt|svelte|remix|react-router)":' | head -1 | tr -d '":' || echo "not detected"`
TypeScript: !`test -f tsconfig.json && echo "yes" || echo "no"`
Router: !`grep -l 'app/.*page\.\(tsx\|js\)' -r . 2>/dev/null | head -1 && echo "app-router" || (test -d pages && echo "pages-router" || echo "not detected")`

## Guardrails

- Read existing pages before generating to match project patterns
- Never overwrite existing files without user confirmation
- Follow the project's routing convention (file-based or config-based)
- Use the project's existing data fetching approach (SSR, SSG, CSR)
- Preserve the existing layout hierarchy — nest within parent layouts

## Workflow

### Step 1: Detect Project Stack

Use Glob and Read to determine:

1. **Framework**: Check `package.json` for next, nuxt, @sveltejs/kit, remix, or react-router-dom
2. **Router type**: App Router (`app/` dir) vs Pages Router (`pages/` dir) vs config-based
3. **Language**: Check for `tsconfig.json` (TypeScript) or `.js` pages
4. **Styling**: Check for tailwind.config, CSS modules, styled-components, or emotion
5. **Data fetching**: Check for existing loader/getServerSideProps/server.ts patterns
6. **SEO approach**: Check for metadata exports, Head components, or useSeoMeta usage
7. **Page directory**: Find where pages live (`app/`, `pages/`, `src/routes/`, `src/app/`)

### Step 2: Gather Requirements

Use AskUserQuestion for choices that cannot be auto-detected:

**Question 1 (only if framework not detected): Which framework?**
- Next.js App Router (Recommended)
- Next.js Pages Router
- Nuxt 3
- SvelteKit

**Question 2: Page type?**
- Landing (hero, CTA, testimonials)
- Dashboard (KPIs, charts, tables)
- List/Index (filterable table, pagination)
- Form (validation, submission, confirmation)

**Question 3: Which features to include? (multiSelect: true)**
- SEO metadata (Recommended)
- Loading state (skeleton screen)
- Error boundary with recovery
- Breadcrumb navigation

### Step 3: Analyze Existing Patterns

Read 2-3 existing pages in the project to match:

- Route naming: kebab-case vs camelCase, dynamic segments syntax
- Layout usage: shared layouts, nested layouts, layout groups
- Data fetching: server components vs client, loader vs getServerSideProps
- SEO pattern: metadata export vs Head component vs composable
- Error handling: error.tsx vs ErrorBoundary vs try/catch
- Loading pattern: loading.tsx vs Suspense vs inline skeletons

### Step 4: Generate Files

Create files matching detected patterns per framework:

**Next.js App Router** (`app/{page-name}/`):
- `page.tsx` — Server component with metadata export, semantic HTML landmarks
- `layout.tsx` — Only if page needs its own nested layout
- `loading.tsx` — Skeleton screen matching page structure
- `error.tsx` — Client component with `'use client'`, error + reset props
- `not-found.tsx` — Custom 404 for the route segment

**Next.js Pages Router** (`pages/`):
- `{page-name}.tsx` — Page component with getServerSideProps/getStaticProps
- `next/head` for SEO with title, description, OG tags

**Nuxt 3** (`pages/`):
- `{page-name}.vue` — Page with definePageMeta and useSeoMeta composable

**SvelteKit** (`src/routes/{page-name}/`):
- `+page.svelte` — Page component with svelte:head for SEO
- `+page.server.ts` — Server load function for data fetching
- `+layout.svelte` — Only if page needs nested layout
- `+error.svelte` — Error page using $page.error store

**All frameworks — SEO metadata includes:**
- Title (50-60 chars), description (150-160 chars)
- Open Graph tags (og:title, og:description, og:image)
- Canonical URL
- JSON-LD structured data where appropriate

**All frameworks — accessibility includes:**
- Semantic HTML landmarks (header, nav, main, footer)
- Single h1 per page, proper heading hierarchy
- Skip navigation link as first focusable element
- Focus management on route transitions

### Step 5: Verify

Run project verification:
- Type check: `pnpm typecheck` or `npx tsc --noEmit`
- Lint: `pnpm lint` on the new files
- Dev server: Confirm page renders at expected route

## Generated Files

| Artifact | Next.js App Router | Next.js Pages | Nuxt 3 | SvelteKit |
|----------|-------------------|---------------|--------|-----------|
| Page | `app/{name}/page.tsx` | `pages/{name}.tsx` | `pages/{name}.vue` | `src/routes/{name}/+page.svelte` |
| Layout | `app/{name}/layout.tsx` | — | — | `src/routes/{name}/+layout.svelte` |
| Loading | `app/{name}/loading.tsx` | — | — | — |
| Error | `app/{name}/error.tsx` | — | — | `src/routes/{name}/+error.svelte` |
| Server data | — | — | — | `src/routes/{name}/+page.server.ts` |

Paths adapt to the project's detected structure. Only generate files that the framework supports and the user selected.

## Verification

After generation, verify:
- Page renders without TypeScript errors
- Route is accessible at the expected URL path (`/{page-name}`)
- SEO metadata appears correctly (check page source or dev tools)
- Loading state displays while data is fetching
- Error boundary catches and displays errors with a recovery button
- No unused imports or missing dependencies
- Heading hierarchy is correct (single h1, sequential levels)

## Default Behavior

If no page name provided (`$1` is empty):
1. Ask the user for the page name using AskUserQuestion
2. Suggest naming convention based on the detected framework (kebab-case for routes)
