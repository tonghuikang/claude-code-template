"""Tests for post_bash_validator.py."""

from post_bash_validator import validate_bash_command


def test_validate_bash_command_chained():
    """Test that chained commands with && are flagged."""
    assert len(validate_bash_command("pwd && cat CLAUDE.md")) == 1
    assert len(validate_bash_command("git add . && git commit")) == 1


def test_validate_bash_command_allowed():
    """Test that allowed commands pass validation."""
    assert len(validate_bash_command("python run.py")) == 0
    assert len(validate_bash_command("python3 run.py")) == 0
    assert len(validate_bash_command("ls")) == 0
    assert len(validate_bash_command("pwd")) == 0
    assert len(validate_bash_command("uv run python3 run.py")) == 0
