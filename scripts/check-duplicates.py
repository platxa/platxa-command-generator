#!/usr/bin/env python3
"""check-duplicates.py - Detect duplicate or redundant commands.

Usage:
    python3 scripts/check-duplicates.py <command-file-or-directory>
    python3 scripts/check-duplicates.py --audit <commands-directory>

Detection layers:
    1. Exact name match  -> ERROR (exit 1)
    2. Fuzzy name match  -> WARNING (ratio >= 0.85)
    3. Description similarity -> WARNING (ratio >= 0.80)

For directory mode (self-validation), checks SKILL.md name against skills.
For file mode, checks command filename against existing commands.

Exit codes: 0 = no duplicates, 1 = exact duplicate found
"""

from __future__ import annotations

import argparse
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


def parse_command_frontmatter(command_path: Path) -> tuple[str, str]:
    """Extract name and description from a command .md file.

    For command files, name is derived from filename.
    Description is extracted from frontmatter if present.

    Returns:
        (name, description) tuple.
    """
    name = command_path.stem  # filename without .md

    try:
        text = command_path.read_text()
    except OSError:
        return name, ""

    # Extract description from frontmatter if present
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return name, ""

    fm = match.group(1)
    description = ""
    for line in fm.splitlines():
        if line.startswith("description:"):
            description = line.split(":", 1)[1].strip()
            break

    return name, description


def parse_skill_frontmatter(skill_md: Path) -> tuple[str, str]:
    """Extract name and description from SKILL.md frontmatter."""
    try:
        text = skill_md.read_text()
    except OSError:
        return "", ""

    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return "", ""

    fm = match.group(1)
    name = ""
    description = ""
    for line in fm.splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip()
        elif line.startswith("description:"):
            description = line.split(":", 1)[1].strip()

    return name, description


def collect_commands(
    commands_dir: Path, skip_path: Path | None = None
) -> list[tuple[str, str, Path]]:
    """Collect (name, description, path) from all .md files in a commands directory."""
    commands: list[tuple[str, str, Path]] = []
    if not commands_dir.is_dir():
        return commands

    for md_file in sorted(commands_dir.glob("*.md")):
        if skip_path and md_file.resolve() == skip_path.resolve():
            continue
        name, desc = parse_command_frontmatter(md_file)
        if name:
            commands.append((name, desc, md_file))

    return commands


def collect_skills(
    catalog_dir: Path, skip_dir: Path | None = None
) -> list[tuple[str, str, Path]]:
    """Collect (name, description, path) from SKILL.md files under catalog_dir."""
    skills: list[tuple[str, str, Path]] = []
    if not catalog_dir.is_dir():
        return skills

    for skill_md in sorted(catalog_dir.glob("*/SKILL.md")):
        skill_path = skill_md.parent
        if skip_dir and skill_path.resolve() == skip_dir.resolve():
            continue
        name, desc = parse_skill_frontmatter(skill_md)
        if name:
            skills.append((name, desc, skill_path))

    return skills


def normalize_name(name: str) -> str:
    """Strip common prefixes and hyphens, lowercase."""
    n = name.lower()
    for prefix in ("platxa-", "odoo-"):
        if n.startswith(prefix):
            n = n[len(prefix):]
    return n.replace("-", "")


def check_exact_name(
    target_name: str, items: list[tuple[str, str, Path]]
) -> list[tuple[str, Path]]:
    """Return items with exact same name."""
    return [(n, p) for n, _, p in items if n == target_name]


def check_fuzzy_name(
    target_name: str,
    items: list[tuple[str, str, Path]],
    threshold: float = 0.85,
) -> list[tuple[str, Path, float]]:
    """Return items with fuzzy name match above threshold."""
    norm_target = normalize_name(target_name)
    matches: list[tuple[str, Path, float]] = []
    for name, _, path in items:
        if name == target_name:
            continue
        norm = normalize_name(name)
        ratio = SequenceMatcher(None, norm_target, norm).ratio()
        if ratio >= threshold:
            matches.append((name, path, ratio))
    return matches


def check_description_similarity(
    target_desc: str,
    items: list[tuple[str, str, Path]],
    threshold: float = 0.80,
) -> list[tuple[str, Path, float]]:
    """Return items with similar descriptions above threshold."""
    if not target_desc:
        return []
    matches: list[tuple[str, Path, float]] = []
    for name, desc, path in items:
        if not desc:
            continue
        ratio = SequenceMatcher(None, target_desc.lower(), desc.lower()).ratio()
        if ratio >= threshold:
            matches.append((name, path, ratio))
    return matches


