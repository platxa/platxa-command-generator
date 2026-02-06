#!/usr/bin/env bash
# validate-frontmatter.sh - Validate command frontmatter
#
# Usage: validate-frontmatter.sh <command-file-or-directory>
#
# For commands, ALL frontmatter fields are OPTIONAL.
# If frontmatter exists, validates field values.
# Commands without frontmatter (basic type) pass validation.

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
    echo "Validates command frontmatter against spec."
    echo "All frontmatter fields are optional for commands."
    exit 1
}

# Parse arguments
TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
    error "Command file or directory required"
    usage
fi

# Determine the file to validate
if [[ -d "$TARGET" ]]; then
    # Directory mode: check for SKILL.md (self-validation)
    COMMAND_FILE="$TARGET/SKILL.md"
    IS_SKILL=true
else
    COMMAND_FILE="$TARGET"
    IS_SKILL=false
fi

if [[ ! -f "$COMMAND_FILE" ]]; then
    error "File not found: $COMMAND_FILE"
    exit 1
fi

echo "Validating frontmatter: $(basename "$COMMAND_FILE")"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if file starts with ---
read -r FIRST_LINE < "$COMMAND_FILE"
if [[ "$FIRST_LINE" != "---" ]]; then
    if $IS_SKILL; then
        # SKILL.md requires frontmatter
        error "File must start with --- (frontmatter delimiter)"
        exit 1
    else
        # Commands without frontmatter are valid (basic type)
        info "No frontmatter (basic command type) - valid"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${GREEN}✓ PASSED${NC} - 0 errors, 0 warnings"
        exit 0
    fi
fi

# Extract frontmatter content (between first and second ---)
FRONTMATTER=$(sed -n '2,/^---$/p' "$COMMAND_FILE" | sed '$d')

if [[ -z "$FRONTMATTER" ]]; then
    error "Empty frontmatter"
    exit 1
fi

info "Frontmatter found"

