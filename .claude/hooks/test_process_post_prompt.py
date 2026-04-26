"""Tests for process_post_prompt.py."""

from process_post_prompt import validate_user_prompt


def test_validate_user_prompt_allowed():
    """Test that allowed prompts pass validation."""
    assert len(validate_user_prompt("format my code")) == 0
    assert len(validate_user_prompt("check my python files")) == 0
    assert len(validate_user_prompt("run the tests")) == 0
    assert len(validate_user_prompt("please run ruff on my code")) == 0
    assert len(validate_user_prompt("use ruff to format")) == 0
