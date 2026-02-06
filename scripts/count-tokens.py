#!/usr/bin/env python3
"""count-tokens.py - Count tokens in command files.

Usage: count-tokens.py <command-file-or-directory> [--json] [--warn-threshold N]

Provides accurate token counts using tiktoken (cl100k_base encoding)
with fallback to word-based estimation.

Budget limits for commands:
- Recommended: 2000 tokens, 300 lines
- Hard limit: 4000 tokens, 600 lines

When passed a directory (self-validation), uses skill-level limits.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TypedDict

# Try to import tiktoken for accurate counting
try:
    import tiktoken  # type: ignore[import-untyped]

    TIKTOKEN_AVAILABLE = True
except ImportError:
    tiktoken = None  # type: ignore[assignment]
    TIKTOKEN_AVAILABLE = False


class FileTokens(TypedDict):
    """Token count for a single file."""

    path: str
    tokens: int
    lines: int
    method: str


class TokenReport(TypedDict):
    """Complete token count report."""

    command_name: str
    command_tokens: int
    command_lines: int
    ref_total_tokens: int
    ref_files: list[FileTokens]
    total_tokens: int
    method: str
    warnings: list[str]
    passed: bool
    is_directory: bool


# Recommended budget limits for single command files
COMMAND_LIMITS = {
    "command_tokens": 2000,
    "command_lines": 300,
}

# Hard budget limits for single command files
COMMAND_HARD_LIMITS = {
    "command_tokens": 4000,
    "command_lines": 600,
}

# Skill-level limits (for self-validation of the generator directory)
SKILL_LIMITS = {
    "skill_md_tokens": 5000,
    "skill_md_lines": 500,
    "single_ref_tokens": 2000,
    "total_ref_tokens": 10000,
    "total_skill_tokens": 15000,
}

SKILL_HARD_LIMITS = {
    "skill_md_tokens": 10000,
    "skill_md_lines": 1000,
    "single_ref_tokens": 4000,
    "total_ref_tokens": 20000,
    "total_skill_tokens": 30000,
}


def count_tokens_tiktoken(text: str) -> int:
    """Count tokens using tiktoken (accurate)."""
    assert tiktoken is not None
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def count_tokens_estimate(text: str) -> int:
    """Estimate tokens from word count (fallback)."""
    words = len(text.split())
    return int(words * 1.3)


def count_tokens(text: str) -> tuple[int, str]:
    """Count tokens with best available method."""
    if TIKTOKEN_AVAILABLE:
        return count_tokens_tiktoken(text), "tiktoken"
    else:
        return count_tokens_estimate(text), "estimate"


def count_lines(text: str) -> int:
    """Count lines in text."""
    return len(text.split("\n"))


def analyze_command_file(command_path: Path, warn_threshold: int = 80) -> TokenReport:
    """Analyze token counts for a single command file."""
    warnings: list[str] = []
    command_name = command_path.stem

    if not command_path.exists():
        return TokenReport(
            command_name=command_name,
            command_tokens=0,
            command_lines=0,
            ref_total_tokens=0,
            ref_files=[],
            total_tokens=0,
            method="none",
            warnings=["Command file not found"],
            passed=False,
            is_directory=False,
        )

    content = command_path.read_text()
    tokens, method = count_tokens(content)
    lines = count_lines(content)

    limits = COMMAND_LIMITS
    hard = COMMAND_HARD_LIMITS

    # Check token limits
    if tokens > limits["command_tokens"]:
        warnings.append(
            f"Command exceeds recommended token limit: {tokens} > {limits['command_tokens']}"
        )
        warnings.append(
            "Consider converting to a skill — commands are re-processed every message, "
            "skills load on demand. See references/patterns/command-vs-skill-vs-hook.md"
        )
    elif tokens > limits["command_tokens"] * warn_threshold / 100:
        warnings.append(
            f"Command approaching token limit: {tokens} ({warn_threshold}% of {limits['command_tokens']})"
        )

    # Check line limits
    if lines > limits["command_lines"]:
        warnings.append(
            f"Command exceeds recommended line limit: {lines} > {limits['command_lines']}"
        )
    elif lines > limits["command_lines"] * warn_threshold / 100:
        warnings.append(
            f"Command approaching line limit: {lines} ({warn_threshold}% of {limits['command_lines']})"
        )

    passed = tokens <= hard["command_tokens"] and lines <= hard["command_lines"]

    return TokenReport(
        command_name=command_name,
        command_tokens=tokens,
        command_lines=lines,
        ref_total_tokens=0,
        ref_files=[],
        total_tokens=tokens,
        method=method,
        warnings=warnings,
        passed=passed,
        is_directory=False,
    )


def analyze_directory(skill_dir: Path, warn_threshold: int = 80) -> TokenReport:
    """Analyze token counts for a skill directory (self-validation)."""
    warnings: list[str] = []
    skill_name = skill_dir.name

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return TokenReport(
            command_name=skill_name,
            command_tokens=0,
            command_lines=0,
            ref_total_tokens=0,
            ref_files=[],
            total_tokens=0,
            method="none",
            warnings=["SKILL.md not found"],
            passed=False,
            is_directory=True,
        )

    content = skill_md.read_text()
    skill_tokens, method = count_tokens(content)
    skill_lines = count_lines(content)

    limits = SKILL_LIMITS
    hard = SKILL_HARD_LIMITS

    # Check SKILL.md limits
    if skill_tokens > limits["skill_md_tokens"]:
        warnings.append(
            f"SKILL.md exceeds token limit: {skill_tokens} > {limits['skill_md_tokens']}"
        )
    elif skill_tokens > limits["skill_md_tokens"] * warn_threshold / 100:
        warnings.append(
            f"SKILL.md approaching token limit: {skill_tokens} "
            f"({warn_threshold}% of {limits['skill_md_tokens']})"
        )

    if skill_lines > limits["skill_md_lines"]:
        warnings.append(
            f"SKILL.md exceeds line limit: {skill_lines} > {limits['skill_md_lines']}"
        )
    elif skill_lines > limits["skill_md_lines"] * warn_threshold / 100:
        warnings.append(
            f"SKILL.md approaching line limit: {skill_lines} "
            f"({warn_threshold}% of {limits['skill_md_lines']})"
        )

    # Check references
    ref_files: list[FileTokens] = []
    ref_total_tokens = 0

    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        for ref_file in sorted(refs_dir.rglob("*.md")):
            ref_content = ref_file.read_text()
            ref_tokens, _ = count_tokens(ref_content)
            ref_lines = count_lines(ref_content)
            rel_path = str(ref_file.relative_to(skill_dir))
            ref_files.append(
                FileTokens(path=rel_path, tokens=ref_tokens, lines=ref_lines, method=method)
            )
            ref_total_tokens += ref_tokens

            if ref_tokens > limits["single_ref_tokens"]:
                warnings.append(
                    f"{rel_path} exceeds limit: {ref_tokens} > {limits['single_ref_tokens']}"
                )

    # Check totals
    total_tokens = skill_tokens + ref_total_tokens

    if ref_total_tokens > limits["total_ref_tokens"]:
        warnings.append(
            f"Total references exceed limit: {ref_total_tokens} > {limits['total_ref_tokens']}"
        )

    if total_tokens > limits["total_skill_tokens"]:
        warnings.append(
            f"Total skill exceeds limit: {total_tokens} > {limits['total_skill_tokens']}"
        )

    # Determine pass/fail using hard limits
    passed = (
        skill_tokens <= hard["skill_md_tokens"]
        and skill_lines <= hard["skill_md_lines"]
        and ref_total_tokens <= hard["total_ref_tokens"]
        and total_tokens <= hard["total_skill_tokens"]
        and all(f["tokens"] <= hard["single_ref_tokens"] for f in ref_files)
    )

    return TokenReport(
        command_name=skill_name,
        command_tokens=skill_tokens,
        command_lines=skill_lines,
        ref_total_tokens=ref_total_tokens,
        ref_files=ref_files,
        total_tokens=total_tokens,
        method=method,
        warnings=warnings,
        passed=passed,
        is_directory=True,
    )


def print_report(report: TokenReport) -> None:
    """Print human-readable token report."""
    print(f"Token Count Report: {report['command_name']}")
    print("━" * 50)
    print()

    if report["is_directory"]:
        print("SKILL.md:")
        print(f"  Tokens: {report['command_tokens']:,} / {SKILL_LIMITS['skill_md_tokens']:,}")
        print(f"  Lines:  {report['command_lines']:,} / {SKILL_LIMITS['skill_md_lines']:,}")
    else:
        print("Command:")
        print(f"  Tokens: {report['command_tokens']:,} / {COMMAND_LIMITS['command_tokens']:,}")
        print(f"  Lines:  {report['command_lines']:,} / {COMMAND_LIMITS['command_lines']:,}")
    print()

    if report["ref_files"]:
        print("References:")
        for f in report["ref_files"]:
            print(f"  {f['path']}: {f['tokens']:,} tokens")
        print("  ────────────────────────────")
        print(f"  Total: {report['ref_total_tokens']:,} / {SKILL_LIMITS['total_ref_tokens']:,}")
        print()

    print(f"Total: {report['total_tokens']:,} tokens")
    print(f"Method: {report['method']}")
    print()

    if report["warnings"]:
        print("Warnings:")
        for w in report["warnings"]:
            print(f"  ⚠ {w}")
        print()

    print("━" * 50)
    if report["passed"]:
        print("✓ PASSED - Within token budget")
    else:
        print("✗ FAILED - Exceeds token budget")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Count tokens in command files")
    parser.add_argument("path", type=Path, help="Path to command file or directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--warn-threshold", type=int, default=80, help="Warning threshold percentage (default: 80)"
    )

    args = parser.parse_args()

    if args.path.is_dir():
        report = analyze_directory(args.path, args.warn_threshold)
    elif args.path.is_file():
        report = analyze_command_file(args.path, args.warn_threshold)
    else:
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
