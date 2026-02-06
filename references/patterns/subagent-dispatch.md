# Task Tool Subagent Dispatch

How to dispatch Task tool subagents for each workflow phase.

## Subagent Mapping

| Phase | Subagent Type | Agent Prompt | Purpose |
|-------|--------------|--------------|---------|
| Discovery | `Explore` | discovery-agent.md | Research domain |
| Architecture | `general-purpose` | architecture-agent.md | Design structure |
| Generation | `general-purpose` | generation-agent.md | Create command |
| Validation | `general-purpose` | validation-agent.md | Score quality |

## Dispatch Patterns

### Discovery Phase

```
Task(
  subagent_type="Explore",
  description="Research {domain} command patterns",
  prompt="""
    [Load references/agents/discovery-agent.md]

    Command description: {description}
    Target users: {target_users}

    Output: JSON with domain, command_type, tools, arguments, gaps
  """
)
```

**Why Explore**: Optimized for search, codebase exploration, pattern finding.

### Architecture Phase

```
Task(
  subagent_type="general-purpose",
  description="Design {command_name} structure",
  prompt="""
    [Load references/agents/architecture-agent.md]

    Discovery findings: {discovery_json}

    Output: Architecture blueprint JSON
  """
)
```

**Why general-purpose**: Needs reasoning about structure and trade-offs.

### Generation Phase

```
Task(
  subagent_type="general-purpose",
  description="Generate {command_name} file",
  prompt="""
    [Load references/agents/generation-agent.md]
    [Load references/templates/{type}-template.md]

    Architecture: {architecture_json}

    Output: Complete command .md file content
  """
)
```

### Validation Phase

```
Task(
  subagent_type="general-purpose",
  description="Validate {command_name}",
  prompt="""
    [Load references/agents/validation-agent.md]

    Command file: {command_path}

    Output: Validation report with score
  """
)
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Subagent timeout | Retry with simpler prompt |
| Invalid output format | Request structured JSON |
| Subagent failure | Log error, ask user for guidance |

## Parallel Dispatch

Discovery can run multiple searches in parallel:
1. Web search for standards
2. Analyze existing commands
3. Find example patterns

Architecture, Generation, and Validation are sequential (each depends on previous).