def check_item(
    target_name: str,
    target_desc: str,
    items: list[tuple[str, str, Path]],
) -> int:
    """Check a single item against a collection. Returns exit code."""
    has_error = False

    exact = check_exact_name(target_name, items)
    for name, path in exact:
        print(f"ERROR: Exact duplicate name '{name}' in {path}", file=sys.stderr)
        has_error = True

    fuzzy = check_fuzzy_name(target_name, items)
    for name, path, ratio in fuzzy:
        print(
            f"WARNING: Similar name '{name}' (ratio={ratio:.2f}) in {path}",
            file=sys.stderr,
        )

    desc_matches = check_description_similarity(target_desc, items)
    for name, path, ratio in desc_matches:
        print(
            f"WARNING: Similar description to '{name}' (ratio={ratio:.2f}) in {path}",
            file=sys.stderr,
        )

    if has_error:
        return 1

    print(f"No duplicates found for '{target_name}'")
    return 0


def check_path(target_path: Path, catalog: Path | None = None) -> int:
    """Check a file or directory against catalog. Returns exit code."""
    if target_path.is_dir():
        # Directory mode: check SKILL.md
        skill_md = target_path / "SKILL.md"
        if not skill_md.exists():
            print("ERROR: SKILL.md not found", file=sys.stderr)
            return 1

        target_name, target_desc = parse_skill_frontmatter(skill_md)
        if not target_name:
            print("ERROR: No name in frontmatter", file=sys.stderr)
            return 1

        if catalog is None:
            catalog = target_path.parent

        items = collect_skills(catalog, skip_dir=target_path)
        return check_item(target_name, target_desc, items)

    else:
        # File mode: check command .md file
        target_name, target_desc = parse_command_frontmatter(target_path)

        if catalog is None:
            catalog = target_path.parent

        items = collect_commands(catalog, skip_path=target_path)
        return check_item(target_name, target_desc, items)


def audit_catalog(catalog_dir: Path) -> int:
    """Check all commands in directory against each other. Returns exit code."""
    if not catalog_dir.is_dir():
        print(f"ERROR: Not a directory: {catalog_dir}", file=sys.stderr)
        return 1

    all_items = collect_commands(catalog_dir)
    if not all_items:
        print("No commands found in directory")
        return 0

    has_error = False
    seen_pairs: set[tuple[str, ...]] = set()

    for i, (name_a, desc_a, path_a) in enumerate(all_items):
        others = all_items[:i] + all_items[i + 1:]

        for name_b, _, path_b in others:
            pair = tuple(sorted([name_a, name_b]))
            if name_a == name_b and pair not in seen_pairs:
                seen_pairs.add(pair)
                print(
                    f"ERROR: Duplicate name '{name_a}': {path_a} and {path_b}",
                    file=sys.stderr,
                )
                has_error = True

        for name_b, path_b, ratio in check_fuzzy_name(name_a, others):
            pair = tuple(sorted([name_a, name_b]))
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                print(
                    f"WARNING: Similar names '{name_a}' <-> '{name_b}' "
                    f"(ratio={ratio:.2f}): {path_a} and {path_b}",
                    file=sys.stderr,
                )

        if desc_a:
            for name_b, path_b, ratio in check_description_similarity(desc_a, others):
                pair = tuple(sorted([name_a, name_b]))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    print(
                        f"WARNING: Similar descriptions '{name_a}' <-> '{name_b}' "
                        f"(ratio={ratio:.2f}): {path_a} and {path_b}",
                        file=sys.stderr,
                    )

    if has_error:
        return 1

    print(f"Audit complete: {len(all_items)} commands checked")
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Detect duplicate commands")
    parser.add_argument(
        "path",
        type=Path,
        help="Command file, directory, or catalog directory with --audit",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Audit entire directory for cross-duplicates",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="Catalog directory to compare against (default: parent of target)",
    )

    args = parser.parse_args()

    if args.audit:
        return audit_catalog(args.path)
    else:
        return check_path(args.path, catalog=args.catalog)


if __name__ == "__main__":
    sys.exit(main())
