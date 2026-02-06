# Context Handoff

Patterns for passing context between workflow phases and subagents.

## Phase-to-Phase Handoff

Each phase produces output that feeds the next phase:

```
INIT → {description, target_users}
  ↓
DISCOVERY → {domain, command_type, tools, arguments, gaps}
  ↓
ARCHITECTURE → {type, frontmatter, sections, dynamic_features, budget}
  ↓
GENERATION → {command_file_path, content}
  ↓
VALIDATION → {score, errors, warnings, recommendations}
  ↓
INSTALLATION → {install_path, verified}
```

## Handoff Format

State is persisted as JSON in `.claude/command_creation_state.json`:

```json
{
  "phase": "architecture",
  "input": {
    "description": "generate unit tests for Python modules",
    "target_users": "Python developers"
  },
  "discovery": {
    "status": "complete",
    "output": {
      "domain": "testing",
      "command_type": "Parameterized",
      "tools": ["Read", "Write", "Bash"],
      "arguments": [{"name": "$1", "purpose": "module path"}]
    }
  },
  "architecture": {
    "status": "in_progress"
  }
}
```

## Subagent Context Injection

When dispatching a subagent via Task tool, include:

1. **Previous phase output** (from state file)
2. **User input** (description, clarifications)
3. **Relevant templates** (loaded from references/)
4. **Constraints** (token budget, type requirements)

## Minimal Context Principle

Only pass context relevant to the current phase:
- Discovery agent: user description + existing commands
- Architecture agent: discovery output + type guidelines
- Generation agent: architecture blueprint + template
- Validation agent: command file path + quality criteria

## Context Size Management

Keep handoff data under 1000 tokens per phase to preserve subagent context window for actual work.
