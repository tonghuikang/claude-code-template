"""
Claude Code Hook: Centralized Hook Processing.

Routes hook events to appropriate validators.

From:
https://github.com/anthropics/claude-code/tree/main/examples/hooks
"""

import json
import sys
import random
import time

from pydantic import ValidationError

from hook_models import BashToolInput, EditToolInput, WriteToolInput
from post_bash_validator import validate_bash_command
from post_edit_validator import validate_edit_content
from post_prompt_validator import validate_user_prompt
from pre_bash_validator import validate_before_execution
from stop_validator import validate_stop


def load_hook_input() -> dict:
    """Load and parse JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        # Exit code 1 shows stderr to the user but not to Claude
        sys.exit(1)


def main():
    """Route hook events to appropriate validators."""
    # https://docs.claude.com/en/docs/claude-code/hooks#hook-input
    input_data = load_hook_input()

    hook_event_name = input_data.get("hook_event_name", "")
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    exit_zero_messages = []
    exit_one_messages = []
    exit_two_messages = []

    # Route to appropriate validator based on hook_event_name + tool_name
    # Hook lifecycle: UserPromptSubmit -> PreToolUse -> PostToolUse -> Stop
    if hook_event_name == "UserPromptSubmit":
        prompt = input_data.get("prompt", "")
        exit_zero_messages = validate_user_prompt(prompt)

    elif hook_event_name == "PreToolUse" and tool_name == "Bash":
        try:
            bash_input = BashToolInput(**tool_input)
            exit_two_messages = validate_before_execution(bash_input.command)
        except ValidationError as e:
            exit_one_messages.append(f"Invalid Bash tool input: {e}")

    elif hook_event_name == "PostToolUse" and tool_name == "Edit":
        try:
            edit_input = EditToolInput(**tool_input)
            exit_two_messages = validate_edit_content(
                edit_input.old_string, edit_input.new_string, edit_input.file_path
            )
        except ValidationError as e:
            exit_one_messages.append(f"Invalid Edit tool input: {e}")

    elif hook_event_name == "PostToolUse" and tool_name == "Write":
        try:
            write_input = WriteToolInput(**tool_input)
            exit_two_messages = validate_edit_content(
                "", write_input.content, write_input.file_path
            )
        except ValidationError as e:
            exit_one_messages.append(f"Invalid Write tool input: {e}")

    elif hook_event_name == "PostToolUse" and tool_name == "Bash":
        try:
            bash_input = BashToolInput(**tool_input)
            exit_two_messages = validate_bash_command(bash_input.command)
        except ValidationError as e:
            exit_one_messages.append(f"Invalid Bash tool input: {e}")

    elif hook_event_name == "Stop":
        transcript_path = input_data.get("transcript_path", "")
        exit_two_messages = validate_stop(transcript_path)

    # Print messages
    for exit_zero_message in exit_zero_messages:
        # https://docs.claude.com/en/docs/claude-code/hooks#simple%3A-exit-code
        print(exit_zero_message, file=sys.stdout)

    for exit_one_message in exit_one_messages:
        print(exit_one_message, file=sys.stderr)

    for exit_two_message in exit_two_messages:
        # https://docs.claude.com/en/docs/claude-code/hooks#exit-code-2-behavior
        print(exit_two_message, file=sys.stderr)

    time.sleep(3 * random.random())

    # Handle validation results
    if exit_two_messages:
        # exit two should have a high priority than exit 1
        sys.exit(2)
    if exit_one_messages:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
