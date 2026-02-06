# Content Quality Scorer

Criteria for scoring command content quality.

## Scoring Dimensions

### 1. Clarity (0-10)

| Score | Criteria |
|-------|---------|
| 9-10 | Every instruction is specific, actionable, unambiguous |
| 7-8 | Most instructions clear, minor ambiguity |
| 5-6 | Some vague instructions, needs interpretation |
| 3-4 | Frequently unclear, contradictory |
| 1-2 | Incomprehensible or missing |

### 2. Completeness (0-10)

| Score | Criteria |
|-------|---------|
| 9-10 | All cases covered, fallbacks defined, edge cases handled |
| 7-8 | Primary workflow complete, some edges missing |
| 5-6 | Basic workflow present, significant gaps |
| 3-4 | Partial instructions, many missing steps |
| 1-2 | Placeholder or stub content |

### 3. Consistency (0-10)

| Score | Criteria |
|-------|---------|
| 9-10 | No contradictions, uniform style, coherent flow |
| 7-8 | Minor inconsistencies in style |
| 5-6 | Some conflicting instructions |
| 3-4 | Frequent contradictions |
| 1-2 | Internally incoherent |

### 4. Efficiency (0-10)

| Score | Criteria |
|-------|---------|
| 9-10 | Concise, no redundancy, within recommended budget |
| 7-8 | Mostly efficient, minor verbosity |
| 5-6 | Some bloat, approaching budget |
| 3-4 | Significant waste, over recommended budget |
| 1-2 | Excessive, over hard limit |

## Overall Score

```
overall = (clarity * 0.35) + (completeness * 0.30) +
          (consistency * 0.20) + (efficiency * 0.15)
```

## Pass Threshold

- Score >= 7.0: PASS
- Score 5.0-6.9: WARN (improvements suggested)
- Score < 5.0: FAIL (must rework)

## Bonus Points

Add to overall score (capped at 10.0):

| Criterion | Bonus | How to Detect |
|-----------|-------|---------------|
| Verification section present | +0.5 | `## Verification` heading with actionable checks |
| Guardrails section present | +0.3 | `## Guardrails` heading with read-before-act rules |
| Default Behavior for $1/$2 | +0.3 | `## Default Behavior` heading when command uses arguments |
| Examples section present | +0.3 | `## Examples` or `## Example` heading with usage demonstrations |
| Examples are realistic | +0.2 | Examples use plausible file paths, commands, data |

```
final_score = min(10.0, overall + bonus)
```

## Quick Checks

- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No contradictory instructions
- [ ] All tool references are valid
- [ ] Arguments ($1/$2) have fallback handling
- [ ] Output format is specified
- [ ] Examples are realistic
