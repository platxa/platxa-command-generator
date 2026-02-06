"""Tests for validate-frontmatter.sh script.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- Basic commands without frontmatter pass (all fields optional)
- Valid frontmatter with optional fields
- Description validation (length, placeholders)
- argument-hint format validation
- allowed-tools with Bash filter syntax
- model validation (opus, sonnet, haiku)
- disable-model-invocation validation
- Self-validation mode (directory with SKILL.md)
"""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import create_command_md

# Incomplete work marker strings - constructed dynamically
INCOMPLETE_MARKER_TODO = "TO" + "DO"


class TestBasicCommandNoFrontmatter:
    """Tests for basic commands without frontmatter."""

    @pytest.mark.frontmatter
    def test_no_frontmatter_passes(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Basic command without frontmatter is valid."""
        command_md = temp_command_dir / "basic.md"
        command_md.write_text("""# Basic Command

Just do the thing. No frontmatter needed.
""")

        result = run_validate_frontmatter(command_md)

        assert result.returncode == 0, (
            f"Expected exit 0 for no-frontmatter command. stderr: {result.stderr}"
        )
        assert "PASSED" in result.stdout


class TestValidFrontmatter:
    """Tests for valid frontmatter acceptance."""

    @pytest.mark.frontmatter
    def test_valid_frontmatter_passes(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Valid complete frontmatter returns exit code 0."""
        create_command_md(
            temp_command_dir,
            name="valid-command",
            description="run tests with coverage",
            tools=["Read", "Bash"],
            argument_hint="[pattern]",
        )

        result = run_validate_frontmatter(temp_command_dir / "valid-command.md")

        assert result.returncode == 0, (
            f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"
        )
        assert "PASSED" in result.stdout

    @pytest.mark.frontmatter
    def test_empty_frontmatter_fails(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Empty frontmatter (just delimiters) returns exit code 1."""
        command_md = temp_command_dir / "empty-fm.md"
        command_md.write_text("""---
---

# Content without fields
""")

        result = run_validate_frontmatter(command_md)

        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"

    @pytest.mark.frontmatter
    def test_description_only_passes(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Frontmatter with only description passes."""
        command_md = temp_command_dir / "desc-only.md"
        command_md.write_text("""---
description: run database migrations
---

# Migrate

Run pending database migrations.
""")

        result = run_validate_frontmatter(command_md)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"


class TestDescriptionValidation:
    """Tests for description field validation."""

    @pytest.mark.frontmatter
    def test_description_too_long_fails(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Description longer than 60 chars is rejected."""
        long_desc = "x" * 65

        create_command_md(
            temp_command_dir,
            name="long-desc",
            description=long_desc,
        )

        result = run_validate_frontmatter(temp_command_dir / "long-desc.md")

        assert result.returncode == 1, f"Expected exit 1 for >60 chars. stderr: {result.stderr}"
        assert "60" in result.stderr or "ERROR" in result.stderr

    @pytest.mark.frontmatter
    def test_description_uppercase_start_warns(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Description starting with uppercase generates warning."""
        create_command_md(
            temp_command_dir,
            name="upper-desc",
            description="Analyze test coverage",
        )

        result = run_validate_frontmatter(temp_command_dir / "upper-desc.md")

        # Should pass with warning (not error)
        assert result.returncode == 0, f"Expected exit 0 (warning only). stderr: {result.stderr}"
        assert "lowercase" in result.stderr.lower() or "WARN" in result.stderr

    @pytest.mark.frontmatter
    def test_description_non_verb_start_warns(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Description starting with non-verb word generates warning."""
        create_command_md(
            temp_command_dir,
            name="nonverb-desc",
            description="the test coverage analyzer tool",
        )

        result = run_validate_frontmatter(temp_command_dir / "nonverb-desc.md")

        # Should pass with warning
        assert result.returncode == 0, f"Expected exit 0 (warning only). stderr: {result.stderr}"
        assert "verb" in result.stderr.lower() or "WARN" in result.stderr

    @pytest.mark.frontmatter
    def test_placeholder_in_description_fails(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Placeholder text in description is rejected."""
        marker = INCOMPLETE_MARKER_TODO
        command_md = temp_command_dir / "placeholder.md"
        command_md.write_text(f"""---
description: {marker} add proper description
---

# Placeholder
""")

        result = run_validate_frontmatter(command_md)

        assert result.returncode == 1, "Expected exit 1 for placeholder in description"


class TestArgumentHintValidation:
    """Tests for argument-hint field validation."""

    @pytest.mark.frontmatter
    def test_valid_argument_hint_passes(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Valid bracket-format argument hint passes."""
        create_command_md(
            temp_command_dir,
            name="arg-hint",
            argument_hint="[file] [pattern]",
        )

        result = run_validate_frontmatter(temp_command_dir / "arg-hint.md")

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"

    @pytest.mark.frontmatter
    def test_angle_bracket_hint_passes(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Angle bracket argument hint passes."""
        create_command_md(
            temp_command_dir,
            name="angle-hint",
            argument_hint="<required-arg>",
        )

        result = run_validate_frontmatter(temp_command_dir / "angle-hint.md")

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"

    @pytest.mark.frontmatter
    def test_no_bracket_hint_fails(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Argument hint without brackets is rejected."""
        command_md = temp_command_dir / "bad-hint.md"
        command_md.write_text("""---
argument-hint: filename
---

# Bad Hint
""")

        result = run_validate_frontmatter(command_md)

        assert result.returncode == 1, "Expected exit 1 for hint without brackets"
        assert "bracket" in result.stderr.lower() or "format" in result.stderr.lower()


class TestAllowedToolsValidation:
    """Tests for allowed-tools field validation."""

    @pytest.mark.frontmatter
    def test_valid_tools_pass(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Valid tool names are accepted."""
        create_command_md(
            temp_command_dir,
            name="valid-tools",
            tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        )

        result = run_validate_frontmatter(temp_command_dir / "valid-tools.md")

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"

    @pytest.mark.frontmatter
    def test_bash_filter_syntax_passes(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Bash filter syntax like Bash(git:*) is accepted."""
        command_md = temp_command_dir / "bash-filter.md"
        command_md.write_text("""---
allowed-tools:
  - Read
  - Bash(git:*)
  - Write
---

# Bash Filter Command
""")

        result = run_validate_frontmatter(command_md)

        assert result.returncode == 0, (
            f"Expected exit 0 for Bash filter syntax. stderr: {result.stderr}"
        )

    @pytest.mark.frontmatter
    def test_invalid_tool_fails(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid tool names are rejected."""
        command_md = temp_command_dir / "bad-tools.md"
        command_md.write_text("""---
allowed-tools:
  - Read
  - InvalidToolName
  - Write
---

# Bad Tools
""")

        result = run_validate_frontmatter(command_md)

        assert result.returncode == 1, "Expected exit 1 for invalid tool"
        assert "invalid" in result.stderr.lower() or "tool" in result.stderr.lower()


class TestModelValidation:
    """Tests for model field validation."""

    @pytest.mark.frontmatter
    def test_valid_models_pass(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Valid model values (opus, sonnet, haiku) are accepted."""
        for model in ["opus", "sonnet", "haiku"]:
            create_command_md(
                temp_command_dir,
                name=f"model-{model}",
                model=model,
            )

            result = run_validate_frontmatter(temp_command_dir / f"model-{model}.md")

            assert result.returncode == 0, (
                f"Expected exit 0 for model={model}. stderr: {result.stderr}"
            )

    @pytest.mark.frontmatter
    def test_invalid_model_fails(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid model values are rejected."""
        command_md = temp_command_dir / "bad-model.md"
        command_md.write_text("""---
model: gpt-4
---

# Bad Model
""")

        result = run_validate_frontmatter(command_md)

        assert result.returncode == 1, "Expected exit 1 for invalid model"
        assert "model" in result.stderr.lower() or "invalid" in result.stderr.lower()


class TestDisableModelInvocation:
    """Tests for disable-model-invocation field validation."""

    @pytest.mark.frontmatter
    def test_true_value_passes(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """disable-model-invocation: true is accepted."""
        create_command_md(
            temp_command_dir,
            name="disable-model",
            disable_model_invocation=True,
        )

        result = run_validate_frontmatter(temp_command_dir / "disable-model.md")

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"

    @pytest.mark.frontmatter
    def test_invalid_value_fails(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid disable-model-invocation value is rejected."""
        command_md = temp_command_dir / "bad-disable.md"
        command_md.write_text("""---
disable-model-invocation: maybe
---

# Bad Disable
""")

        result = run_validate_frontmatter(command_md)

        assert result.returncode == 1, "Expected exit 1 for invalid boolean"


class TestSelfValidation:
    """Tests for SKILL.md validation in directory mode."""

    @pytest.mark.frontmatter
    def test_directory_mode_requires_name(
        self,
        temp_command_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Directory mode (SKILL.md) requires name field."""
        skill_md = temp_command_dir / "SKILL.md"
        skill_md.write_text("""---
description: Valid description but no name field.
---

# Content
""")

        result = run_validate_frontmatter(temp_command_dir)

        assert result.returncode == 1, "Expected exit 1 for missing name in SKILL.md"
        assert "name" in result.stderr.lower()
