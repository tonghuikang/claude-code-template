"""Tests for post_bash_validator.py."""

from post_bash_validator import validate_after_execution


def test_validate_after_execution_chained():
    """Test that chained commands with && are flagged."""
    assert len(validate_after_execution("pwd && cat CLAUDE.md")) == 1
    assert len(validate_after_execution("git add . && git commit")) == 1


def test_validate_after_execution_allowed():
    """Test that allowed commands pass validation."""
    assert len(validate_after_execution("python run.py")) == 0
    assert len(validate_after_execution("python3 run.py")) == 0
    assert len(validate_after_execution("ls")) == 0
    assert len(validate_after_execution("pwd")) == 0
    assert len(validate_after_execution("uv run python3 run.py")) == 0
