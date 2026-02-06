#!/usr/bin/env bash
# validate-structure.sh - Validate command file structure
#
# Usage: validate-structure.sh <command-file-or-directory>
#
# For a single .md file: checks it exists, is readable, not empty
# For a directory: checks it contains a SKILL.md (for the generator itself)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
    ((ERRORS++)) || true
}

warn() {
    echo -e "${YELLOW}WARN:${NC} $1" >&2
    ((WARNINGS++)) || true
}

info() {
    echo -e "${GREEN}OK:${NC} $1"
}

usage() {
    echo "Usage: $0 <command-file-or-directory>"
    echo ""
    echo "Validates command file structure."
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo "  -v, --verbose Show detailed output"
    exit 1
}

# Parse arguments
VERBOSE=false
TARGET=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            TARGET="$1"
            shift
            ;;
    esac
done

if [[ -z "$TARGET" ]]; then
    error "Command file or directory required"
    usage
fi

# Determine if target is a directory (generator self-validation) or a command file
if [[ -d "$TARGET" ]]; then
    # Directory mode: check for SKILL.md (self-validation of the generator)
    TARGET=$(cd "$TARGET" 2>/dev/null && pwd) || {
        error "Directory does not exist: $TARGET"
        exit 1
    }
    COMMAND_FILE="$TARGET/SKILL.md"
    SKILL_NAME=$(basename "$TARGET")
    IS_DIR=true
else
    # File mode: validate a single command .md file
    COMMAND_FILE="$TARGET"
    SKILL_NAME=$(basename "$TARGET" .md)
    IS_DIR=false
fi

echo "Validating structure: $SKILL_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check 1: File exists
echo ""
echo "Checking required files..."

if [[ -f "$COMMAND_FILE" ]]; then
    info "$(basename "$COMMAND_FILE") exists"
else
    error "$(basename "$COMMAND_FILE") not found"
fi

# Check 2: File is readable
if [[ -r "$COMMAND_FILE" ]]; then
    info "$(basename "$COMMAND_FILE") is readable"
else
    error "$(basename "$COMMAND_FILE") is not readable"
fi

# Check 3: File is not empty
if [[ -s "$COMMAND_FILE" ]]; then
    info "$(basename "$COMMAND_FILE") is not empty"
else
    error "$(basename "$COMMAND_FILE") is empty"
fi

# Extract body (after frontmatter) once for all content checks
BODY=""
if [[ -f "$COMMAND_FILE" ]] && [[ -s "$COMMAND_FILE" ]]; then
    FIRST_LINE=$(head -1 "$COMMAND_FILE")
    if [[ "$FIRST_LINE" == "---" ]]; then
        # Find the closing --- (second occurrence), then take everything after it
        CLOSING_LINE=$(awk 'NR>1 && /^---$/ { print NR; exit }' "$COMMAND_FILE")
        if [[ -n "$CLOSING_LINE" ]]; then
            BODY=$(tail -n +"$((CLOSING_LINE + 1))" "$COMMAND_FILE")
        else
            BODY=$(cat "$COMMAND_FILE")
        fi
    else
        BODY=$(cat "$COMMAND_FILE")
    fi
fi

# Check 4: Scan for placeholder content in command body
if [[ -n "$BODY" ]]; then
    echo ""
    echo "Checking for placeholder content..."

    PLACEHOLDER_PATTERNS='(TODO|TBD|FIXME|HACK|XXX|PLACEHOLDER|COMING SOON|NOT YET|IMPLEMENT ME)'

    if echo "$BODY" | grep -qwiE "$PLACEHOLDER_PATTERNS"; then
        MATCH=$(echo "$BODY" | grep -wiE "$PLACEHOLDER_PATTERNS" | head -1 | sed 's/^[[:space:]]*//')
        error "Placeholder content found: $MATCH"
    else
        info "No placeholder content detected"
    fi
fi

# Check 5: H1 heading required in command body
if [[ -n "$BODY" ]]; then
    echo ""
    echo "Checking for H1 heading..."

    if echo "$BODY" | grep -qE '^# '; then
        H1_LINE=$(echo "$BODY" | grep -E '^# ' | head -1)
        info "H1 heading found: $H1_LINE"
    else
        error "Missing H1 heading — every command must start with '# Title'"
    fi
fi

# Check 6: Warn if command lacks verification section (renumbered)
if [[ -f "$COMMAND_FILE" ]] && [[ -s "$COMMAND_FILE" ]]; then
    if grep -qiE '^#{1,3}\s*(verification|verify|test|check)' "$COMMAND_FILE"; then
        info "Verification section found"
    else
        warn "No verification section — commands should include how to verify results"
    fi
fi

# Check 6: Warn if parameterized command lacks fallback for missing arguments
if [[ -f "$COMMAND_FILE" ]] && [[ -s "$COMMAND_FILE" ]]; then
    if grep -qE '\$1|\$2|\$ARGUMENTS' "$COMMAND_FILE"; then
        if grep -qiE '^#{1,3}\s*(default behavior|fallback|missing argument)' "$COMMAND_FILE"; then
            info "Parameterized command has fallback section"
        else
            warn "Uses \$1/\$2 but no 'Default Behavior' section for missing arguments"
        fi
    fi
