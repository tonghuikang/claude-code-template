"""Tests for check_edit.py."""

from check_edit import check_edit


def test_check_edit_exception():
    """Test that broad exception catching is flagged."""
    assert len(check_edit("", "except Exception:", "test.py")) == 1
    assert len(check_edit("", "try: pass\nexcept Exception: pass", "test.py")) == 1


def test_check_edit_type_checking():
    """Test that TYPE_CHECKING usage is flagged."""
    assert len(check_edit("", "if TYPE_CHECKING:", "test.py")) == 1
    assert (
        len(
            check_edit(
                "", "from typing import TYPE_CHECKING\nif TYPE_CHECKING:", "test.py"
            )
        )
        == 1
    )


def test_check_edit_allowed():
    """Test that allowed content passes validation."""
    assert len(check_edit("", "except ValueError:", "test.py")) == 0
    assert len(check_edit("", "except KeyError:", "test.py")) == 0
    assert len(check_edit("", "def foo(): pass", "test.py")) == 0
    assert len(check_edit("", "", "test.py")) == 0
