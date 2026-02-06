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

# Check 4: If directory mode (self-validation), check SKILL.md has frontmatter
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
