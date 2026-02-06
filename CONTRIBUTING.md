# Contributing to Platxa Command Generator

Thank you for your interest in contributing to Platxa Command Generator! This document provides guidelines and best practices for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/platxa-command-generator.git
   cd platxa-command-generator
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Types of Contributions

| Type | Description |
|------|-------------|
| **New Command Templates** | Add templates for new command types |
| **Bug Fixes** | Fix issues in existing functionality |
| **Pattern Improvements** | Enhance implementation patterns |
| **Documentation** | Improve README, examples, or inline docs |
| **Script Enhancements** | Better validation or utility scripts |
| **Test Coverage** | Add missing tests or improve assertions |

### Contribution Workflow

1. Check existing [issues](../../issues) and [pull requests](../../pulls)
2. For major changes, open an issue first to discuss
3. Fork and create a feature branch
4. Make your changes following style guidelines
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

### Prerequisites

- Claude Code CLI installed
- Bash shell (for scripts)
- Python 3.10+ (for token counting)

### Testing Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_validate_frontmatter.py -v

# Run all validations on a command
./scripts/validate-all.sh commands/my-command.md

# Check token budget
python3 scripts/count-tokens.py commands/my-command.md

# Security check
./scripts/security-check.sh commands/my-command.md
```

### Testing Command Generation

Install as a local skill and test:

```bash
# Copy to local skills
./scripts/install-command.sh . --user

# Test in Claude Code
# Use: /platxa-command-generator
```

## Pull Request Process

### Before Submitting

1. **Run all tests**:
   ```bash
   pytest tests/ -v
   ```

2. **Validate the main SKILL.md**:
   ```bash
   ./scripts/validate-all.sh .
   ```

3. **Follow commit message format**:
   ```
   type(scope): description
   ```
   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### PR Requirements

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Validation scripts pass
- [ ] Documentation updated (if applicable)
- [ ] Descriptive PR title and body

## Style Guidelines

### Markdown Files

- Use ATX-style headers (`#`, `##`, `###`)
- One sentence per line for easier diffs
- Use fenced code blocks with language specifiers
- Tables should be properly aligned

### Command .md Files

Follow Claude Code slash command specification:

```yaml
---
description: Brief verb-starting description
allowed-tools:
  - Read
  - Write
argument-hint: "[target]"
---
```

All frontmatter fields are optional.

### Shell Scripts

- Include shebang: `#!/usr/bin/env bash`
- Use `set -euo pipefail` for safety
- Quote variables: `"$variable"`
- Add usage comments at the top
- Make scripts executable: `chmod +x script.sh`

### Python Scripts

- Python 3.10+ compatible
- Type hints where applicable
- Follow PEP 8 style

## Reporting Issues

### Bug Reports

Include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Claude Code version)

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Potential implementation approach

## Questions?

- Open an issue for general questions
- Tag maintainers for urgent matters

---

**Thank you for contributing!**

*Created by DJ Patel — Founder & CEO, Platxa | https://platxa.com*
