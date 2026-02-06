#!/usr/bin/env bash
# validate-all.sh - Run all command validators
#
# Usage: validate-all.sh <command-file-or-directory> [--verbose] [--json]
#
# Runs:
# - validate-structure.sh
# - validate-frontmatter.sh
# - count-tokens.py
# - security-check.sh
# - check-duplicates.py

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Results tracking
declare -A RESULTS
TOTAL_ERRORS=0

usage() {
    echo "Usage: $0 <command-file-or-directory> [--verbose] [--json]"
    echo ""
    echo "Run all validators on a command file or directory."
    echo ""
    echo "Options:"
    echo "  -v, --verbose  Show detailed output from each validator"
    echo "  --json         Output results as JSON"
    echo "  -h, --help     Show this help message"
    exit 1
}

# Parse arguments
VERBOSE=false
JSON_OUTPUT=false
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
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            TARGET="$1"
            shift
            ;;
    esac
done

if [[ -z "$TARGET" ]]; then
    echo -e "${RED}Error:${NC} Command file or directory required" >&2
    usage
fi

# Resolve path
if [[ -d "$TARGET" ]]; then
    TARGET=$(cd "$TARGET" 2>/dev/null && pwd) || {
        echo -e "${RED}Error:${NC} Directory does not exist: $TARGET" >&2
        exit 1
    }
    DISPLAY_NAME=$(basename "$TARGET")
elif [[ -f "$TARGET" ]]; then
    TARGET=$(realpath "$TARGET" 2>/dev/null || echo "$TARGET")
    DISPLAY_NAME=$(basename "$TARGET")
else
    echo -e "${RED}Error:${NC} Path does not exist: $TARGET" >&2
    exit 1
fi

run_validator() {
    local name="$1"
    shift

    if ! $JSON_OUTPUT; then
        echo -e "\n${BLUE}[$name]${NC}"
    fi

    if $VERBOSE; then
        if "$@"; then
            RESULTS[$name]="PASS"
            return 0
        else
            RESULTS[$name]="FAIL"
            ((TOTAL_ERRORS++)) || true
            return 1
        fi
    else
        local output
        if output=$("$@" 2>&1); then
            RESULTS[$name]="PASS"
            if ! $JSON_OUTPUT; then
                echo -e "${GREEN}✓ PASSED${NC}"
            fi
            return 0
        else
            RESULTS[$name]="FAIL"
            ((TOTAL_ERRORS++)) || true
            if ! $JSON_OUTPUT; then
                echo -e "${RED}✗ FAILED${NC}"
                echo "$output" | tail -5 | sed 's/^/  /'
            fi
            return 1
        fi
    fi
}

if ! $JSON_OUTPUT; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Validating: $DISPLAY_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

OVERALL_PASS=true

# 1. Structure validation
if [[ -x "$SCRIPT_DIR/validate-structure.sh" ]]; then
    run_validator "Structure" "$SCRIPT_DIR/validate-structure.sh" "$TARGET" || OVERALL_PASS=false
else
    if ! $JSON_OUTPUT; then
        echo -e "\n${YELLOW}[Structure]${NC} Skipped - validator not found"
    fi
    RESULTS["Structure"]="SKIP"
fi

# 2. Frontmatter validation
if [[ -x "$SCRIPT_DIR/validate-frontmatter.sh" ]]; then
    run_validator "Frontmatter" "$SCRIPT_DIR/validate-frontmatter.sh" "$TARGET" || OVERALL_PASS=false
else
    if ! $JSON_OUTPUT; then
        echo -e "\n${YELLOW}[Frontmatter]${NC} Skipped - validator not found"
    fi
    RESULTS["Frontmatter"]="SKIP"
fi

# 3. Token count validation
if [[ -x "$SCRIPT_DIR/count-tokens.py" ]]; then
    run_validator "Tokens" python3 "$SCRIPT_DIR/count-tokens.py" "$TARGET" || OVERALL_PASS=false
elif command -v python3 &>/dev/null && [[ -f "$SCRIPT_DIR/count-tokens.py" ]]; then
    run_validator "Tokens" python3 "$SCRIPT_DIR/count-tokens.py" "$TARGET" || OVERALL_PASS=false
