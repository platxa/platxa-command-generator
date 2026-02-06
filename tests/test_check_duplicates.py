"""Tests for check-duplicates.py script.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- Exact name duplicate detected (exit 1)
- Fuzzy name match warned
- No duplicates passes cleanly (exit 0)
- Self-comparison excluded
- Audit mode for directory-wide scanning
- Different commands with different names pass
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from helpers import create_command_md


@pytest.fixture
def run_check_duplicates(scripts_dir: Path):
    """Fixture to run check-duplicates.py."""
    script_path = scripts_dir / "check-duplicates.py"

    def _run(
        target: Path,
        *,
        audit: bool = False,
        catalog: Path | None = None,
    ) -> subprocess.CompletedProcess:
        cmd = ["python3", str(script_path)]
        if audit:
            cmd.append("--audit")
        if catalog:
            cmd.extend(["--catalog", str(catalog)])
        cmd.append(str(target))
        return subprocess.run(cmd, capture_output=True, text=True)

    return _run


class TestExactDuplicate:
    """Tests for exact name duplicate detection."""

    @pytest.mark.duplicates
    def test_exact_name_duplicate_exits_1(self, tmp_path: Path, run_check_duplicates) -> None:
        """Exact duplicate command name returns exit code 1."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        # Existing command
        create_command_md(commands_dir, "deploy", description="Deploy app")

        # New command with same name in different directory
        new_dir = tmp_path / "new"
        new_dir.mkdir()
        cmd = create_command_md(new_dir, "deploy", description="Different description")

        result = run_check_duplicates(cmd, catalog=commands_dir)
        assert result.returncode == 1
        assert "Exact duplicate" in result.stderr


class TestFuzzyName:
    """Tests for fuzzy name matching."""

    @pytest.mark.duplicates
    def test_fuzzy_name_warns(self, tmp_path: Path, run_check_duplicates) -> None:
        """Similar names produce a warning."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        create_command_md(commands_dir, "test-runner", description="Run tests")

        new_dir = tmp_path / "new"
        new_dir.mkdir()
        cmd = create_command_md(new_dir, "test-runer", description="Completely different")

        result = run_check_duplicates(cmd, catalog=commands_dir)
        assert result.returncode == 0
        assert "Similar name" in result.stderr


class TestNoDuplicates:
    """Tests for clean pass scenarios."""

    @pytest.mark.duplicates
    def test_unique_command_passes(self, tmp_path: Path, run_check_duplicates) -> None:
        """Unique command with no matches returns exit 0."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        create_command_md(commands_dir, "deploy", description="Deploy app")

        new_dir = tmp_path / "new"
        new_dir.mkdir()
        cmd = create_command_md(new_dir, "lint", description="Run linter")

        result = run_check_duplicates(cmd, catalog=commands_dir)
        assert result.returncode == 0
        assert "No duplicates" in result.stdout

    @pytest.mark.duplicates
    def test_empty_catalog_passes(self, tmp_path: Path, run_check_duplicates) -> None:
        """Empty catalog directory passes cleanly."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        new_dir = tmp_path / "new"
        new_dir.mkdir()
        cmd = create_command_md(new_dir, "new-cmd", description="A new command")

        result = run_check_duplicates(cmd, catalog=commands_dir)
        assert result.returncode == 0


class TestSelfExclusion:
    """Tests for self-comparison exclusion."""

    @pytest.mark.duplicates
    def test_self_not_compared(self, tmp_path: Path, run_check_duplicates) -> None:
        """Command does not match against itself."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        cmd = create_command_md(commands_dir, "my-cmd", description="Some description")

        result = run_check_duplicates(cmd, catalog=commands_dir)
        assert result.returncode == 0
        assert "No duplicates" in result.stdout


class TestAuditMode:
    """Tests for --audit directory-wide scan."""

    @pytest.mark.duplicates
    def test_audit_clean_directory(self, tmp_path: Path, run_check_duplicates) -> None:
        """Audit on directory with no duplicates passes."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        for name in ("alpha", "beta", "gamma"):
            create_command_md(commands_dir, name, description=f"Description for {name}")

        result = run_check_duplicates(commands_dir, audit=True)
        assert result.returncode == 0
        assert "Audit complete" in result.stdout


class TestDescriptionSimilarity:
    """Tests for description similarity detection."""

    @pytest.mark.duplicates
    def test_similar_descriptions_warns(self, tmp_path: Path, run_check_duplicates) -> None:
        """Near-identical descriptions produce a warning."""
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()

        create_command_md(
            commands_dir,
            "cmd-a",
            description="Run automated tests for the platform using pytest",
        )

        new_dir = tmp_path / "new"
        new_dir.mkdir()
        cmd = create_command_md(
            new_dir,
            "cmd-b",
            description="Run automated tests for the platform using pytest.",
        )

        result = run_check_duplicates(cmd, catalog=commands_dir)
        assert result.returncode == 0
        assert "Similar description" in result.stderr
