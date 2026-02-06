#!/usr/bin/env bash
# Install a Claude Code command to user, project, or plugin location
# Usage: install-command.sh <command-file-or-directory> [--user|--project|--plugin <namespace>]

set -euo pipefail

TARGET="${1:-.}"
LOCATION="${2:---user}"
NAMESPACE="${3:-}"

# Determine what we're installing
if [[ -d "$TARGET" ]]; then
    # Directory mode: installing the generator itself as a skill
    SKILL_MD="$TARGET/SKILL.md"
    if [[ ! -f "$SKILL_MD" ]]; then
        echo "ERROR: SKILL.md not found in $TARGET"
        exit 1
    fi

    # Extract name from frontmatter
    SKILL_NAME=$(sed -n '2,/^---$/p' "$SKILL_MD" | sed '$d' | grep "^name:" | head -1 | sed 's/name: *//' | tr -d '"' | tr -d "'")
    if [[ -z "$SKILL_NAME" ]]; then
        echo "ERROR: Could not extract skill name from SKILL.md"
        exit 1
    fi

    case "$LOCATION" in
        --user|-u)
            TARGET_DIR="$HOME/.claude/skills/$SKILL_NAME"
            LOCATION_NAME="user skills"
            ;;
        --project|-p)
            TARGET_DIR=".claude/skills/$SKILL_NAME"
            LOCATION_NAME="project skills"
            ;;
        *)
            echo "Usage: install-command.sh <directory> [--user|--project]"
            exit 1
            ;;
    esac

    echo "Installing skill: $SKILL_NAME"
    echo "Location: $LOCATION_NAME ($TARGET_DIR)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ -d "$TARGET_DIR" ]]; then
        echo "Skill already installed at $TARGET_DIR"
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 0
        fi
        rm -rf "$TARGET_DIR"
    fi

    mkdir -p "$TARGET_DIR"
    cp "$SKILL_MD" "$TARGET_DIR/"
    echo "Copied SKILL.md"

    for dir in references scripts assets; do
        if [[ -d "$TARGET/$dir" ]]; then
            cp -r "$TARGET/$dir" "$TARGET_DIR/"
            echo "Copied $dir/"
        fi
    done

    if [[ -d "$TARGET_DIR/scripts" ]]; then
        chmod +x "$TARGET_DIR/scripts"/*.sh 2>/dev/null || true
    fi

    echo ""
    echo "Skill installed successfully to $TARGET_DIR"
else
    # File mode: installing a single command .md file
    COMMAND_FILE="$TARGET"
    if [[ ! -f "$COMMAND_FILE" ]]; then
        echo "ERROR: File not found: $COMMAND_FILE"
        exit 1
    fi

    COMMAND_NAME=$(basename "$COMMAND_FILE" .md)

    case "$LOCATION" in
        --user|-u)
            TARGET_DIR="$HOME/.claude/commands"
            LOCATION_NAME="user"
            ;;
        --project|-p)
            TARGET_DIR=".claude/commands"
            LOCATION_NAME="project"
            ;;
        --plugin)
            if [[ -z "$NAMESPACE" ]]; then
                echo "ERROR: --plugin requires a namespace argument"
                echo "Usage: install-command.sh <file> --plugin <namespace>"
                exit 1
            fi
            TARGET_DIR=".claude/plugins/$NAMESPACE/commands"
            LOCATION_NAME="plugin ($NAMESPACE)"
            ;;
        *)
            echo "Usage: install-command.sh <command-file> [--user|--project|--plugin <namespace>]"
            echo "  --user, -u       Install to ~/.claude/commands/ (default)"
            echo "  --project, -p    Install to .claude/commands/"
            echo "  --plugin <ns>    Install to .claude/plugins/<ns>/commands/"
            exit 1
            ;;
    esac

    echo "Installing command: $COMMAND_NAME"
    echo "Location: $LOCATION_NAME ($TARGET_DIR)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    mkdir -p "$TARGET_DIR"

    TARGET_FILE="$TARGET_DIR/$COMMAND_NAME.md"
    if [[ -f "$TARGET_FILE" ]]; then
        echo "Command already installed at $TARGET_FILE"
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 0
        fi
    fi

    cp "$COMMAND_FILE" "$TARGET_FILE"

    echo ""
    echo "Command installed successfully!"
    echo "  File: $TARGET_FILE"
    echo "  Use: /$COMMAND_NAME"
fi
