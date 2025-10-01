from unittest import mock

import pytest

from bash_validator import _validate_command, main


def test__validate_command():
    # grep check
    assert len(_validate_command("grep")) == 1
    assert len(_validate_command("ls")) == 0  # No issues

    # Commands with && should be flagged
    assert len(_validate_command("pwd && cat CLAUDE.md")) == 1
    assert len(_validate_command("git add . && git commit")) == 1


def test_main():
    # Test command that should produce alerts (grep)
    with mock.patch(
        "json.load",
        return_value={"tool_name": "Bash", "tool_input": {"command": "grep foo"}},
    ):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2

    # Test allowed command - should not raise SystemExit
    with mock.patch(
        "json.load",
        return_value={"tool_name": "Bash", "tool_input": {"command": "pwd"}},
    ):
        main()  # Should complete normally without raising

    # Test non-Bash tool
    with mock.patch("json.load", return_value={"tool_name": "Edit", "tool_input": {}}):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
