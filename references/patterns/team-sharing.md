# Team Sharing

How to share Claude Code slash commands with your team via git.

## Project Commands (Shared via Git)

Commands in `.claude/commands/` are project-scoped and should be committed to version control:

```bash
# Add commands to git
git add .claude/commands/
git commit -m "Add team slash commands"
git push
```

Team members get the commands automatically when they pull:

```bash
git pull  # Commands available immediately via /command-name
```

## User Commands (Personal, Not Shared)

Commands in `~/.claude/commands/` are personal and not tracked by git.

| Location | Scope | Shared | Invocation |
|----------|-------|--------|------------|
| `.claude/commands/deploy.md` | Project | Yes (git) | `/deploy` |
| `~/.claude/commands/scratch.md` | User | No | `/scratch` |

## Recommended `.gitignore`

Do **not** gitignore `.claude/commands/`. The `.claude/` directory may contain other files you want to ignore:

```gitignore
# Claude Code - ignore settings, keep commands
.claude/settings.json
.claude/settings.local.json
!.claude/commands/
```

## Workflow for Adding a Team Command

1. Create the command in `.claude/commands/`:
   ```bash
   /generate my-command   # Or write manually
   ```

2. Validate before committing:
   ```bash
   ./scripts/validate-all.sh .claude/commands/my-command.md
   ```

3. Commit and push:
   ```bash
   git add .claude/commands/my-command.md
   git commit -m "Add /my-command for team use"
   git push
   ```

4. Team members pull and use immediately — no installation step needed.

## Plugin Commands (Distributed via npm/pip)

For commands shared across multiple projects, package them as a plugin:

```
my-plugin/
  plugin.json           # Plugin manifest
  commands/
    build.md            # /my-plugin:build
    test.md             # /my-plugin:test
```

Install via package manager:

```bash
npm install --save-dev @team/claude-plugin
```

See `references/templates/plugin-template.md` for plugin command structure.

## Organizing Shared Commands

For teams with many commands, use subdirectories:

```
.claude/commands/
  deploy.md             # /deploy
  db/
    migrate.md          # /db:migrate
    seed.md             # /db:seed
  ci/
    release.md          # /ci:release
```

See `references/patterns/naming-conventions.md` for directory organization rules.
