---
description: prepare and publish a new release with changelog
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(git:*)
  - Bash(npm:version)
  - Grep
  - Glob
  - TodoWrite
  - AskUserQuestion
disable-model-invocation: true
---

# Release

Prepare and publish a new release through a multi-phase workflow.

Current version: !`cat package.json 2>/dev/null | grep '"version"' | head -1 | sed 's/.*: "//;s/".*//' || echo "unknown"`
Current branch: !`git branch --show-current`
Unreleased commits: !`git log $(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~10)..HEAD --oneline 2>/dev/null | head -10`

## Guardrails

- Phase 1 must analyze all changes before any modifications
- Never push or publish without explicit user confirmation
- Always create the release from a clean working tree

## Phases

### Phase 1: Analyze Changes

**Goal:** Understand what's being released

1. Read current version from package.json
2. List all commits since last tag
3. Categorize changes (features, fixes, breaking)
4. Check for uncommitted changes (abort if dirty)

**Exit criteria:** Change summary documented, working tree clean

### Phase 2: Version Bump

**Goal:** Determine and apply version number

1. Ask user for version bump type (major/minor/patch) based on changes
2. Update version in package.json
3. Update CHANGELOG.md with categorized changes

**Exit criteria:** Version bumped, changelog updated

### Phase 3: Publish

**Goal:** Create tag and push release

1. Show summary of all changes for final review
2. Ask user to confirm before proceeding
3. Commit version bump and changelog
4. Create git tag
5. Push commit and tag

**Exit criteria:** Tag pushed, release published

## Progress Tracking

Track each phase with TodoWrite for visibility.

## Verification

After release completes, verify:
- `git tag -l` includes the new version tag
- CHANGELOG.md has entry for new version
- package.json shows new version

## Error Recovery

If any phase fails:
1. Do NOT proceed to next phase
2. Show error details
3. If Phase 3 fails, remove local tag with `git tag -d`
