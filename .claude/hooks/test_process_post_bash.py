"""Tests for process_post_bash.py."""

from process_post_bash import validate_post_bash_command


def test_validate_post_bash_command_allowed():
    """Test that allowed commands pass validation."""
    assert len(validate_post_bash_command("python run.py")) == 0
    assert len(validate_post_bash_command("python3 run.py")) == 0
    assert len(validate_post_bash_command("ls")) == 0
    assert len(validate_post_bash_command("pwd")) == 0
    assert len(validate_post_bash_command("uv run python3 run.py")) == 0
    assert len(validate_post_bash_command("pwd && cat CLAUDE.md")) == 0
    assert len(validate_post_bash_command("git add . && git commit")) == 0
