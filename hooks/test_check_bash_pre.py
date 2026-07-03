"""Tests for check_bash_pre.py."""

from check_bash_pre import check_bash_pre


def test_check_bash_pre_python():
    """Test that python commands are flagged."""
    assert len(check_bash_pre("python run.py")) == 1
    assert len(check_bash_pre("python3 run.py")) == 1


def test_check_bash_pre_allowed():
    """Test that allowed commands pass validation."""
    assert len(check_bash_pre("uv run python3 run.py")) == 0
    assert len(check_bash_pre("ls")) == 0
    assert len(check_bash_pre("pwd")) == 0
    assert len(check_bash_pre("grep foo")) == 0
    assert len(check_bash_pre("grep -r pattern")) == 0
