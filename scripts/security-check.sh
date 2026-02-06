#!/usr/bin/env bash
# security-check.sh - Scan command content for security issues
#
# Usage: security-check.sh <command-file-or-directory>
#
# Scans markdown files for dangerous patterns that could be executed
# by the AI agent, including credential leaks, destructive commands,
# and data exfiltration patterns.

set -euo pipefail

# Colors & counters
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

error() {
    echo -e "${RED}SECURITY:${NC} $1" >&2
    ((ERRORS++)) || true
}

warn() {
    echo -e "${YELLOW}WARN:${NC} $1" >&2
    ((WARNINGS++)) || true
}

usage() {
    echo "Usage: $0 <command-file-or-directory>"
    echo ""
    echo "Scan command content for security issues."
    exit 1
}

# Argument parsing
TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
    echo -e "${RED}Error:${NC} Command file or directory required" >&2
    usage
fi

# Determine scan mode
if [[ -d "$TARGET" ]]; then
    SCAN_NAME=$(basename "$TARGET")
    IS_DIR=true
else
    SCAN_NAME=$(basename "$TARGET")
    IS_DIR=false
fi

SELF_PATH=$(realpath "${BASH_SOURCE[0]}" 2>/dev/null || echo "")

echo "Security Check: $SCAN_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Pattern definitions

CREDENTIAL_PATTERNS=(
    'password\s*='
    'passwd\s*='
    'api_key\s*='
    'apikey\s*='
    'secret\s*='
    'token\s*='
    'AWS_ACCESS_KEY'
    'AWS_SECRET'
    'GITHUB_TOKEN'
    'ANTHROPIC_API_KEY'
    'OPENAI_API_KEY'
)

MARKDOWN_DANGEROUS=(
    'curl.*\| *sh'
    'curl.*\| *bash'
    'wget.*\| *sh'
    'wget.*\| *bash'
    'eval\s*"?\$\('
    'rm -rf /'
    'rm -rf /\*'
    ':(){:|:&};:'
    'mkfs\.'
    'dd if=/dev/'
    '> /dev/sd'
    'chmod -R 777 /'
    'base64\s+-d.*\|\s*bash'
    'base64\s+--decode.*\|\s*bash'
    'python[23]?\s+-c.*__import__'
    'nc\s+-[el]'
    'bash\s+-i\s+>&\s*/dev/tcp'
    '/dev/tcp/'
    'nohup.*&'
)

EXFIL_PATTERNS=(
    'curl.*-d\s*@'
    'curl.*--data.*@'
    'curl.*--upload-file'
    'wget.*--post-file'
    'cat.*/etc/(passwd|shadow|hosts)'
    '\$\(cat\s+/etc/'
    '\$\(cat\s+(~|\$HOME)/\.'
    'base64.*</etc/'
)

# Phase 1: Scan markdown files
echo ""
echo "Phase 1: Scanning markdown files for malicious patterns..."
echo ""

