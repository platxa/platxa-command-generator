# Token Budget Constraints

Guidelines for keeping commands efficient and within limits.

## Budget Overview

### Command Files (Single .md)

| Metric | Recommended | Hard Limit |
|--------|-------------|------------|
| Tokens | 2,000 | 4,000 |
| Lines | 300 | 600 |

### Skill Directories (Self-Validation)

| Component | Limit |
|-----------|-------|
| SKILL.md | 5,000 tokens / 500 lines |
| Single reference | 2,000 tokens |
| All references | 30,000 tokens |
| Total skill | 35,000 tokens |

## Why Token Budgets Matter

1. **Context Window**: Commands consume context; large commands crowd out user content
2. **Responsiveness**: Smaller commands load faster
3. **Focus**: Concise commands stay on task

## Line Budget Allocation (Commands)

| Section | Lines | Purpose |
|---------|-------|---------|
| Frontmatter | 5-10 | Metadata |
| Title + Context | 5-15 | What and why |
| Workflow | 30-80 | Step-by-step |
| Examples | 20-50 | Usage demos |
| Output format | 10-20 | Expected results |
| **Total** | **~70-175** | Well within 300 |

## Token Estimation

```
1 token ~ 4 characters (English)
1 token ~ 0.75 words
100 words ~ 130 tokens
1 line of code ~ 10-15 tokens
```

## Efficiency Tips

1. Use bullet points over paragraphs
2. Tables for structured data
3. Minimal code blocks (show structure, not volume)
4. No verbose introductions ("In this command we will...")
5. No repeated information

## Red Flags

- [ ] Description > 60 characters
- [ ] More than 8 tools in allowed-tools
- [ ] Examples longer than 30 lines each
- [ ] Verbose explanations of obvious steps
- [ ] Duplicate content across sections