# Parse frontmatter with Python yaml.safe_load
PARSED=$(python3 -c "
import yaml, sys
try:
    data = yaml.safe_load(sys.stdin)
    if not isinstance(data, dict):
        print('__YAML_ERROR__')
        sys.exit(0)
    # Extract fields - all optional for commands
    name = str(data.get('name', '') or '')
    desc = str(data.get('description', '') or '')
    # Accept both 'tools' and 'allowed-tools'
    tools_key = ''
    tools_list = []
    if 'allowed-tools' in data:
        tools_key = 'allowed-tools'
        tools_list = data['allowed-tools'] or []
    elif 'tools' in data:
        tools_key = 'tools'
        tools_list = data['tools'] or []
    tools_csv = ','.join(str(t) for t in tools_list) if tools_list else ''
    model = str(data.get('model', '') or '')
    arg_hint = str(data.get('argument-hint', '') or '')
    disable_model = str(data.get('disable-model-invocation', '') or '')
    fields = '|'.join(str(k) for k in data.keys())
    for val in [name, desc, tools_key, tools_csv, model, arg_hint, disable_model, fields]:
        print(val)
except yaml.YAMLError:
    print('__YAML_ERROR__')
" <<< "$FRONTMATTER")

if [[ "$PARSED" == "__YAML_ERROR__" ]]; then
    error "Invalid YAML syntax"
    exit 1
fi

info "Valid YAML syntax"

# Read fields line-by-line
mapfile -t PARSED_LINES <<< "$PARSED"
NAME="${PARSED_LINES[0]}"
DESC="${PARSED_LINES[1]}"
TOOLS_KEY="${PARSED_LINES[2]}"
TOOLS_CSV="${PARSED_LINES[3]}"
MODEL="${PARSED_LINES[4]}"
ARG_HINT="${PARSED_LINES[5]}"
DISABLE_MODEL="${PARSED_LINES[6]}"
FIELD_NAMES="${PARSED_LINES[7]}"

# If this is a SKILL.md (self-validation), require name and description
if $IS_SKILL; then
    echo ""
    echo "Checking required SKILL.md fields..."

    if [[ -z "$NAME" ]]; then
        error "Missing required field: name"
    else
        info "name field present: $NAME"

        # Check name format (hyphen-case)
        if [[ ! "$NAME" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
            error "name must be hyphen-case (lowercase letters, numbers, hyphens)"
        else
            info "name format valid (hyphen-case)"
        fi

        # Check name length
        NAME_LEN=${#NAME}
        if [[ $NAME_LEN -gt 64 ]]; then
            error "name too long: $NAME_LEN chars (max 64)"
        elif [[ $NAME_LEN -lt 2 ]]; then
            error "name too short: $NAME_LEN chars (min 2)"
        else
            info "name length valid: $NAME_LEN chars"
        fi

        # Check for double hyphens
        if [[ "$NAME" == *"--"* ]]; then
            error "name cannot contain consecutive hyphens"
        fi
    fi

    if [[ -z "$DESC" ]]; then
        error "Missing required field: description"
    else
        info "description field present"

        DESC_LEN=${#DESC}
        if [[ $DESC_LEN -gt 1024 ]]; then
            error "description too long: $DESC_LEN chars (max 1024)"
        elif [[ $DESC_LEN -lt 10 ]]; then
            warn "description very short: $DESC_LEN chars"
        else
            info "description length valid: $DESC_LEN chars"
        fi

        if echo "$DESC" | grep -qiE '(TODO|TBD|FIXME|placeholder)'; then
            error "description contains placeholder text"
        fi
    fi
fi

echo ""
echo "Checking optional fields..."

# Validate description if present (command-level: <= 60 chars, starts with verb)
if [[ -n "$DESC" ]] && ! $IS_SKILL; then
    DESC_LEN=${#DESC}
    if [[ $DESC_LEN -gt 60 ]]; then
        error "description exceeds 60 chars: $DESC_LEN chars (max 60)"
    else
        info "description length valid: $DESC_LEN chars"
    fi

    if echo "$DESC" | grep -qiE '(TODO|TBD|FIXME|placeholder)'; then
        error "description contains placeholder text"
    fi

    # Check that description starts with lowercase letter
    FIRST_CHAR="${DESC:0:1}"
    if [[ "$FIRST_CHAR" =~ [A-Z] ]]; then
        warn "description should start with lowercase verb (e.g., 'analyze ...', not 'Analyze ...')"
    elif [[ ! "$FIRST_CHAR" =~ [a-z] ]]; then
        warn "description should start with a verb (first character is not a letter)"
    else
        info "description starts with lowercase"
    fi

    # Check for common non-verb starting patterns
    FIRST_WORD=$(echo "$DESC" | awk '{print $1}')
    NON_VERB_PATTERNS="the a an this that these those my our your its"
    for pattern in $NON_VERB_PATTERNS; do
        if [[ "${FIRST_WORD,,}" == "$pattern" ]]; then
            warn "description should start with a verb, not '$FIRST_WORD' (e.g., 'analyze ...', 'generate ...')"
            break
        fi
    done
fi

# Validate argument-hint if present
if [[ -n "$ARG_HINT" ]]; then
    info "argument-hint present: $ARG_HINT"

    # Must use bracket format: [arg] or <arg>
    if [[ ! "$ARG_HINT" =~ [\[\<] ]]; then
        error "argument-hint should use bracket format: [arg] or <arg>"
    else
        info "argument-hint format valid"
    fi
fi

# Validate allowed-tools if present
if [[ -n "$TOOLS_KEY" ]]; then
    if [[ -n "$TOOLS_CSV" ]]; then
        IFS=',' read -ra TOOL_ARRAY <<< "$TOOLS_CSV"
        TOOL_COUNT=${#TOOL_ARRAY[@]}
        info "tools field present with $TOOL_COUNT tools"

        # Valid base tool names
        VALID_TOOLS="Read Write Edit MultiEdit Glob Grep LS Bash Task WebFetch WebSearch AskUserQuestion TodoWrite KillShell BashOutput NotebookEdit"

        for TOOL in "${TOOL_ARRAY[@]}"; do
            [[ -z "$TOOL" ]] && continue
            # Extract base tool name (handle Bash filter syntax like "Bash(git:*)")
            BASE_TOOL=$(echo "$TOOL" | sed 's/(.*//')
            if ! echo "$VALID_TOOLS" | grep -qw "$BASE_TOOL"; then
                error "Invalid tool: $TOOL"
            fi

            # Validate Bash filter syntax if present
            if [[ "$TOOL" == *"("* ]]; then
                if [[ "$BASE_TOOL" != "Bash" ]]; then
                    error "Filter syntax only supported for Bash, not: $TOOL"
                elif [[ ! "$TOOL" =~ ^Bash\([a-zA-Z0-9_\ -]+:[^\)]+\)$ ]]; then
                    error "Invalid Bash filter syntax: $TOOL (expected Bash(command:pattern))"
                else
                    info "Bash filter syntax valid: $TOOL"
                fi
            fi
        done
    else
        info "tools field present but empty"
    fi
else
    info "No tools field (optional)"
fi

# Validate model if present
if [[ -n "$MODEL" ]]; then
    if [[ "$MODEL" =~ ^(opus|sonnet|haiku)$ ]]; then
        info "model field valid: $MODEL"
    else
        error "Invalid model: $MODEL (must be opus, sonnet, or haiku)"
    fi
fi

# Validate disable-model-invocation if present
if [[ -n "$DISABLE_MODEL" ]]; then
    if [[ "$DISABLE_MODEL" =~ ^(true|false|True|False)$ ]]; then
        info "disable-model-invocation valid: $DISABLE_MODEL"
    else
        error "Invalid disable-model-invocation: $DISABLE_MODEL (must be true or false)"
    fi
fi

# Check for unknown fields
echo ""
echo "Checking for unknown fields..."

KNOWN_FIELDS="name description tools allowed-tools model argument-hint disable-model-invocation subagent_type run_in_background license metadata"

IFS='|' read -ra FIELD_ARRAY <<< "$FIELD_NAMES"
for field in "${FIELD_ARRAY[@]}"; do
    [[ -z "$field" ]] && continue
    if ! echo "$KNOWN_FIELDS" | grep -qw "$field"; then
        warn "Unknown field will be ignored: $field"
    fi
done

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Frontmatter Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ PASSED${NC} - $ERRORS errors, $WARNINGS warnings"
    exit 0
else
    echo -e "${RED}✗ FAILED${NC} - $ERRORS errors, $WARNINGS warnings"
    exit 1
fi
