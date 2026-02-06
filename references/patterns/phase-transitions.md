# Phase Transitions

Rules governing transitions between workflow phases.

## INIT Phase

**Entry**: User invokes the generator
**Actions**:
1. Create session ID
2. Ask for command description and purpose
3. Ask for target users

**Exit to DISCOVERY**: User provides description

## DISCOVERY Phase

**Entry**: User input received
**Actions**:
1. Launch discovery subagent via Task tool
2. Search existing commands for overlap
3. Research domain best practices

**Exit to ARCHITECTURE**: Sufficiency score >= 0.8
**Exit to CLARIFY**: Gaps identified

## CLARIFY Phase

**Entry**: Discovery found gaps
**Actions**:
1. Present questions to user via AskUserQuestion
2. Collect answers

**Exit to DISCOVERY**: User provides answers (re-run with context)

## ARCHITECTURE Phase

**Entry**: Discovery sufficient
**Actions**:
1. Classify command type
2. Design frontmatter fields
3. Plan dynamic features
4. Estimate token budget

**Exit to GENERATION**: Blueprint created and within budget

## GENERATION Phase

**Entry**: Architecture blueprint ready
**Actions**:
1. Load appropriate template
2. Generate frontmatter (if needed)
3. Generate command body
4. Write .md file

**Exit to VALIDATION**: File written successfully

## VALIDATION Phase

**Entry**: Command file generated
**Actions**:
1. Run validate-structure.sh
2. Run validate-frontmatter.sh
3. Run count-tokens.py
4. Run security-check.sh
5. Score content quality

**Exit to INSTALLATION**: Score >= 7.0 and no errors
**Exit to REWORK**: Score < 7.0 or errors found

## REWORK Phase

**Entry**: Validation failed
**Actions**:
1. Present issues to user
2. Apply fixes based on feedback
3. Regenerate problematic sections

**Exit to GENERATION**: Fixes applied (max 2 rework cycles)

## INSTALLATION Phase

**Entry**: Validation passed
**Actions**:
1. Ask user for install location (user/project/plugin)
2. Copy file to target
3. Verify installation

**Exit to COMPLETE**: File installed successfully

## Transition Guards

- Max 2 CLARIFY cycles before proceeding with warnings
- Max 2 REWORK cycles before asking user to accept or restart
- Always validate before installation (no bypass)
