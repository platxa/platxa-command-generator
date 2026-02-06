# Bash Execution Patterns

Patterns for using !`bash` inline execution in commands.

## What !`command` Does

Content inside `` !`command` `` is executed at command load time and the output replaces the backtick block. This enables dynamic content in commands.

## Pattern: Inject Runtime Context

```markdown
# Deploy

Current branch: !`git branch --show-current`
Last commit: !`git log --oneline -1`

Deploy the current branch to the target environment.
```

## Pattern: Detect Project Type

```markdown
# Auto-Format

Project type detected:
!`if [ -f package.json ]; then echo "Node.js"; elif [ -f pyproject.toml ]; then echo "Python"; elif [ -f go.mod ]; then echo "Go"; else echo "Unknown"; fi`

Format all source files using the appropriate formatter.
```

## Pattern: List Available Targets

```markdown
# Run Script

Available scripts:
!`ls scripts/*.sh 2>/dev/null | sed 's|scripts/||' | sed 's|\.sh$||'`

Run the specified script from the scripts/ directory.
```

## Pattern: Environment Information

```markdown
# Environment Check

System: !`uname -s`
Node: !`node --version 2>/dev/null || echo "not installed"`
Python: !`python3 --version 2>/dev/null || echo "not installed"`

Verify the environment meets project requirements.
```

## Safety Rules

- Commands execute with user's permissions
- Keep commands simple and fast
- Handle missing tools gracefully (use `|| echo "fallback"`)
- Never execute destructive commands
- Never expose secrets or credentials
- Avoid commands that take > 1 second

## Best Practices

- Use for read-only context injection
- Provide fallbacks for missing tools
- Keep commands short and portable
- Test commands work on target OS
- Document what each !`command` provides
