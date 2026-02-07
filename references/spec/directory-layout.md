# Directory Layout

Expected structure for the platxa-command-generator repository.

## Repository Structure

```
platxa-command-generator/
├── SKILL.md                          # Main orchestrator (the generator itself)
├── CLAUDE.md                         # Dev instructions
├── CONTRIBUTING.md                   # Contribution guidelines
├── LICENSE                           # MIT license
├── pyproject.toml                    # Python project config
├── pytest.ini                        # Test config
├── requirements.txt                  # Dependencies
├── .gitignore                        # Git ignores
│
├── references/
│   ├── agents/                       # Subagent prompt definitions
│   │   ├── discovery-agent.md        # Research domain, existing commands
│   │   ├── architecture-agent.md     # Determine command type + structure
│   │   ├── generation-agent.md       # Create the command .md file
│   │   └── validation-agent.md       # Quality scoring + spec compliance
│   │
│   ├── templates/                    # Command type templates
│   │   ├── basic-template.md         # No frontmatter
│   │   ├── standard-template.md      # With allowed-tools
│   │   ├── parameterized-template.md # $1/$2 + argument-hint
│   │   ├── interactive-template.md   # AskUserQuestion workflows
│   │   ├── workflow-template.md      # Multi-phase + state
│   │   ├── plugin-template.md        # ${CLAUDE_PLUGIN_ROOT} paths
│   │   ├── command-templates.md      # Template selection guide
│   │   └── anti-patterns.md          # Common mistakes
│   │
│   ├── patterns/                     # Implementation patterns
│   │   ├── command-types.md          # Type decision tree
│   │   ├── frontmatter-generator.md  # Frontmatter creation rules
│   │   ├── frontmatter-validator.md  # Validation rules
│   │   ├── argument-patterns.md      # $1/$2/$ARGUMENTS patterns
│   │   ├── file-reference-patterns.md# @file patterns
│   │   ├── bash-execution-patterns.md# !`bash` patterns
│   │   ├── naming-conventions.md     # Command naming rules
│   │   ├── domain-discovery.md       # Research patterns
│   │   ├── content-quality-scorer.md # Quality scoring criteria
│   │   ├── token-budget.md           # Budget limits
│   │   ├── state-machine.md          # Workflow state transitions
│   │   ├── phase-transitions.md      # Phase progression rules
│   │   ├── quality-gate.md           # Quality thresholds
│   │   ├── error-handling.md         # Error recovery patterns
│   │   ├── context-handoff.md        # Agent-to-agent handoff
│   │   └── subagent-dispatch.md      # Task tool delegation
│   │
│   └── spec/
│       └── directory-layout.md       # This file
│
├── scripts/
│   ├── validate-all.sh               # Run all validators
│   ├── validate-structure.sh         # Check command file structure
│   ├── validate-frontmatter.sh       # Validate command frontmatter
│   ├── count-tokens.py               # Token/line budget checker
│   ├── security-check.sh             # Security scanning
│   ├── install-command.sh            # Install to user/project/plugin
│   └── check-duplicates.py           # Duplicate detection
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Fixtures + helpers
│   ├── helpers.py                    # Shared test utilities
│   ├── test_validate_frontmatter.py  # Frontmatter validation tests
│   ├── test_validate_structure.py    # Structure validation tests
│   ├── test_count_tokens.py          # Token counting tests
│   ├── test_security_check.py        # Security scan tests
│   ├── test_integration.py           # Full validation workflow
│   └── test_check_duplicates.py      # Duplicate detection tests
│
├── commands/                         # Generated commands
│   └── .gitkeep
│
├── assets/
│   └── command-template/
│       └── command.md                # Blank command template
│
└── .github/
    └── workflows/
        └── ci.yml                    # Test + validate + lint
```

## Generated Command Structure

Commands are single .md files:

```
command-name.md
```

### With Frontmatter (Standard+)

```markdown
---
description: verb phrase ≤60 chars
allowed-tools:
  - Tool1
  - Tool2
argument-hint: [arg description]
---

# Command Title

Instructions...
```

### Without Frontmatter (Basic)

```markdown
# Command Title

Instructions...
```

## Install Locations

| Location | Path | Scope |
|----------|------|-------|
| User | `~/.claude/commands/` | All projects |
| Project | `.claude/commands/` | Single project |
| Plugin | `.claude/plugins/{ns}/commands/` | Plugin users |
