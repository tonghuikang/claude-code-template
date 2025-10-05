"""
Claude Code Hook: Centralized Hook Processing.

Routes hook events to appropriate validators.

From:
https://github.com/anthropics/claude-code/tree/main/examples/hooks
"""

import json
import sys

from post_bash_validator import validate_after_execution
from post_edit_validator import validate_content
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

    exit_one_messages = []
    exit_two_messages = []

    # Route to appropriate validator based on hook_event_name + tool_name
    # Hook lifecycle: UserPromptSubmit -> PreToolUse -> PostToolUse -> Stop
    if hook_event_name == "UserPromptSubmit":
        prompt = tool_input.get("prompt", "")
        if prompt:
            exit_one_messages = validate_user_prompt(prompt)

    elif hook_event_name == "PreToolUse" and tool_name == "Bash":
        command = tool_input.get("command", "")
        if command:
            exit_two_messages = validate_before_execution(command)

    elif hook_event_name == "PostToolUse" and tool_name == "Edit":
        content = tool_input.get("new_string", "")
        if content:
            exit_two_messages = validate_content(content)

    elif hook_event_name == "PostToolUse" and tool_name == "Write":
        content = tool_input.get("content", "")
        if content:
            exit_two_messages = validate_content(content)

    elif hook_event_name == "PostToolUse" and tool_name == "Bash":
        command = tool_input.get("command", "")
        if command:
            exit_two_messages = validate_after_execution(command)

    elif hook_event_name == "Stop":
        transcript_path = input_data.get("transcript_path", "")
        if transcript_path:
            exit_two_messages = validate_stop(transcript_path)

    for exit_one_message in exit_one_messages:
        print(exit_one_message, file=sys.stderr)

    for exit_two_message in exit_two_messages:
        print(exit_two_message, file=sys.stderr)

    # Handle validation results
    # https://docs.claude.com/en/docs/claude-code/hooks#exit-code-2-behavior
    if exit_two_messages:
        # exit two should have a high priority than exit 1
        sys.exit(2)
    if exit_one_messages:
        sys.exit(1)


if __name__ == "__main__":
    main()
