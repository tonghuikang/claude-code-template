"""
Claude Code Hook: Centralized Hook Processing.

Thin wrapper: parses Claude Code hook payloads and routes them to the
shared business logic in the repository-level hooks/ directory.

Adapted from:
https://github.com/anthropics/claude-code/tree/main/examples/hooks

"""

import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))

from hook_models import (
    BashToolInput,
    EditToolInput,
    GenericHook,
    NotificationHook,
    PostToolUseHook,
    PreToolUseHook,
    StopHook,
    UserPromptSubmitHook,
    WebFetchToolInput,
    WriteToolInput,
)
from check_bash_post import check_bash_post
from check_bash_pre import check_bash_pre
from check_edit import check_edit
from check_prompt import check_prompt
from check_stop import check_stop
from check_webfetch import check_webfetch
from notification import speak

_HOOKS_BY_EVENT: dict[str, type[GenericHook]] = {
    "UserPromptSubmit": UserPromptSubmitHook,
    "PreToolUse": PreToolUseHook,
    "Notification": NotificationHook,
    "PostToolUse": PostToolUseHook,
    "Stop": StopHook,
}


def load_hook_input() -> GenericHook:
    """Load and parse JSON input from stdin into a typed hook model."""
    try:
        raw_data = json.load(sys.stdin)
        generic_hook = GenericHook.from_dict(raw_data)

        # Route to specific hook model based on hook_event_name
        hook_cls = _HOOKS_BY_EVENT.get(generic_hook.hook_event_name)
        if hook_cls is None:
            return generic_hook
        return hook_cls.from_dict(raw_data)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except (TypeError, AttributeError) as e:
        print(f"Error: Invalid hook input structure: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Route hook events to the appropriate checks."""
    # https://docs.claude.com/en/docs/claude-code/hooks#hook-input
    hook_input = load_hook_input()

    exit_zero_messages = []
    exit_one_messages = []
    exit_two_messages = []

    # Route to the appropriate check based on hook_event_name + tool_name
    # Hook lifecycle: UserPromptSubmit -> PreToolUse -> Notification -> PostToolUse -> Stop
    if isinstance(hook_input, UserPromptSubmitHook):
        print(asdict(hook_input))  # Original prompt_validator behavior
        if hook_input.prompt:
            exit_zero_messages = check_prompt(hook_input.prompt)

    elif isinstance(hook_input, PreToolUseHook):
        if hook_input.tool_name == "Bash":
            bash_input = BashToolInput.from_dict(hook_input.tool_input)
            exit_two_messages = check_bash_pre(bash_input.command)

        elif hook_input.tool_name == "WebFetch":
            webfetch_input = WebFetchToolInput.from_dict(hook_input.tool_input)
            if webfetch_input.url:
                exit_two_messages = check_webfetch(webfetch_input.url)

    elif isinstance(hook_input, NotificationHook):
        speak(hook_input.message)

    elif isinstance(hook_input, PostToolUseHook):
        if hook_input.tool_name == "Bash":
            bash_input = BashToolInput.from_dict(hook_input.tool_input)
            if bash_input.command:
                exit_two_messages = check_bash_post(bash_input.command)

        elif hook_input.tool_name == "Edit":
            edit_input = EditToolInput.from_dict(hook_input.tool_input)
            if edit_input.new_string or edit_input.file_path:
                exit_two_messages = check_edit(
                    edit_input.old_string, edit_input.new_string, edit_input.file_path
                )

        elif hook_input.tool_name == "Write":
            write_input = WriteToolInput.from_dict(hook_input.tool_input)
            if write_input.content or write_input.file_path:
                exit_two_messages = check_edit(
                    "", write_input.content, write_input.file_path
                )

    elif isinstance(hook_input, StopHook):
        if hook_input.stop_hook_active:
            sys.exit(0)
        if hook_input.transcript_path:
            exit_two_messages = check_stop(hook_input.transcript_path)
        speak(hook_input.last_assistant_message)

    # Handle exit codes and output
    for exit_zero_message in exit_zero_messages:
        # https://docs.claude.com/en/docs/claude-code/hooks#simple%3A-exit-code
        print(exit_zero_message, file=sys.stdout)

    for exit_one_message in exit_one_messages:
        # Exit code 1 shows stderr to the user but not to Claude
        print(exit_one_message, file=sys.stderr)

    for exit_two_message in exit_two_messages:
        # Exit code 2 shows stderr to Claude (tool already ran)
        # https://docs.claude.com/en/docs/claude-code/hooks#exit-code-2-behavior
        print(exit_two_message, file=sys.stderr)

    if exit_two_messages:
        sys.exit(2)
    if exit_one_messages:
        sys.exit(1)

    # No issues found
    sys.exit(0)


if __name__ == "__main__":
    main()
