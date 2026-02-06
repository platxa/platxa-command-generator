# Quality Gate

Enforce minimum quality thresholds before command installation.

## Gate Thresholds

| Gate | Threshold | Type | Bypass |
|------|-----------|------|--------|
| Overall Score | >= 7.0 | Hard | No |
| Structure Valid | Pass | Hard | No |
| Frontmatter Valid | Pass | Hard | No |
| Token Budget | Pass | Hard | No |
| Security Check | Pass | Hard | No |
| Content Quality | >= 6.0 | Soft | With warning |

## Gate Checks

### 1. Structure (Hard)
- File exists and is readable
- Not empty
- Has .md extension

### 2. Frontmatter (Hard)
- Valid YAML if present
- All fields within constraints
- No unknown fields

### 3. Token Budget (Hard)
- Under 4000 tokens (hard limit)
- Under 600 lines (hard limit)
- Warning if over 2000 tokens or 300 lines

### 4. Security (Hard)
- No dangerous patterns (piped remote execution, destructive filesystem commands)
- No hardcoded credentials
- No data exfiltration patterns

### 5. Content Quality (Soft)
- Clear, specific instructions
- No placeholder content
- Examples provided (recommended)
- Argument fallbacks defined (if parameterized)

## Gate Results

```
Quality Gate Check
══════════════════════════════════════
  Structure:        ✓ PASS
  Frontmatter:      ✓ PASS
  Token Budget:     ✓ PASS (850 / 4000)
  Security:         ✓ PASS
  Content Quality:  7.2 / 6.0  ✓ PASS
──────────────────────────────────────
  Overall Score:    8.1 / 7.0  ✓ PASS
  Result: PASS
══════════════════════════════════════
```

## Failure Actions

- Hard gate failure → Block installation, show errors
- Soft gate failure → Allow with warning, suggest improvements
- Overall < 7.0 → Route to REWORK phase
