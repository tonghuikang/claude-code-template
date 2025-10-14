"""Tests for post_edit_validator.py."""

from post_edit_validator import validate_edit_content


def test_validate_edit_content_exception():
    """Test that broad exception catching is flagged."""
    assert len(validate_edit_content("", "except Exception:", "test.py")) == 1
    assert (
        len(validate_edit_content("", "try: pass\nexcept Exception: pass", "test.py"))
        == 1
    )


def test_validate_edit_content_type_checking():
    """Test that TYPE_CHECKING usage is flagged."""
    assert len(validate_edit_content("", "if TYPE_CHECKING:", "test.py")) == 1
    assert (
        len(
            validate_edit_content(
                "", "from typing import TYPE_CHECKING\nif TYPE_CHECKING:", "test.py"
            )
        )
        == 1
    )


def test_validate_edit_content_allowed():
    """Test that allowed content passes validation."""
    assert len(validate_edit_content("", "except ValueError:", "test.py")) == 0
    assert len(validate_edit_content("", "except KeyError:", "test.py")) == 0
    assert len(validate_edit_content("", "def foo(): pass", "test.py")) == 0
    assert len(validate_edit_content("", "", "test.py")) == 0
