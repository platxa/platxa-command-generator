# Command Type Decision Tree

Classify commands into the correct type based on requirements.

## Decision Flow

```
1. Does it need frontmatter?
   NO  → Basic
   YES → Continue

2. Does it accept user arguments ($1/$2)?
   YES → Parameterized
   NO  → Continue

3. Does it need interactive user input?
   YES → Interactive
   NO  → Continue

4. Is it a multi-phase workflow?
   YES → Workflow
   NO  → Continue

5. Is it distributed as a plugin?
   YES → Plugin
   NO  → Standard
```

## Type Definitions

| Type | Frontmatter | Dynamic Features | Complexity |
|------|------------|-----------------|------------|
| Basic | None | None | Low |
| Standard | description, allowed-tools | None | Low-Medium |
| Parameterized | + argument-hint | $1, $2, $ARGUMENTS | Medium |
| Interactive | + AskUserQuestion | User prompts | Medium |
| Workflow | + TodoWrite, Task | Multi-phase state | High |
| Plugin | + ${CLAUDE_PLUGIN_ROOT} | Plugin paths | Medium-High |

## Type Indicators

### Basic
- Simple instructions or checklists
- No tool restrictions needed
- Under 50 lines typically

### Standard
- Needs specific tool access
- Benefits from description in help
- Most team commands

### Parameterized
- Operates on user-specified target
- File paths, module names, patterns
- Invoked as `/command arg1 arg2`

### Interactive
- Multiple configuration choices
- Guided wizards
- Uses AskUserQuestion tool

### Workflow
- 3+ sequential phases
- Benefits from progress tracking
- May be interrupted and resumed

### Plugin
- Distributed via npm/pip
- References plugin-local files
- Uses ${CLAUDE_PLUGIN_ROOT}
