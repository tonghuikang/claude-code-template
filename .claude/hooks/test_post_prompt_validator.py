"""Tests for post_prompt_validator.py."""

from post_prompt_validator import validate_user_prompt


def test_validate_user_prompt_ruff():
    """Test that prompts containing 'ruff' are flagged."""
    assert len(validate_user_prompt("please run ruff on my code")) == 1
    assert len(validate_user_prompt("use ruff to format")) == 1


def test_validate_user_prompt_allowed():
    """Test that allowed prompts pass validation."""
    assert len(validate_user_prompt("format my code")) == 0
    assert len(validate_user_prompt("check my python files")) == 0
    assert len(validate_user_prompt("run the tests")) == 0
