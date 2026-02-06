"""Tests for count-tokens.py script.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- Small command passes (within budget)
- Command token limit (2000 recommended, 4000 hard)
- Command line limit (300 recommended, 600 hard)
- JSON output format
- Missing file handling
- Directory mode (self-validation with skill-level limits)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers import (
    create_command_md,
    create_skill_md,
    generate_long_lines,
    generate_long_text,
)


class TestSmallCommandPasses:
    """Tests for small command acceptance."""

    @pytest.mark.tokens
    def test_small_command_passes(
        self,
        temp_command_dir: Path,
        run_count_tokens,
    ) -> None:
        """Small command returns passed=true."""
        create_command_md(
            temp_command_dir,
            name="small-cmd",
            description="Run tests",
            tools=["Bash"],
            content="# Small Command\n\nRun tests.\n",
        )

        result = run_count_tokens(temp_command_dir / "small-cmd.md", json_output=True)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"

        data = json.loads(result.stdout)
        assert data["passed"] is True
        assert data["command_tokens"] < 2000


class TestCommandTokenLimits:
    """Tests for command token limits."""

    @pytest.mark.tokens
    @pytest.mark.slow
    def test_command_over_hard_token_limit_fails(
        self,
        temp_command_dir: Path,
        run_count_tokens,
    ) -> None:
        """Command exceeding hard token limit (4000) fails."""
        long_content = generate_long_text(4500)

        create_command_md(
            temp_command_dir,
            name="large-cmd",
            description="Too many tokens",
            content=f"# Large Command\n\n{long_content}\n",
        )

        result = run_count_tokens(temp_command_dir / "large-cmd.md", json_output=True)

        assert result.returncode == 1, "Expected exit 1 for token limit exceeded"

        data = json.loads(result.stdout)
        assert data["passed"] is False
        assert data["command_tokens"] > 4000

    @pytest.mark.tokens
    @pytest.mark.slow
    def test_command_over_recommended_warns(
        self,
        temp_command_dir: Path,
        run_count_tokens,
    ) -> None:
        """Command exceeding recommended limit (2000) but under hard limit warns."""
        content = generate_long_text(2500)

        create_command_md(
            temp_command_dir,
            name="warn-cmd",
            content=f"# Warning Command\n\n{content}\n",
        )

        result = run_count_tokens(temp_command_dir / "warn-cmd.md", json_output=True)

        data = json.loads(result.stdout)

        # Should pass (under hard limit) but have warnings
        if data["command_tokens"] <= 4000:
            assert data["passed"] is True
        if data["command_tokens"] > 2000:
            assert any("exceeds" in w.lower() or "limit" in w.lower() for w in data["warnings"])


class TestCommandLineLimits:
    """Tests for command line limits."""

    @pytest.mark.tokens
    def test_command_over_hard_line_limit_fails(
        self,
        temp_command_dir: Path,
        run_count_tokens,
    ) -> None:
        """Command exceeding hard line limit (600) fails."""
        long_content = generate_long_lines(610)

        create_command_md(
            temp_command_dir,
            name="many-lines",
            content=f"# Many Lines\n\n{long_content}\n",
        )

        result = run_count_tokens(temp_command_dir / "many-lines.md", json_output=True)

        assert result.returncode == 1, "Expected exit 1 for line limit exceeded"

        data = json.loads(result.stdout)
        assert data["passed"] is False
        assert data["command_lines"] > 600


class TestJsonOutput:
    """Tests for JSON output format."""

    @pytest.mark.tokens
    def test_json_output_valid(
        self,
        temp_command_dir: Path,
        run_count_tokens,
    ) -> None:
        """--json flag outputs valid JSON with required fields."""
        create_command_md(
            temp_command_dir,
            name="json-test",
            description="Test JSON output",
        )

        result = run_count_tokens(temp_command_dir / "json-test.md", json_output=True)

        data = json.loads(result.stdout)

        # Check required fields
        assert "command_name" in data
        assert "command_tokens" in data
        assert "command_lines" in data
        assert "total_tokens" in data
        assert "method" in data
        assert "warnings" in data
        assert "passed" in data

        # Check types
        assert isinstance(data["command_name"], str)
        assert isinstance(data["command_tokens"], int)
        assert isinstance(data["command_lines"], int)
        assert isinstance(data["total_tokens"], int)
        assert isinstance(data["method"], str)
        assert isinstance(data["warnings"], list)
        assert isinstance(data["passed"], bool)


class TestMissingFile:
    """Tests for missing file handling."""

    @pytest.mark.tokens
    def test_missing_file_fails(
        self,
        temp_command_dir: Path,
        run_count_tokens,
    ) -> None:
        """Missing file returns exit code 1."""
        result = run_count_tokens(temp_command_dir / "nonexistent.md", json_output=True)

        assert result.returncode == 1, "Expected exit 1 for missing file"


class TestDirectoryMode:
    """Tests for directory mode (skill-level limits)."""

    @pytest.mark.tokens
    def test_directory_mode_uses_skill_limits(
        self,
        temp_command_dir: Path,
        run_count_tokens,
    ) -> None:
        """Directory mode uses skill-level limits (5000 tokens, 500 lines)."""
        create_skill_md(
            temp_command_dir,
            name="test-generator",
            description="A test generator skill.",
            content="# Generator\n\nSmall content.\n",
        )

        result = run_count_tokens(temp_command_dir, json_output=True)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"

        data = json.loads(result.stdout)
        assert data["passed"] is True
        assert data["is_directory"] is True

    @pytest.mark.tokens
    def test_directory_missing_skill_md_fails(
        self,
        temp_command_dir: Path,
        run_count_tokens,
    ) -> None:
        """Directory without SKILL.md fails gracefully."""
        result = run_count_tokens(temp_command_dir, json_output=True)

        assert result.returncode == 1, "Expected exit 1 for missing SKILL.md"

        data = json.loads(result.stdout)
        assert data["passed"] is False