fi

# Check 8: Warn if command contains vague instructions without specifics
if [[ -n "$BODY" ]]; then
    echo ""
    echo "Checking for vague instructions..."

    # Patterns like "improve the code" or "fix issues" without specific targets
    VAGUE_PATTERNS='(^|\s)(improve|fix|update|enhance|optimize|refactor|clean up|make better)\s+(the\s+)?(code|it|things|stuff|everything|issues|problems)'

    VAGUE_MATCH=$(echo "$BODY" | grep -iE "$VAGUE_PATTERNS" | head -1 | sed 's/^[[:space:]]*//' || true)
    if [[ -n "$VAGUE_MATCH" ]]; then
        warn "Vague instruction detected: '$VAGUE_MATCH' — be specific about what to change and how"
    else
        info "No vague instructions detected"
    fi
fi

# Check 9: Warn if command lacks concrete references (file paths, code, tool names)
if [[ -n "$BODY" ]]; then
    echo ""
    echo "Checking prompt specificity..."

    # Look for concrete references: file paths, backtick code, tool names, variables
    HAS_CONCRETE=false
    if echo "$BODY" | grep -qE '`[^`]+`'; then HAS_CONCRETE=true; fi
    if echo "$BODY" | grep -qE '\$1|\$2|\$ARGUMENTS'; then HAS_CONCRETE=true; fi
    if echo "$BODY" | grep -qE '\.(py|ts|js|md|sh|json|yaml|yml|toml)'; then HAS_CONCRETE=true; fi
    if echo "$BODY" | grep -qwE '(Read|Write|Edit|Bash|Glob|Grep|Task|AskUserQuestion)'; then HAS_CONCRETE=true; fi

    if $HAS_CONCRETE; then
        info "Concrete references found (file paths, code, or tool names)"
    else
        warn "No concrete references found — commands should reference specific files, tools, or code patterns"
    fi
fi

# Check 10: If directory mode (self-validation), check SKILL.md has frontmatter
if $IS_DIR; then
    if head -1 "$COMMAND_FILE" 2>/dev/null | grep -q '^---$'; then
        info "SKILL.md has frontmatter"
    else
        error "SKILL.md missing frontmatter (must start with ---)"
    fi

    # Check directory structure
    echo ""
    echo "Checking directory structure..."

    # Check references directory
    REFS_DIR="$TARGET/references"
    if [[ -d "$REFS_DIR" ]]; then
        info "references/ directory exists"
        MD_COUNT=$(find "$REFS_DIR" -name "*.md" | wc -l)
        if [[ $MD_COUNT -gt 0 ]]; then
            info "Found $MD_COUNT reference files"
        else
            warn "references/ directory is empty"
        fi
    else
        if $VERBOSE; then
            info "No references/ directory (optional)"
        fi
    fi

    # Check scripts directory
    SCRIPTS_DIR="$TARGET/scripts"
    if [[ -d "$SCRIPTS_DIR" ]]; then
        info "scripts/ directory exists"
        SCRIPT_COUNT=$(find "$SCRIPTS_DIR" \( -name "*.sh" -o -name "*.py" \) | wc -l)
        if [[ $SCRIPT_COUNT -gt 0 ]]; then
            info "Found $SCRIPT_COUNT scripts"
        fi

        echo ""
        echo "Checking script permissions..."
        for script in "$SCRIPTS_DIR"/*.sh; do
            [[ -e "$script" ]] || continue
            if [[ -x "$script" ]]; then
                info "$(basename "$script") is executable"
            else
                error "$(basename "$script") is not executable"
            fi
        done
    fi

    # Check for hidden files (except .gitkeep)
    echo ""
    echo "Checking for hidden files..."
    HIDDEN_FILES=$(find "$TARGET" -name ".*" ! -name ".gitkeep" ! -name ".gitignore" ! -name ".github" -type f 2>/dev/null)
    if [[ -n "$HIDDEN_FILES" ]]; then
        warn "Found hidden files:"
        echo "$HIDDEN_FILES" | while read -r f; do
            echo "  - $f"
        done
    else
        info "No unexpected hidden files"
    fi

    # Check for large files
    echo ""
    echo "Checking file sizes..."
    LARGE_FILES=$(find "$TARGET" -type f -size +100k 2>/dev/null)
    if [[ -n "$LARGE_FILES" ]]; then
        warn "Found files > 100KB:"
        echo "$LARGE_FILES" | while read -r f; do
            SIZE=$(du -h "$f" | cut -f1)
            echo "  - $(basename "$f"): $SIZE"
        done
    else
        info "All files under 100KB"
    fi
else
    # File mode: check command .md file is valid markdown
    if [[ "$COMMAND_FILE" == *.md ]]; then
        info "File has .md extension"
    else
        warn "File does not have .md extension"
    fi
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Structure Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ PASSED${NC} - $ERRORS errors, $WARNINGS warnings"
    exit 0
else
    echo -e "${RED}✗ FAILED${NC} - $ERRORS errors, $WARNINGS warnings"
    exit 1
fi
