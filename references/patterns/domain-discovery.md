# Domain Discovery

Research patterns for understanding the command's target domain.

## Discovery Process

### 1. Understand User Intent

What does the user want to accomplish?
- What task is being automated?
- What manual steps are being replaced?
- What output is expected?

### 2. Analyze Existing Commands

Search for similar commands:
```
~/.claude/commands/     # User-level commands
.claude/commands/       # Project-level commands
```

Check for overlap or gaps in existing commands.

### 3. Identify Tool Requirements

Map tasks to Claude Code tools:

| Task | Tools Needed |
|------|-------------|
| Read files | Read, Glob, Grep |
| Modify files | Write, Edit, MultiEdit |
| Run commands | Bash |
| Search web | WebSearch, WebFetch |
| User input | AskUserQuestion |
| Track progress | TodoWrite |
| Delegate work | Task |

### 4. Determine Dynamic Features

Does the command need:
- User arguments? → $1, $2, $ARGUMENTS
- File content injection? → @file
- Runtime information? → !`bash`
- Plugin-local files? → ${CLAUDE_PLUGIN_ROOT}

### 5. Assess Complexity

| Complexity | Indicators | Type |
|-----------|-----------|------|
| Low | Single action, no decisions | Basic/Standard |
| Medium | User input, multiple steps | Parameterized/Interactive |
| High | Multi-phase, state tracking | Workflow |

## Output

Discovery produces a JSON summary:
```json
{
  "domain": "testing",
  "purpose": "Generate unit tests for Python modules",
  "command_type": "Parameterized",
  "tools": ["Read", "Write", "Bash"],
  "arguments": [{"name": "$1", "purpose": "module path"}],
  "existing_commands": ["run-tests"],
  "gaps": ["no test generation command exists"]
}
```
