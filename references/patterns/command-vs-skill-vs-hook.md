# Command vs Skill vs Hook vs Agent

Decision guide for choosing the right Claude Code extension type.

## Quick Decision Matrix

| Need | Use |
|------|-----|
| User-invoked action (`/do-something`) | **Command** |
| Reusable knowledge loaded on demand | **Skill** |
| Automatic validation on tool use | **Hook** |
| Autonomous multi-step task delegation | **Agent** |

## When to Use Each

### Command (Slash Command)

**User types `/command-name` to trigger it.**

Use when:
- Action is user-initiated and on-demand
- Task has a clear start and end
- Output is for the current conversation
- Needs specific tool restrictions (`allowed-tools`)

Examples: `/review`, `/test`, `/deploy`, `/scaffold`

Key files: `.claude/commands/*.md` or `~/.claude/commands/*.md`

### Skill

**Claude loads it automatically when context is relevant.**

Use when:
- Knowledge should persist across conversations
- Content is reference material (conventions, patterns, API docs)
- Multiple commands or agents benefit from the same knowledge
- Size exceeds command token budget (>4000 tokens)

Examples: style guides, API references, architecture docs, coding patterns

Key files: `.claude/skills/<name>/SKILL.md` + `references/`

### Hook

**Runs automatically before/after tool use.**

Use when:
- Validation must happen on every tool call (not just when user remembers)
- Enforcing rules that should never be bypassed
- Pre-commit checks, security gates, format enforcement
- No user action required — fires automatically

Examples: lint on save, block `rm -rf`, require tests before commit

Key files: `.claude/hooks.json` (PreToolUse, PostToolUse, Notification events)

### Agent (Plugin Agent)

**Claude delegates to it via Task tool for autonomous work.**

Use when:
- Task requires multi-step autonomous reasoning
- Specialized expertise benefits from isolated context
- Work can run in parallel with other tasks
- Long-running operations that shouldn't block the conversation

Examples: code reviewer, test generator, security scanner, research agent

Key files: Plugin `agents/*.md` with frontmatter defining `subagent_type`

## Decision Flowchart

```
Does the user explicitly trigger it?
├── YES → Is it a single focused action?
│   ├── YES → COMMAND
│   └── NO (multi-step, autonomous) → AGENT
└── NO → Does it fire on tool use events?
    ├── YES → HOOK
    └── NO → Is it reference knowledge?
        ├── YES → SKILL
        └── NO → Reconsider the need
```

## Combining Extensions

Extensions often work together:

- **Command + Skill**: Command loads skill knowledge for informed action
- **Command + Hook**: Hook validates what the command produces
- **Agent + Skill**: Agent reads skill references for domain expertise
- **Hook + Command**: Hook blocks action, suggests running a command to fix it

## Key Differences

| Aspect | Command | Skill | Hook | Agent |
|--------|---------|-------|------|-------|
| Trigger | User invokes | Auto-loaded | Tool event | Task delegation |
| Scope | Single conversation | Cross-conversation | Every tool call | Isolated context |
| Token cost | Per message | On demand | Minimal | Separate budget |
| User control | Explicit | Implicit | Transparent | Delegated |
| Frontmatter | Optional | Required (`name`) | N/A (JSON config) | Required |