scan_markdown_file() {
    local mdfile="$1"
    local md_rel="$2"
    local content
    content=$(<"$mdfile")

    # Skip files with nosec directive
    if echo "$content" | grep -q '<!-- nosec -->'; then
        echo "Skipping: $md_rel (nosec directive)"
        return
    fi

    for pattern in "${MARKDOWN_DANGEROUS[@]}"; do
        if echo "$content" | grep -qE "$pattern"; then
            error "$md_rel: Dangerous agent instruction: $pattern"
        fi
    done

    for pattern in "${EXFIL_PATTERNS[@]}"; do
        if echo "$content" | grep -qE "$pattern"; then
            error "$md_rel: Possible data exfiltration pattern: $pattern"
        fi
    done

    for pattern in "${CREDENTIAL_PATTERNS[@]}"; do
        if echo "$content" | grep -qiE "$pattern"; then
            match_line=$(echo "$content" | grep -iE "$pattern" | head -1)
            if [[ ! "$match_line" =~ \<.*\> ]] && \
               [[ ! "$match_line" =~ \{.*\} ]] && \
               [[ ! "$match_line" =~ your_ ]] && \
               [[ ! "$match_line" =~ YOUR_ ]] && \
               [[ ! "$match_line" =~ os\.environ ]] && \
               [[ ! "$match_line" =~ \$\{ ]] && \
               [[ ! "$match_line" =~ getenv ]]; then
                warn "$md_rel: Possible hardcoded credential: $pattern"
            fi
        fi
    done
}

if $IS_DIR; then
    while IFS= read -r -d '' mdfile; do
        md_rel="${mdfile#"$TARGET"/}"
        scan_markdown_file "$mdfile" "$md_rel"
    done < <(find "$TARGET" -name "*.md" -type f -print0 2>/dev/null)

    # Phase 2: Scan scripts if directory mode
    SCRIPTS_DIR="$TARGET/scripts"
    if [[ -d "$SCRIPTS_DIR" ]]; then
        SCRIPT_COUNT=$(find "$SCRIPTS_DIR" \( -name "*.sh" -o -name "*.py" \) -type f 2>/dev/null | wc -l)
        if [[ "$SCRIPT_COUNT" -gt 0 ]]; then
            echo ""
            echo "Phase 2: Scanning $SCRIPT_COUNT script(s)..."
            echo ""

            BASH_DANGEROUS=(
                'rm -rf /'
                'rm -rf /\*'
                'rm -rf ~'
                'rm -rf $HOME'
                ':(){:|:&};:'
                'mkfs\.'
                'dd if=/dev/zero'
                'dd if=/dev/random'
                '> /dev/sda'
                'chmod -R 777 /'
                'chmod 777 /'
                'wget.*\| *sh'
                'curl.*\| *sh'
                'curl.*\| *bash'
                'wget.*\| *bash'
                '\$\(.*\)\s*>\s*/etc/'
                'eval "\$\('
                'sudo\s+rm'
                'sudo\s+chmod'
            )

            PYTHON_DANGEROUS=(
                'os\.system\('
                'subprocess\.call\(.*shell=True'
                'subprocess\.Popen\(.*shell=True'
                'eval\('
                'exec\('
                '__import__\('
                'pickle\.loads?\('
                'yaml\.load\([^,]*\)'
                'os\.remove\(.*/'
                'shutil\.rmtree\(.*/'
                'open\(.*/etc/'
            )

            while IFS= read -r -d '' script; do
                script_name=$(basename "$script")

                # Skip self
                if [[ -n "$SELF_PATH" ]] && [[ "$(realpath "$script" 2>/dev/null)" == "$SELF_PATH" ]]; then
                    echo "Skipping: $script_name (security scanner)"
                    continue
                fi

                echo "Checking: $script_name"
                content=$(<"$script")

                if echo "$content" | grep -q '# nosec'; then
                    echo "Skipping: $script_name (nosec directive)"
                    continue
                fi

                if [[ "$script" == *.sh ]]; then
                    for pattern in "${BASH_DANGEROUS[@]}"; do
                        if echo "$content" | grep -qE "$pattern"; then
                            error "$script_name: Dangerous pattern found: $pattern"
                        fi
                    done
                fi

                if [[ "$script" == *.py ]]; then
                    for pattern in "${PYTHON_DANGEROUS[@]}"; do
                        if echo "$content" | grep -qE "$pattern"; then
                            match_line=$(echo "$content" | grep -E "$pattern" | head -1)
                            if [[ ! "$match_line" =~ ^[[:space:]]*# ]]; then
                                error "$script_name: Dangerous pattern found: $pattern"
                            fi
                        fi
                    done
                fi

                for pattern in "${CREDENTIAL_PATTERNS[@]}"; do
                    if echo "$content" | grep -qiE "$pattern"; then
                        match_line=$(echo "$content" | grep -iE "$pattern" | head -1)
                        if [[ ! "$match_line" =~ os\.environ ]] && \
                           [[ ! "$match_line" =~ \$\{ ]] && \
                           [[ ! "$match_line" =~ getenv ]]; then
                            warn "$script_name: Possible hardcoded credential: $pattern"
                        fi
                    fi
                done

            done < <(find "$SCRIPTS_DIR" \( -name "*.sh" -o -name "*.py" \) -type f -print0 2>/dev/null)
        fi
    fi
else
    # Single file mode
    scan_markdown_file "$TARGET" "$SCAN_NAME"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Security Check Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}✓ PASSED${NC} - No security issues found"
    exit 0
elif [[ $ERRORS -eq 0 ]]; then
    echo -e "${YELLOW}⚠ PASSED WITH WARNINGS${NC} - $WARNINGS warning(s)"
    echo "Review warnings before deployment."
    exit 0
else
    echo -e "${RED}✗ FAILED${NC} - $ERRORS security issue(s), $WARNINGS warning(s)"
    echo "Fix security issues before installation."
    exit 1
fi
