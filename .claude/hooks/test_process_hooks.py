"""Tests for process_hooks.py."""

from io import StringIO
from unittest import mock

import pytest
from process_hooks import load_hook_input, main


# Tests for load_hook_input function
def test_load_hook_input_valid():
    """Test loading valid JSON input."""
    mock_stdin = StringIO('{"tool_name": "Bash", "hook_event_name": "PreToolUse"}')
    with mock.patch("sys.stdin", mock_stdin):
        result = load_hook_input()
        assert result["tool_name"] == "Bash"
        assert result["hook_event_name"] == "PreToolUse"


def test_load_hook_input_invalid():
    """Test loading invalid JSON input."""
    mock_stdin = StringIO("invalid json")
    with mock.patch("sys.stdin", mock_stdin):
        with pytest.raises(SystemExit) as exc:
            load_hook_input()
        assert exc.value.code == 1


# Tests for UserPromptSubmit hook
def test_main_user_prompt_submit():
    """Test routing to user prompt validator."""
    with mock.patch(
        "process_hooks.load_hook_input",
        return_value={
            "hook_event_name": "UserPromptSubmit",
            "tool_name": "",
            "tool_input": {},
            "prompt": "run ruff on my code",
        },
    ):
        with mock.patch(
            "process_hooks.validate_user_prompt", return_value=["Refer to CLAUDE.md"]
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with("run ruff on my code")
            assert exc.value.code == 0


# Tests for PreToolUse hooks
def test_main_pre_bash():
    """Test routing to pre-bash validator."""
    with mock.patch(
        "process_hooks.load_hook_input",
        return_value={
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python test.py"},
        },
    ):
        with mock.patch(
            "process_hooks.validate_before_execution", return_value=["Use uv run"]
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with("python test.py")
            assert exc.value.code == 2


# Tests for PostToolUse hooks
def test_main_post_bash():
    """Test routing to post-bash validator."""
    with mock.patch(
        "process_hooks.load_hook_input",
        return_value={
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "grep foo"},
        },
    ):
        with mock.patch(
            "process_hooks.validate_bash_command", return_value=["Use Grep tool"]
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with("grep foo")
            assert exc.value.code == 2


def test_main_post_edit():
    """Test routing to post-edit validator."""
    with mock.patch(
        "process_hooks.load_hook_input",
        return_value={
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_input": {
                "old_string": "old code",
                "new_string": "except Exception: pass",
                "file_path": "test.py",
            },
        },
    ):
        with mock.patch(
            "process_hooks.validate_edit_content",
            return_value=["Catch specific exception"],
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with(
                "old code", "except Exception: pass", "test.py"
            )
            assert exc.value.code == 2


def test_main_post_write():
    """Test routing to post-write validator."""
    with mock.patch(
        "process_hooks.load_hook_input",
        return_value={
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
            "tool_input": {"content": "if TYPE_CHECKING:", "file_path": "test.py"},
        },
    ):
        with mock.patch(
            "process_hooks.validate_edit_content", return_value=["Avoid TYPE_CHECKING"]
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with("", "if TYPE_CHECKING:", "test.py")
            assert exc.value.code == 2


# Tests for Stop hook
def test_main_stop():
    """Test routing to stop validator."""
    with mock.patch(
        "process_hooks.load_hook_input",
        return_value={
            "hook_event_name": "Stop",
            "tool_name": "",
            "tool_input": {},
            "transcript_path": "/tmp/transcript.jsonl",
        },
    ):
        with mock.patch(
            "process_hooks.validate_stop", return_value=["Review your work"]
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with("/tmp/transcript.jsonl")
            assert exc.value.code == 2


# Edge case tests
def test_main_no_issues():
    """Test that no issues results in clean exit."""
    with mock.patch(
        "process_hooks.load_hook_input",
        return_value={
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "pwd"},
        },
    ):
        with mock.patch("process_hooks.validate_bash_command", return_value=[]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0


def test_main_empty_command():
    """Test handling of empty command."""
    with mock.patch(
        "process_hooks.load_hook_input",
        return_value={
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": ""},
        },
    ):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0


def test_main_unknown_hook():
    """Test handling of unknown hook events."""
    with mock.patch(
        "process_hooks.load_hook_input",
        return_value={
            "hook_event_name": "UnknownEvent",
            "tool_name": "UnknownTool",
            "tool_input": {},
        },
    ):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
