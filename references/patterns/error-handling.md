# Error Handling

Error recovery patterns for the command generation workflow.

## Error Categories

### Recoverable Errors

| Error | Phase | Recovery |
|-------|-------|----------|
| Discovery timeout | DISCOVERY | Retry with simpler queries |
| Insufficient research | DISCOVERY | Route to CLARIFY |
| Template not found | GENERATION | Fall back to Standard template |
| Over token budget | GENERATION | Trim content, move to concise |
| Validation warnings | VALIDATION | Show warnings, allow proceed |
| Low quality score | VALIDATION | Route to REWORK |

### Unrecoverable Errors

| Error | Phase | Action |
|-------|-------|--------|
| State file corrupted | Any | Start fresh, warn user |
| Missing required input | INIT | Re-prompt user |
| Install path not writable | INSTALLATION | Report error, suggest alternative |
| User cancellation | Any | Clean up state, exit |

## Recovery Patterns

### Retry with Backoff

```
Attempt 1: Full discovery query
Attempt 2: Simplified query (fewer search terms)
Attempt 3: Manual fallback (ask user for domain info)
```

### Graceful Degradation

```
IF template load fails:
    Use generic Standard template
IF token count unavailable (no tiktoken):
    Use word-count estimation (words * 1.3)
IF security check unavailable:
    Skip with warning, manual review required
```

### State Recovery

```
IF state file exists AND phase != "complete":
    Ask user: "Resume existing session or start new?"
    IF resume: Load state and continue from stored phase
    IF new: Clean up old state, start fresh
```

## Error Reporting

Always include:
1. What failed (specific error)
2. Why it failed (root cause if known)
3. What to do next (recovery action)
4. How to prevent it (if applicable)
