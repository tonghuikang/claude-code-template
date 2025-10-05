"""Tests for pre_bash_validator.py."""

from pre_bash_validator import validate_before_execution


def test_validate_before_execution_python():
    """Test that python commands are flagged."""
    assert len(validate_before_execution("python run.py")) == 1
    assert len(validate_before_execution("python3 run.py")) == 1


def test_validate_before_execution_grep():
    """Test that grep commands are flagged."""
    assert len(validate_before_execution("grep foo")) == 1
    assert len(validate_before_execution("grep -r pattern")) == 1


def test_validate_before_execution_allowed():
    """Test that allowed commands pass validation."""
    assert len(validate_before_execution("uv run python3 run.py")) == 0
    assert len(validate_before_execution("ls")) == 0
    assert len(validate_before_execution("pwd")) == 0
