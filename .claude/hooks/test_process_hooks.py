"""Tests for process_hooks.py."""

from io import StringIO
from unittest import mock

import pytest
from hook_models import (
    GenericHook,
    NotificationHook,
    PostToolUseHook,
    PreToolUseHook,
    StopHook,
    UserPromptSubmitHook,
)
from process_hooks import load_hook_input, main


# Tests for load_hook_input function
def test_load_hook_input_valid_pre_tool_use():
    """Test loading valid JSON input returns PreToolUseHook."""
    mock_stdin = StringIO(
        '{"tool_name": "Bash", "hook_event_name": "PreToolUse", "tool_input": {}}'
    )
    with mock.patch("sys.stdin", mock_stdin):
        result = load_hook_input()
        assert isinstance(result, PreToolUseHook)
        assert result.tool_name == "Bash"
        assert result.hook_event_name == "PreToolUse"


def test_load_hook_input_valid_generic():
    """Test loading unknown hook event returns GenericHook."""
    mock_stdin = StringIO('{"hook_event_name": "UnknownEvent"}')
    with mock.patch("sys.stdin", mock_stdin):
        result = load_hook_input()
        assert isinstance(result, GenericHook)


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
    hook = UserPromptSubmitHook(
        hook_event_name="UserPromptSubmit",
        prompt="run ruff on my code",
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
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
    hook = PreToolUseHook(
        hook_event_name="PreToolUse",
        tool_name="Bash",
        tool_input={"command": "python test.py"},
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
        with mock.patch(
            "process_hooks.validate_pre_bash_command", return_value=["Use uv run"]
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with("python test.py")
            assert exc.value.code == 2


# Tests for PostToolUse hooks
def test_main_post_bash():
    """Test routing to post-bash validator."""
    hook = PostToolUseHook(
        hook_event_name="PostToolUse",
        tool_name="Bash",
        tool_input={"command": "grep foo"},
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
        with mock.patch(
            "process_hooks.validate_post_bash_command", return_value=["Use Grep tool"]
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with("grep foo")
            assert exc.value.code == 2


def test_main_post_edit():
    """Test routing to post-edit validator."""
    hook = PostToolUseHook(
        hook_event_name="PostToolUse",
        tool_name="Edit",
        tool_input={
            "old_string": "old code",
            "new_string": "except Exception: pass",
            "file_path": "test.py",
        },
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
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
    hook = PostToolUseHook(
        hook_event_name="PostToolUse",
        tool_name="Write",
        tool_input={"content": "if TYPE_CHECKING:", "file_path": "test.py"},
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
        with mock.patch(
            "process_hooks.validate_edit_content", return_value=["Avoid TYPE_CHECKING"]
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with("", "if TYPE_CHECKING:", "test.py")
            assert exc.value.code == 2


# Tests for Stop hook
def test_main_stop_validate():
    """Test routing to stop validator."""
    hook = StopHook(
        hook_event_name="Stop",
        transcript_path="/tmp/transcript.jsonl",
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
        with mock.patch(
            "process_hooks.validate_stop", return_value=["Review your work"]
        ) as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_called_once_with("/tmp/transcript.jsonl")
            assert exc.value.code == 2


def test_main_stop_hook_active_exits_early():
    """Test that stop_hook_active=True exits 0 without running validate_stop."""
    hook = StopHook(
        hook_event_name="Stop",
        transcript_path="/tmp/transcript.jsonl",
        stop_hook_active=True,
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
        with mock.patch("process_hooks.validate_stop") as mock_validator:
            with pytest.raises(SystemExit) as exc:
                main()
            mock_validator.assert_not_called()
            assert exc.value.code == 0


def test_main_stop_notification():
    """Test that Stop hook with CLAUDE_CODE_NOTIFY sends notification."""
    hook = StopHook(
        hook_event_name="Stop",
        last_assistant_message="Done with the task",
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
        with mock.patch.dict("os.environ", {"CLAUDE_CODE_NOTIFY": "simple"}):
            with mock.patch("process_hooks.subprocess.Popen") as mock_popen:
                with pytest.raises(SystemExit) as exc:
                    main()
                mock_popen.assert_called_once_with(
                    ["say", "Done with the task"],
                    start_new_session=True,
                )
                assert exc.value.code == 0


# Edge case tests
def test_main_no_issues():
    """Test that no issues results in clean exit."""
    hook = PostToolUseHook(
        hook_event_name="PostToolUse",
        tool_name="Bash",
        tool_input={"command": "pwd"},
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
        with mock.patch("process_hooks.validate_post_bash_command", return_value=[]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0


def test_main_empty_command():
    """Test handling of empty command."""
    hook = PreToolUseHook(
        hook_event_name="PreToolUse",
        tool_name="Bash",
        tool_input={"command": ""},
    )
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0


def test_main_unknown_hook():
    """Test handling of unknown hook events."""
    hook = GenericHook(hook_event_name="UnknownEvent")
    with mock.patch("process_hooks.load_hook_input", return_value=hook):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
