# Command Naming Conventions

Rules for naming commands and their files.

## File Name Rules

- Lowercase hyphen-case: `my-command.md`
- `.md` extension required
- No spaces, underscores, or special characters
- Maximum 64 characters (including .md)
- Descriptive but concise

## Naming Patterns

### Verb-First (Preferred)

```
deploy-staging.md
run-tests.md
generate-docs.md
check-coverage.md
fix-imports.md
```

### Domain-Scoped

```
git-sync.md
docker-build.md
api-test.md
db-migrate.md
k8s-deploy.md
```

### Action-Target

```
lint-python.md
format-code.md
review-pr.md
analyze-deps.md
create-component.md
```

## Naming Anti-Patterns

| Bad | Why | Better |
|-----|-----|--------|
| `cmd.md` | Too vague | `deploy-app.md` |
| `my_command.md` | Underscores | `my-command.md` |
| `DoStuff.md` | CamelCase | `do-stuff.md` |
| `a-very-long-command-name-that-describes-everything-it-does.md` | Too long | `generate-tests.md` |
| `1-deploy.md` | Starts with number | `deploy-step1.md` |

## Invocation

Commands are invoked by filename without extension:
- `deploy-staging.md` → `/deploy-staging`
- `run-tests.md` → `/run-tests`
- `generate-docs.md` → `/generate-docs`

## Plugin Namespacing

Plugin commands are namespaced:
- `plugin-name/commands/build.md` → `/plugin-name:build`

## Directory Organization

For large command libraries, organize commands into subdirectories. Subdirectory names become prefixes:

```
.claude/commands/
  deploy-staging.md          → /deploy-staging
  workflows/
    release.md               → /workflows:release
    onboard.md               → /workflows:onboard
  tools/
    lint.md                  → /tools:lint
    format.md                → /tools:format
  db/
    migrate.md               → /db:migrate
    seed.md                  → /db:seed
```

**When to organize into directories**:
- More than 10 commands in a single directory
- Commands naturally group by domain (db, api, deploy)
- Team needs to discover commands by category

**Naming the directories**:
- Use short, lowercase names (1-2 words)
- Group by domain, not by action
- Avoid nesting deeper than one level

## Duplicate Prevention

Before naming a command:
1. Check `~/.claude/commands/` for existing user commands
2. Check `.claude/commands/` for existing project commands
3. Avoid names that collide with built-in CLI commands
