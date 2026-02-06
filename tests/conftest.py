"""Pytest configuration and fixtures for platxa-command-generator tests.

This module provides fixtures for creating temporary command files
and helper functions for testing the validation scripts.

All tests use REAL file system operations - NO mocks or simulations.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from collections.abc import Callable, Generator
from pathlib import Path

import pytest

# Path to the command generator root
COMMAND_GENERATOR_ROOT = Path(__file__).parent.parent


@pytest.fixture
def temp_command_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test command files.

    Yields:
        Path to the temporary directory
    """
    with tempfile.TemporaryDirectory(prefix="command_test_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def scripts_dir() -> Path:
    """Get the path to the scripts directory."""
    return COMMAND_GENERATOR_ROOT / "scripts"


@pytest.fixture
def run_validate_frontmatter(scripts_dir: Path) -> Callable[..., subprocess.CompletedProcess]:
    """Fixture that returns a function to run validate-frontmatter.sh."""
    script_path = scripts_dir / "validate-frontmatter.sh"

    def _run(target: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(script_path), str(target)],
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},
        )

    return _run


@pytest.fixture
def run_validate_structure(scripts_dir: Path) -> Callable[..., subprocess.CompletedProcess]:
    """Fixture that returns a function to run validate-structure.sh."""
    script_path = scripts_dir / "validate-structure.sh"

    def _run(target: Path, verbose: bool = False) -> subprocess.CompletedProcess:
        cmd = [str(script_path)]
        if verbose:
            cmd.append("--verbose")
        cmd.append(str(target))

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},
        )

    return _run


@pytest.fixture
def run_count_tokens(scripts_dir: Path) -> Callable[..., subprocess.CompletedProcess]:
    """Fixture that returns a function to run count-tokens.py."""
    script_path = scripts_dir / "count-tokens.py"

    def _run(
        target: Path, json_output: bool = False, warn_threshold: int = 80
    ) -> subprocess.CompletedProcess:
        cmd = ["python3", str(script_path)]
        if json_output:
            cmd.append("--json")
        if warn_threshold != 80:
            cmd.extend(["--warn-threshold", str(warn_threshold)])
        cmd.append(str(target))

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

    return _run


@pytest.fixture
def run_security_check(scripts_dir: Path) -> Callable[..., subprocess.CompletedProcess]:
    """Fixture that returns a function to run security-check.sh."""
    script_path = scripts_dir / "security-check.sh"

    def _run(target: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(script_path), str(target)],
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},
        )

    return _run


@pytest.fixture
def run_validate_all(scripts_dir: Path) -> Callable[..., subprocess.CompletedProcess]:
    """Fixture that returns a function to run validate-all.sh."""
    script_path = scripts_dir / "validate-all.sh"

    def _run(target: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(script_path), str(target)],
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},
        )

    return _run


@pytest.fixture
def run_install_command(
    scripts_dir: Path,
) -> Callable[..., subprocess.CompletedProcess]:
    """Fixture that returns a function to run install-command.sh."""
    script_path = scripts_dir / "install-command.sh"

    def _run(
        target: Path,
        target_base: Path,
        location: str = "--project",
    ) -> subprocess.CompletedProcess:
        env = {**os.environ, "TERM": "dumb"}
        if location == "--user":
            env["HOME"] = str(target_base)

        cwd = str(target_base) if location == "--project" else None

        return subprocess.run(
            [str(script_path), str(target), location],
            capture_output=True,
            text=True,
            env=env,
            cwd=cwd,
            input="n\n",  # Auto-answer "no" to overwrite prompt
        )

    return _run


@pytest.fixture
def create_valid_command(temp_command_dir: Path) -> Callable[[], Path]:
    """Fixture that returns a function to create a valid command file."""

    def _create() -> Path:
        command_md = temp_command_dir / "test-command.md"
        command_md.write_text("""---
description: Run tests with coverage
allowed-tools:
  - Bash
  - Read
argument-hint: "[test-pattern]"
---

# Test Runner

Run project tests with optional pattern filtering.

## Usage

When invoked with an argument, run only matching tests:

```
pytest $1 -v --tb=short
```

Without arguments, run all tests:

```
pytest tests/ -v
```
""")
        return command_md

    return _create


@pytest.fixture
def self_dir() -> Path:
    """Get the path to the platxa-command-generator itself for self-testing."""
    return COMMAND_GENERATOR_ROOT
