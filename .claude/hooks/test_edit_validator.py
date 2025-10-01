from unittest import mock

import pytest

from edit_validator import _validate_content, main


def test__validate_content():
    # Content that should produce alerts
    assert len(_validate_content("except Exception:")) == 1
    assert len(_validate_content("if TYPE_CHECKING:")) == 1

    # Normal content should not produce alerts
    assert len(_validate_content("except ValueError:")) == 0
    assert len(_validate_content("def foo(): pass")) == 0
    assert len(_validate_content("")) == 0


def test_main():
    # Test Edit tool with content that should produce alerts
    with mock.patch(
        "json.load",
        return_value={
            "tool_name": "Edit",
            "tool_input": {"new_string": "except Exception:"},
        },
    ):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2

    # Test Write tool with content that should produce alerts
    with mock.patch(
        "json.load",
        return_value={
            "tool_name": "Write",
            "tool_input": {"content": "if TYPE_CHECKING:"},
        },
    ):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2

    # Test allowed content - should not raise SystemExit
    with mock.patch(
        "json.load",
        return_value={
            "tool_name": "Edit",
            "tool_input": {"new_string": "except ValueError:"},
        },
    ):
        main()  # Should complete normally without raising

    # Test non-Edit/Write tool
    with mock.patch("json.load", return_value={"tool_name": "Bash", "tool_input": {}}):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
