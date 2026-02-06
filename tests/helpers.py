"""Helper functions for creating test command files.

This module provides utility functions to create test command files
with various configurations for testing the validation scripts.

All operations use REAL file system - NO mocks or simulations.
"""

from __future__ import annotations

from pathlib import Path


def create_command_md(
    target_dir: Path,
    name: str,
    *,
    description: str | None = None,
    tools: list[str] | None = None,
    model: str | None = None,
    argument_hint: str | None = None,
    disable_model_invocation: bool | None = None,
    content: str = "# Command\n\nInstructions here.\n",
    include_frontmatter: bool = True,
) -> Path:
    """Create a command .md file with optional frontmatter.

    Args:
        target_dir: Directory to create the command file in
        name: Command name (used as filename without .md)
        description: Optional command description
        tools: Optional list of allowed tools
        model: Optional model specification
        argument_hint: Optional argument hint
        disable_model_invocation: Optional boolean
        content: Markdown content after frontmatter
        include_frontmatter: Whether to include frontmatter

    Returns:
        Path to the created command file
    """
    lines: list[str] = []

    if include_frontmatter:
        # Build frontmatter only if there are fields to include
        has_fields = any([
            description, tools, model, argument_hint,
            disable_model_invocation is not None,
        ])

        if has_fields:
            lines.append("---")

            if description is not None:
                lines.append(f"description: {description}")

            if tools:
                lines.append("allowed-tools:")
                for tool in tools:
                    lines.append(f"  - {tool}")

            if model:
                lines.append(f"model: {model}")

            if argument_hint:
                lines.append(f"argument-hint: \"{argument_hint}\"")

            if disable_model_invocation is not None:
                lines.append(
                    f"disable-model-invocation: {str(disable_model_invocation).lower()}"
                )

            lines.append("---")
            lines.append("")

    lines.append(content)

    command_md = target_dir / f"{name}.md"
    command_md.write_text("\n".join(lines))

    return command_md


def create_skill_md(
    skill_dir: Path,
    name: str,
    description: str,
    *,
    tools: list[str] | None = None,
    model: str | None = None,
    content: str = "# Skill\n\nInstructions here.\n",
) -> Path:
    """Create a SKILL.md file with frontmatter (for self-validation tests).

    Args:
        skill_dir: Directory to create SKILL.md in
        name: Skill name for frontmatter
        description: Skill description for frontmatter
        tools: Optional list of allowed tools
        model: Optional model specification
        content: Markdown content after frontmatter

    Returns:
        Path to the created SKILL.md file
    """
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
    ]

    if tools:
        lines.append("allowed-tools:")
        for tool in tools:
            lines.append(f"  - {tool}")

    if model:
        lines.append(f"model: {model}")

    lines.append("---")
    lines.append("")
    lines.append(content)

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("\n".join(lines))

    return skill_md


def generate_long_text(tokens: int, method: str = "words") -> str:
    """Generate text of approximately the specified token count.

    Args:
        tokens: Target token count
        method: Generation method ("words" or "lorem")

    Returns:
        Generated text string with approximately the specified token count.
    """
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
    except ImportError:
        words_needed = tokens
        base_words = [
            "the", "command", "provides", "functionality", "for",
            "testing", "validation", "code", "development", "automation",
            "system", "process", "data", "output", "input",
            "configuration", "setup",
        ]
        words = []
        for i in range(words_needed):
            words.append(base_words[i % len(base_words)])
        return " ".join(words)

    if method == "lorem":
        base_phrase = (
            "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do "
            "eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        )
    else:
        base_phrase = (
            "The command provides functionality for testing validation code "
            "development automation system process data output input "
            "configuration setup implementation verification analysis "
            "generation transformation processing handling management. "
        )

    text = ""
    while True:
        current_tokens = len(encoding.encode(text))
        if current_tokens >= tokens:
            break
        text += base_phrase

    encoded = encoding.encode(text)
    if len(encoded) > tokens:
        encoded = encoded[:tokens]
        text = encoding.decode(encoded)

    return text


def generate_long_lines(line_count: int, chars_per_line: int = 80) -> str:
    """Generate text with the specified number of lines.

    Args:
        line_count: Number of lines to generate
        chars_per_line: Approximate characters per line

    Returns:
        Generated multi-line text
    """
    lines = []
    for i in range(line_count):
        line = f"Line {i + 1}: " + "x" * (chars_per_line - 10)
        lines.append(line)
    return "\n".join(lines)
