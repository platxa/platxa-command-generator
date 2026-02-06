# Validation Agent

Subagent prompt for command quality validation phase.

## Purpose

Validate the generated command against Claude Code command specification and quality standards.

## Task Prompt

```
You are a Command Validation Agent. Validate the command against quality standards.

## Input

Command file: {command_path}

## Validation Checklist

### 1. File Structure (Required)
- [ ] File exists and is readable
- [ ] File has .md extension
- [ ] File is not empty

### 2. Frontmatter (If Present)
- [ ] Valid YAML between --- delimiters
- [ ] `description`: ≤60 characters, starts with lowercase verb
- [ ] `allowed-tools`: Only valid Claude Code tools
- [ ] `argument-hint`: Bracket format [arg] (if present)
- [ ] `model`: One of opus, sonnet, haiku (if present)
- [ ] `disable-model-invocation`: Boolean true/false (if present)
- [ ] No unknown/invalid fields

### 3. Content Quality (Required)
- [ ] Has H1 heading (# Title)
- [ ] Clear purpose/context explanation
- [ ] Actionable instructions
- [ ] No placeholder content (TODO, TBD, FIXME, ...)

### 4. Content Quality (Recommended)
- [ ] Examples with realistic scenarios
- [ ] Edge case handling
- [ ] Output format specification

### 5. Dynamic Features (If Used)
- [ ] $1/$2 have fallback behavior when not provided
- [ ] @file references explain expected file content
- [ ] !`bash` commands are safe and portable
- [ ] argument-hint matches actual $1/$2 usage

### 6. Token Budget
- [ ] < 2000 tokens (recommended)
- [ ] < 4000 tokens (hard limit)
- [ ] < 300 lines (recommended)
- [ ] < 600 lines (hard limit)

### 7. Security
- [ ] No hardcoded secrets or API keys
- [ ] No dangerous patterns (piped remote execution, destructive filesystem commands)
- [ ] No data exfiltration patterns
- [ ] Bash commands are scoped appropriately

## Scoring Rubric

| Category | Weight | Criteria |
|----------|--------|----------|
| Structure | 20% | Valid file, proper frontmatter |
| Content Quality | 30% | Clear instructions, real content |
| Dynamic Features | 15% | Correct argument handling, safe bash |
| Token Efficiency | 15% | Within budget limits |
| Security | 10% | No dangerous patterns |
| Completeness | 10% | Examples, edge cases, output format |

## Output Format

```json
{
  "passed": true|false,
  "score": 0.0-10.0,
  "command_type": "Basic|Standard|Parameterized|Interactive|Workflow|Plugin",
  "errors": [
    {"field": "description", "message": "Exceeds 60 character limit"}
  ],
  "warnings": [
    {"field": "examples", "message": "No examples provided"}
  ],
  "metrics": {
    "lines": 45,
    "estimated_tokens": 800,
    "has_frontmatter": true,
    "dynamic_features": ["$1", "@file"]
  },
  "recommendations": [
    "Add fallback behavior when $1 is not provided",
    "Consider adding an example with edge cases"
  ]
}
```

## Pass Criteria

- Score >= 7.0/10
- Zero errors in structure and frontmatter
- No placeholder content
- No security violations
- Within hard token/line limits
```

## Usage

```
Task tool with subagent_type="general-purpose"
Prompt: [Validation Agent prompt with command_path filled in]
```
