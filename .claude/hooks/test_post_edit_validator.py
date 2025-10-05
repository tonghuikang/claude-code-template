"""Tests for post_edit_validator.py."""

from post_edit_validator import validate_content


def test_validate_content_exception():
    """Test that broad exception catching is flagged."""
    assert len(validate_content("except Exception:")) == 1
    assert len(validate_content("try: pass\nexcept Exception: pass")) == 1


def test_validate_content_type_checking():
    """Test that TYPE_CHECKING usage is flagged."""
    assert len(validate_content("if TYPE_CHECKING:")) == 1
    assert (
        len(validate_content("from typing import TYPE_CHECKING\nif TYPE_CHECKING:"))
        == 1
    )


def test_validate_content_allowed():
    """Test that allowed content passes validation."""
    assert len(validate_content("except ValueError:")) == 0
    assert len(validate_content("except KeyError:")) == 0
    assert len(validate_content("def foo(): pass")) == 0
    assert len(validate_content("")) == 0