else
    if ! $JSON_OUTPUT; then
        echo -e "\n${YELLOW}[Tokens]${NC} Skipped - Python not available"
    fi
    RESULTS["Tokens"]="SKIP"
fi

# 4. Security check
if [[ -x "$SCRIPT_DIR/security-check.sh" ]]; then
    run_validator "Security" "$SCRIPT_DIR/security-check.sh" "$TARGET" || OVERALL_PASS=false
else
    if ! $JSON_OUTPUT; then
        echo -e "\n${YELLOW}[Security]${NC} Skipped - validator not found"
    fi
    RESULTS["Security"]="SKIP"
fi

# 5. Script validation (shellcheck + python syntax, directory mode only)
if [[ -d "$TARGET" ]]; then
    SCRIPTS_DIR="$TARGET/scripts"
    if [[ -d "$SCRIPTS_DIR" ]]; then
        run_shellcheck_stdin() {
            local rc=0
            while IFS= read -r -d '' script; do
                if ! shellcheck -S warning -s bash - < "$script" 2>&1; then
                    rc=1
                fi
            done < <(find "$1" -name "*.sh" -type f -print0 2>/dev/null)
            return $rc
        }

        if command -v shellcheck &>/dev/null; then
            SHELL_SCRIPT_COUNT=$(find "$SCRIPTS_DIR" -name "*.sh" -type f 2>/dev/null | wc -l)
            if [[ "$SHELL_SCRIPT_COUNT" -gt 0 ]]; then
                run_validator "Shellcheck" run_shellcheck_stdin "$SCRIPTS_DIR" || OVERALL_PASS=false
            fi
        fi

        py_syntax_check() {
            local rc=0
            while IFS= read -r -d '' pyfile; do
                if ! python3 -m py_compile "$pyfile" 2>&1; then
                    rc=1
                fi
            done < <(find "$1" -name "*.py" -type f -print0 2>/dev/null)
            return $rc
        }

        PY_COUNT=$(find "$SCRIPTS_DIR" -name "*.py" -type f 2>/dev/null | wc -l)
        if [[ "$PY_COUNT" -gt 0 ]]; then
            run_validator "Python Syntax" py_syntax_check "$SCRIPTS_DIR" || OVERALL_PASS=false
        fi
    fi
fi

# 6. Duplicate detection
if command -v python3 &>/dev/null && [[ -f "$SCRIPT_DIR/check-duplicates.py" ]]; then
    run_validator "Duplicates" python3 "$SCRIPT_DIR/check-duplicates.py" "$TARGET" || OVERALL_PASS=false
else
    if ! $JSON_OUTPUT; then
        echo -e "\n${YELLOW}[Duplicates]${NC} Skipped - Python not available"
    fi
    RESULTS["Duplicates"]="SKIP"
fi

# Output results
if $JSON_OUTPUT; then
    echo "{"
    echo "  \"name\": \"$DISPLAY_NAME\","
    echo "  \"passed\": $( $OVERALL_PASS && echo "true" || echo "false" ),"
    echo "  \"validators\": {"
    first=true
    for key in "${!RESULTS[@]}"; do
        $first || echo ","
        first=false
        echo -n "    \"$key\": \"${RESULTS[$key]}\""
    done
    echo ""
    echo "  },"
    echo "  \"total_errors\": $TOTAL_ERRORS"
    echo "}"
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Validation Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    for key in "${!RESULTS[@]}"; do
        case "${RESULTS[$key]}" in
            PASS)
                echo -e "  ${GREEN}✓${NC} $key"
                ;;
            FAIL)
                echo -e "  ${RED}✗${NC} $key"
                ;;
            SKIP)
                echo -e "  ${YELLOW}○${NC} $key (skipped)"
                ;;
        esac
    done

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if $OVERALL_PASS; then
        echo -e "${GREEN}✓ ALL VALIDATIONS PASSED${NC}"
        echo ""
        echo "'$DISPLAY_NAME' is ready for installation."
    else
        echo -e "${RED}✗ VALIDATION FAILED${NC}"
        echo ""
        echo "Fix the errors above before installation."
    fi
fi

$OVERALL_PASS && exit 0 || exit 1
