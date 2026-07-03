"""Tests for process_pre_bash.py."""

from process_pre_bash import validate_pre_bash_command


def test_validate_pre_bash_command_python():
    """Test that python commands are flagged."""
    assert len(validate_pre_bash_command("python run.py")) == 1
    assert len(validate_pre_bash_command("python3 run.py")) == 1


def test_validate_pre_bash_command_allowed():
    """Test that allowed commands pass validation."""
    assert len(validate_pre_bash_command("uv run python3 run.py")) == 0
    assert len(validate_pre_bash_command("ls")) == 0
    assert len(validate_pre_bash_command("pwd")) == 0
    assert len(validate_pre_bash_command("grep foo")) == 0
    assert len(validate_pre_bash_command("grep -r pattern")) == 0
