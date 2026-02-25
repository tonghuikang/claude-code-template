"""
Claude Code Hook: Centralized Hook Processing.

Routes hook events to appropriate validators.

Adapted from:
https://github.com/anthropics/claude-code/tree/main/examples/hooks

"""

import json
import os
import subprocess
import sys

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
from post_bash_validator import validate_post_bash_command
from post_edit_validator import validate_edit_content
from post_prompt_validator import validate_user_prompt
from pre_bash_validator import validate_pre_bash_command
from pre_webfetch_validator import validate_webfetch_url
from pydantic import ValidationError
from stop_validator import validate_stop


def load_hook_input() -> GenericHook:
    """Load and parse JSON input from stdin using pydantic."""
    try:
        raw_data = json.load(sys.stdin)
        generic_hook = GenericHook(**raw_data)

        # Route to specific hook model based on hook_event_name
        if generic_hook.hook_event_name == "UserPromptSubmit":
            return UserPromptSubmitHook(**raw_data)
        elif generic_hook.hook_event_name == "PreToolUse":
            return PreToolUseHook(**raw_data)
        elif generic_hook.hook_event_name == "Notification":
            return NotificationHook(**raw_data)
        elif generic_hook.hook_event_name == "PostToolUse":
            return PostToolUseHook(**raw_data)
        elif generic_hook.hook_event_name == "Stop":
            return StopHook(**raw_data)
        else:
            return generic_hook

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print(f"Error: Invalid hook input structure: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Route hook events to appropriate validators."""
    # https://docs.claude.com/en/docs/claude-code/hooks#hook-input
    hook_input = load_hook_input()

    exit_zero_messages = []
    exit_one_messages = []
    exit_two_messages = []

    # Route to appropriate validator based on hook_event_name + tool_name
    # Hook lifecycle: UserPromptSubmit -> PreToolUse -> Notification -> PostToolUse -> Stop
    if isinstance(hook_input, UserPromptSubmitHook):
        print(hook_input.model_dump())  # Original prompt_validator behavior
        if hook_input.prompt:
            exit_zero_messages = validate_user_prompt(hook_input.prompt)

    elif isinstance(hook_input, PreToolUseHook):
        if hook_input.tool_name == "Bash":
            bash_input = BashToolInput(**hook_input.tool_input)
            exit_two_messages = validate_pre_bash_command(bash_input.command)

        elif hook_input.tool_name == "WebFetch":
            webfetch_input = WebFetchToolInput(**hook_input.tool_input)
            if webfetch_input.url:
                exit_two_messages = validate_webfetch_url(webfetch_input.url)

    elif isinstance(hook_input, NotificationHook):
        if os.environ.get("CLAUDE_CODE_NOTIFY") == "simple":
            message = hook_input.message
            if message:
                subprocess.Popen(
                    ["say", message],
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                )

    elif isinstance(hook_input, PostToolUseHook):
        if hook_input.tool_name == "Bash":
            bash_input = BashToolInput(**hook_input.tool_input)
            if bash_input.command:
                exit_two_messages = validate_post_bash_command(bash_input.command)

        elif hook_input.tool_name == "Edit":
            edit_input = EditToolInput(**hook_input.tool_input)
            if edit_input.new_string or edit_input.file_path:
                exit_two_messages = validate_edit_content(
                    edit_input.old_string, edit_input.new_string, edit_input.file_path
                )

        elif hook_input.tool_name == "Write":
            write_input = WriteToolInput(**hook_input.tool_input)
            if write_input.content or write_input.file_path:
                exit_two_messages = validate_edit_content(
                    "", write_input.content, write_input.file_path
                )

    elif isinstance(hook_input, StopHook):
        if hook_input.stop_hook_active:
            sys.exit(0)
        if hook_input.transcript_path:
            exit_two_messages = validate_stop(hook_input.transcript_path)
        if os.environ.get("CLAUDE_CODE_NOTIFY") == "simple":
            message = hook_input.last_assistant_message
            if message:
                subprocess.Popen(
                    ["say", message],
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                )

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
