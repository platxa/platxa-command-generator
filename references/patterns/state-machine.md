# Workflow State Machine

State management for command generation workflow.

## State Diagram

```
┌──────┐     ┌──────┐     ┌───────────┐     ┌──────────────┐
│ IDLE │────▶│ INIT │────▶│ DISCOVERY │────▶│ ARCHITECTURE │
└──────┘     └──────┘     └───────────┘     └──────────────┘
                                │                    │
                                │ (gaps)             │
                                ▼                    ▼
                          ┌─────────┐        ┌────────────┐
                          │ CLARIFY │        │ GENERATION │
                          └─────────┘        └────────────┘
                                │                    │
                                └────────┬───────────┘
                                         ▼
                                  ┌────────────┐
                                  │ VALIDATION │
                                  └────────────┘
                                    │       │
                          (< 7.0)   │       │  (>= 7.0)
                                    ▼       ▼
                             ┌────────┐  ┌──────────────┐
                             │ REWORK │  │ INSTALLATION │
                             └────────┘  └──────────────┘
                                  │             │
                                  └──────┬──────┘
                                         ▼
                                   ┌──────────┐
                                   │ COMPLETE │
                                   └──────────┘
```

## Phase Transitions

| From | To | Trigger |
|------|----|---------|
| IDLE | INIT | User invokes /platxa-command-generator |
| INIT | DISCOVERY | User provides description |
| DISCOVERY | ARCHITECTURE | Sufficiency score >= 0.8 |
| DISCOVERY | CLARIFY | Gaps found |
| CLARIFY | DISCOVERY | User answers questions |
| ARCHITECTURE | GENERATION | Blueprint created |
| GENERATION | VALIDATION | Command file generated |
| VALIDATION | INSTALLATION | Score >= 7.0 |
| VALIDATION | REWORK | Score < 7.0 |
| REWORK | GENERATION | Fixes applied |
| INSTALLATION | COMPLETE | File installed |

## State File

Location: `.claude/command_creation_state.json`

```json
{
  "session_id": "cmd_20260207_143022_a1b2c3",
  "phase": "generation",
  "created_at": "2026-02-07T14:30:22Z",
  "input": {
    "description": "generate unit tests",
    "target_users": "Python developers"
  },
  "discovery": {"status": "complete", "output": {}},
  "architecture": {"status": "complete", "command_type": "Parameterized"},
  "generation": {"status": "in_progress"}
}
```

## Error Recovery

| Error | Recovery |
|-------|----------|
| Discovery timeout | Retry with simpler queries |
| Generation failed | Resume from last state |
| Validation failed | Go to REWORK |
| State corrupted | Start fresh, warn user |

## Concurrency

One command creation session per project at a time. Check for existing state file before starting.
