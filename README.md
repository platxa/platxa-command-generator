# Platxa Command Generator

> Autonomous slash command creator for Claude Code CLI. Transforms natural language descriptions into production-ready commands through a multi-phase orchestrated workflow.
>
> **Maintained by**: [Platxa](https://platxa.com) | **License**: MIT | **Version**: 1.0.0

**64 files** | **74 tests** | **7 scripts** | **4 subagents** | **6 command types**

---

## Overview

Platxa Command Generator is a [Claude Code skill](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/skills) that autonomously creates slash commands by orchestrating specialized subagents through a structured pipeline:

```
User describes command
        ↓
   ┌─────────┐     ┌──────────────┐     ┌────────────┐     ┌────────────┐
   │ DISCOVER │ ──▶ │ ARCHITECTURE │ ──▶ │  GENERATE  │ ──▶ │  VALIDATE  │
   │ Research │     │ Type + Plan  │     │ Write .md  │     │ Score ≥7.0 │
   └─────────┘     └──────────────┘     └────────────┘     └─────┬──────┘
                                                                 │
                                              ┌──────────────────┤
                                              │ < 7.0            │ ≥ 7.0
                                         ┌────▼───┐        ┌────▼─────┐
                                         │ REWORK │        │ INSTALL  │
                                         │ (max 2)│        │ Command  │
                                         └────────┘        └──────────┘
```

Each phase uses the Task tool to delegate to specialized subagents defined in `references/agents/`, ensuring deep expertise at every step.

---

## Quick Start

```bash
# Install as a skill
git clone https://github.com/platxa/platxa-command-generator.git
cd platxa-command-generator
./scripts/install-command.sh . --user

# Then in any Claude Code session:
/platxa-command-generator
```

Or invoke directly:

```bash
/platxa-command-generator "Create a command that runs tests with coverage for a specific file"
```

---

## Command Types

The generator classifies commands into six types based on complexity and features:

| Type | Frontmatter | Dynamic Features | Complexity | Use Case |
|------|-------------|-----------------|------------|----------|
| **Basic** | None | None | Low | Simple instructions, checklists |
| **Standard** | `description`, `allowed-tools` | None | Low-Medium | Tool-scoped team commands |
| **Parameterized** | + `argument-hint` | `$1`, `$2` | Medium | Commands with user arguments |
| **Interactive** | + `AskUserQuestion` | User prompts | Medium | Guided wizards, multiple choices |
| **Workflow** | + `TodoWrite`, `Task` | Multi-phase | High | Complex multi-step processes |
| **Plugin** | + `${CLAUDE_PLUGIN_ROOT}` | Plugin paths | Medium-High | Distributed plugin commands |

### Type Decision Tree

```
Does the command need Claude to use specific tools?
├── No → Basic
└── Yes → Does it accept user arguments ($1, $2)?
    ├── No → Standard
    └── Yes → Does it require interactive user input?
        ├── No → Parameterized
        └── Yes → Does it have multiple phases with state?
            ├── No → Interactive
            └── Yes → Is it distributed as a plugin?
                ├── No → Workflow
                └── Yes → Plugin
```

---

## Dynamic Features

Commands support four dynamic features that are resolved at invocation time:

| Feature | Syntax | Example | Resolution |
|---------|--------|---------|------------|
| Positional args | `$1`, `$2` | `/deploy staging` | `$1` = `staging` |
| All arguments | `$ARGUMENTS` | `/search foo bar` | `$ARGUMENTS` = `foo bar` |
| File reference | `@file` | User references a file | Content injected inline |
| Bash execution | `` !`cmd` `` | `` !`git branch --show-current` `` | Output replaces block |
| Plugin root | `${CLAUDE_PLUGIN_ROOT}` | Plugin-relative paths | Absolute plugin path |

---

## Frontmatter Specification

All frontmatter fields are **optional** for commands (Basic type requires none):

```yaml
---
description: generate unit tests for specified module  # ≤60 chars, lowercase verb
allowed-tools:                                          # Valid Claude Code tools
  - Read
  - Write
  - Bash(pytest:*)                                      # Bash filters supported
argument-hint: "[module-path] [options]"                # Bracket format
model: sonnet                                           # opus, sonnet, or haiku
disable-model-invocation: false                         # Prevent AI self-invocation
---
```

Valid tools: `Read`, `Write`, `Edit`, `MultiEdit`, `Glob`, `Grep`, `LS`, `Bash`, `Task`, `WebFetch`, `WebSearch`, `AskUserQuestion`, `TodoWrite`, `KillShell`, `BashOutput`, `NotebookEdit`

---

## Project Structure

```
platxa-command-generator/
├── SKILL.md                           # Main orchestrator entry point
├── references/
│   ├── agents/                        # 4 subagent prompt definitions
│   │   ├── discovery-agent.md         #   Research domain & existing commands
│   │   ├── architecture-agent.md      #   Determine command type & structure
│   │   ├── generation-agent.md        #   Create command .md file
│   │   └── validation-agent.md        #   Quality scoring & compliance
│   ├── templates/                     # 8 command type templates
│   │   ├── basic-template.md          #   No frontmatter
│   │   ├── standard-template.md       #   With allowed-tools
│   │   ├── parameterized-template.md  #   $1/$2 + argument-hint
│   │   ├── interactive-template.md    #   AskUserQuestion workflows
│   │   ├── workflow-template.md       #   Multi-phase + state
│   │   ├── plugin-template.md         #   ${CLAUDE_PLUGIN_ROOT} paths
│   │   ├── command-templates.md       #   Type selection guide
│   │   └── anti-patterns.md           #   Common mistakes to avoid
│   ├── patterns/                      # 22 implementation patterns
│   │   ├── command-types.md           #   Type classification decision tree
│   │   ├── frontmatter-generator.md   #   Field creation rules
│   │   ├── frontmatter-validator.md   #   Validation rules & constraints
│   │   ├── argument-patterns.md       #   $1/$2/$ARGUMENTS usage
│   │   ├── file-reference-patterns.md #   @file reference patterns
│   │   ├── bash-execution-patterns.md #   !`bash` safety & portability
│   │   ├── naming-conventions.md      #   Command naming rules
│   │   ├── domain-discovery.md        #   Research strategies
│   │   ├── content-quality-scorer.md  #   Quality evaluation criteria
│   │   ├── token-budget.md            #   Budget limits & estimation
│   │   ├── state-machine.md           #   Workflow state transitions
│   │   ├── phase-transitions.md       #   Phase progression rules
│   │   ├── quality-gate.md            #   Quality thresholds
│   │   ├── error-handling.md          #   Error recovery patterns
│   │   ├── context-handoff.md         #   Agent-to-agent data flow
│   │   ├── subagent-dispatch.md       #   Task tool delegation
│   │   ├── anti-patterns.md           #   Common anti-patterns catalog
│   │   ├── command-vs-skill-vs-hook.md #  Extension type selection guide
│   │   ├── continuous-learning.md     #   Post-generation improvement loops
│   │   ├── hook-preprocessing.md      #   Hook output filtering patterns
│   │   ├── sequential-composition.md  #   Command pipeline composition
│   │   └── team-sharing.md            #   Multi-user distribution patterns
│   └── spec/
│       └── directory-layout.md        # Repository structure spec
├── scripts/                           # 7 validation & utility scripts
│   ├── validate-all.sh                #   Orchestrates all validators
│   ├── validate-structure.sh          #   File structure checks
│   ├── validate-frontmatter.sh        #   YAML frontmatter validation
│   ├── count-tokens.py                #   Token & line budget enforcement
│   ├── security-check.sh              #   Dangerous pattern scanning
│   ├── install-command.sh             #   Install to user/project/plugin
│   └── check-duplicates.py            #   Duplicate name/description detection
├── tests/                             # 74 tests across 6 modules
│   ├── conftest.py                    #   Pytest fixtures (real file ops)
│   ├── helpers.py                     #   Shared test utilities
│   ├── test_validate_frontmatter.py   #   Frontmatter validation tests
│   ├── test_validate_structure.py     #   Structure validation tests
│   ├── test_count_tokens.py           #   Token budget tests
│   ├── test_security_check.py         #   Security scanning tests
│   ├── test_check_duplicates.py       #   Duplicate detection tests
│   └── test_integration.py            #   Full pipeline tests
├── assets/
│   └── command-template/
│       └── command.md                 # Blank command template
└── commands/
    └── examples/                      # Example commands
        ├── explain.md                 #   Code explanation command
        ├── test-file.md               #   Test runner command
        └── release.md                 #   Release workflow command
```

---

## Quality Standards

Every generated command passes through a multi-gate validation pipeline:

| Gate | Threshold | Type | Description |
|------|-----------|------|-------------|
| Structure | Pass | Hard | File exists, `.md` extension, not empty, H1 heading required |
| Placeholders | Pass | Hard | No TODO/FIXME/placeholder text (whole-word matching) |
| Prompt Specificity | Pass | Soft | No vague instructions; concrete tool/file references required |
| Frontmatter | Pass | Hard | Valid YAML, known fields only, all constraints enforced |
| Description | ≤ 60 chars | Hard | Lowercase verb start, no placeholders, no angle brackets |
| Token Budget | < 4,000 | Hard | Recommended < 2,000 tokens |
| Line Budget | < 600 | Hard | Recommended < 300 lines |
| Security | Pass | Hard | No dangerous patterns or hardcoded credentials |
| Content Quality | ≥ 7.0/10 | Hard | Clear instructions, examples, no placeholders |
| Duplicates | Pass | Hard | No name collisions or high-similarity matches |

### Scoring Rubric

| Category | Weight | Criteria |
|----------|--------|----------|
| Structure | 20% | Valid file, proper frontmatter |
| Content Quality | 30% | Clear instructions, realistic examples |
| Dynamic Features | 15% | Correct argument handling, safe bash |
| Token Efficiency | 15% | Within budget limits |
| Security | 10% | No dangerous patterns |
| Completeness | 10% | Examples, edge cases, output format |

---

## Installation Methods

### Install as a Skill (Recommended)

```bash
./scripts/install-command.sh . --user     # Install to ~/.claude/skills/
./scripts/install-command.sh . --project  # Install to .claude/skills/
```

### Install Generated Commands

```bash
# Install a generated command
./scripts/install-command.sh commands/my-command.md --user     # ~/.claude/commands/
./scripts/install-command.sh commands/my-command.md --project  # .claude/commands/
./scripts/install-command.sh commands/my-command.md --plugin my-plugin  # Plugin namespace
```

### Manual Copy

```bash
cp commands/my-command.md ~/.claude/commands/
```

---

## Validation

```bash
# Run all validators on a command
./scripts/validate-all.sh commands/my-command.md

# Run individual validators
./scripts/validate-structure.sh commands/my-command.md
./scripts/validate-frontmatter.sh commands/my-command.md
python3 scripts/count-tokens.py commands/my-command.md
./scripts/security-check.sh commands/my-command.md
python3 scripts/check-duplicates.py commands/my-command.md

# Self-validate the generator
./scripts/validate-all.sh .
```

Example output:

```
Validation Results for: my-command.md
══════════════════════════════════════
  Structure:        PASS
  Frontmatter:      PASS
  Token Budget:     PASS (850 / 4000)
  Security:         PASS
  Content Quality:  7.2 / 6.0  PASS
──────────────────────────────────────
  Overall Score:    8.1 / 7.0  PASS
  Result: PASS
══════════════════════════════════════
```

---

## Example Commands

Three example commands are included in `commands/examples/`:

| Command | Type | Description |
|---------|------|-------------|
| `explain.md` | Basic | Explains code in a specified file |
| `test-file.md` | Parameterized | Runs tests for a specific file with coverage |
| `release.md` | Workflow | Multi-step release workflow with changelog |

Use these as references when creating new commands or to test the validation pipeline.

---

## Development

### Prerequisites

- Python 3.10+
- `pip install -r requirements.txt` (tiktoken, pyyaml, pytest)

### Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_validate_frontmatter.py -v

# Run tests matching pattern
pytest -k "test_valid_description"

# Validate the generator itself
./scripts/validate-all.sh .

# Check token budget
python3 scripts/count-tokens.py .
```

### Testing Philosophy

All tests use **real file system operations** — no mocks, no simulations. Tests create actual `.md` files in temporary directories, execute validation scripts via subprocess, and verify real output.

---

## Subagent Architecture

The generator delegates each workflow phase to a specialized subagent via the Task tool:

| Phase | Agent | Subagent Type | Purpose |
|-------|-------|---------------|---------|
| Discovery | `discovery-agent.md` | `Explore` | Research domain, analyze existing commands |
| Architecture | `architecture-agent.md` | `general-purpose` | Classify type, design structure |
| Generation | `generation-agent.md` | `general-purpose` | Create command `.md` file |
| Validation | `validation-agent.md` | `general-purpose` | Score quality, check compliance |

Each agent receives context from the previous phase via structured JSON handoffs defined in `references/patterns/context-handoff.md`.

---

## Related Projects

| Project | Description |
|---------|-------------|
| [platxa-skill-generator](https://github.com/platxa/platxa-skill-generator) | Generates Claude Code skills (multi-file directories) |
| [platxa-command-builder](https://github.com/platxa/platxa-skill-generator) | Skill for manually building commands (non-autonomous) |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full submission guide.

```bash
# Quick validation before submitting
pytest tests/ -v
./scripts/validate-all.sh .
python3 scripts/count-tokens.py .
```

Commit format: `type(scope): description` (e.g., `feat(templates): add workflow template`)

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Created by**: DJ Patel — Founder & CEO, Platxa | https://platxa.com
