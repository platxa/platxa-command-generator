"""Tests for validate-structure.sh script.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- Valid command file structure
- Missing/empty file detection
- Directory mode (self-validation) with SKILL.md
- Script permissions in directory mode
"""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import create_command_md, create_skill_md


class TestValidCommandFile:
    """Tests for valid command file acceptance."""

    @pytest.mark.structure
    def test_valid_command_file_passes(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Valid command .md file returns exit code 0."""
        create_command_md(
            temp_command_dir,
            name="valid-command",
            description="Run tests",
            tools=["Read", "Bash"],
        )

        result = run_validate_structure(temp_command_dir / "valid-command.md")

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"
        assert "PASSED" in result.stdout

    @pytest.mark.structure
    def test_basic_command_no_frontmatter_passes(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Command without frontmatter (basic type) passes structure check."""
        command_md = temp_command_dir / "basic.md"
        command_md.write_text("# Basic Command\n\nJust instructions.\n")

        result = run_validate_structure(command_md)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"


class TestMissingAndEmptyFiles:
    """Tests for missing and empty file detection."""

    @pytest.mark.structure
    def test_missing_file_fails(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Missing file returns exit code 1."""
        result = run_validate_structure(temp_command_dir / "nonexistent.md")

        assert result.returncode == 1, "Expected exit 1 for missing file"
        assert "not found" in result.stderr.lower() or "ERROR" in result.stderr

    @pytest.mark.structure
    def test_empty_file_fails(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Empty file returns exit code 1."""
        command_md = temp_command_dir / "empty.md"
        command_md.write_text("")

        result = run_validate_structure(command_md)

        assert result.returncode == 1, "Expected exit 1 for empty file"
        assert "empty" in result.stderr.lower() or "ERROR" in result.stderr


class TestH1Heading:
    """Tests for H1 heading requirement."""

    @pytest.mark.structure
    def test_missing_h1_heading_fails(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Command without H1 heading fails validation."""
        command_md = temp_command_dir / "no-heading.md"
        command_md.write_text("""Just some text without any heading.

Do the thing.
""")

        result = run_validate_structure(command_md)

        assert result.returncode == 1, (
            f"Expected exit 1 for missing H1. stderr: {result.stderr}"
        )
        assert "h1" in result.stderr.lower() or "heading" in result.stderr.lower()

    @pytest.mark.structure
    def test_h1_heading_passes(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Command with H1 heading passes."""
        create_command_md(
            temp_command_dir,
            name="with-heading",
            content="# My Command\n\nDo the thing.\n",
        )

        result = run_validate_structure(temp_command_dir / "with-heading.md")

        assert result.returncode == 0, (
            f"Expected exit 0 for command with H1. stderr: {result.stderr}"
        )


class TestVagueInstructions:
    """Tests for vague instruction detection."""

    @pytest.mark.structure
    def test_vague_instruction_warns(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Vague instructions like 'improve the code' generate warning."""
        command_md = temp_command_dir / "vague.md"
        command_md.write_text("""# Vague Command

Look at the project and improve the code.
Fix issues you find.
""")

        result = run_validate_structure(command_md)

        # Should pass (warning, not error) but stderr should have warning
        assert result.returncode == 0, f"Expected exit 0 (warning). stderr: {result.stderr}"
        assert "vague" in result.stderr.lower() or "WARN" in result.stderr


class TestPromptSpecificity:
    """Tests for prompt specificity check."""

    @pytest.mark.structure
    def test_no_concrete_references_warns(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Command with no file paths, code, or tool names generates warning."""
        command_md = temp_command_dir / "generic.md"
        command_md.write_text("# Generic Command\n\nDo something useful.\n")

        result = run_validate_structure(command_md)

        assert result.returncode == 0, f"Expected exit 0 (warning). stderr: {result.stderr}"
        assert "concrete" in result.stderr.lower() or "WARN" in result.stderr

    @pytest.mark.structure
    def test_concrete_references_passes(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Command with backtick code references passes specificity check."""
        create_command_md(
            temp_command_dir,
            name="specific",
            content="# Specific Command\n\nRun `pytest tests/` and check results.\n",
        )

        result = run_validate_structure(temp_command_dir / "specific.md")

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"
        assert "concrete" in result.stdout.lower() or "Concrete" in result.stdout


class TestDirectoryMode:
    """Tests for directory mode (self-validation with SKILL.md)."""

    @pytest.mark.structure
    def test_valid_directory_passes(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Valid directory with SKILL.md returns exit code 0."""
        create_skill_md(
            temp_command_dir,
            name="test-generator",
            description="A test generator skill for validation testing.",
            tools=["Read", "Write"],
        )

        result = run_validate_structure(temp_command_dir)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"
        assert "PASSED" in result.stdout

    @pytest.mark.structure
    def test_directory_missing_skill_md_fails(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Directory without SKILL.md returns exit code 1."""
        result = run_validate_structure(temp_command_dir)

        assert result.returncode == 1, "Expected exit 1 for missing SKILL.md"

    @pytest.mark.structure
    def test_directory_empty_skill_md_fails(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Directory with empty SKILL.md returns exit code 1."""
        skill_md = temp_command_dir / "SKILL.md"
        skill_md.write_text("")

        result = run_validate_structure(temp_command_dir)

        assert result.returncode == 1, "Expected exit 1 for empty SKILL.md"

    @pytest.mark.structure
    def test_directory_no_frontmatter_fails(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Directory with SKILL.md without frontmatter returns exit code 1."""
        skill_md = temp_command_dir / "SKILL.md"
        skill_md.write_text("# No Frontmatter\n\nJust content.\n")

        result = run_validate_structure(temp_command_dir)

        assert result.returncode == 1, "Expected exit 1 for missing frontmatter"

    @pytest.mark.structure
    def test_non_executable_script_fails(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Non-executable .sh scripts in directory mode return exit code 1."""
        create_skill_md(
            temp_command_dir,
            name="bad-scripts",
            description="A skill with non-executable scripts.",
        )

        scripts_dir = temp_command_dir / "scripts"
        scripts_dir.mkdir()
        script = scripts_dir / "run.sh"
        script.write_text("#!/bin/bash\necho 'test'")
        script.chmod(0o644)

        result = run_validate_structure(temp_command_dir)

        assert result.returncode == 1, "Expected exit 1 for non-executable script"

    @pytest.mark.structure
    def test_placeholder_content_fails(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Command with placeholder content (TODO, FIXME) is rejected."""
        command_md = temp_command_dir / "placeholder.md"
        command_md.write_text("# My Command\n\nTODO: implement this step\n")

        result = run_validate_structure(command_md)

        assert result.returncode == 1, f"Expected exit 1 for placeholder. stderr: {result.stderr}"
        assert "placeholder" in result.stderr.lower() or "TODO" in result.stderr

    @pytest.mark.structure
    @pytest.mark.slow
    def test_large_files_warns(
        self,
        temp_command_dir: Path,
        run_validate_structure,
    ) -> None:
        """Files larger than 100KB generate warning in directory mode."""
        create_skill_md(
            temp_command_dir,
            name="large-files",
            description="A skill with large files.",
        )

        refs_dir = temp_command_dir / "references"
        refs_dir.mkdir()
        large_file = refs_dir / "large.md"
        large_file.write_text("x" * (101 * 1024))

        result = run_validate_structure(temp_command_dir)

        assert result.returncode == 0, "Expected exit 0 (warning only)"
        assert "100" in result.stderr or "large" in result.stderr.lower() or "WARN" in result.stderr
