"""

Claude Code Hook: Bash Command Validator.

Obtained from
https://github.com/anthropics/claude-code/blob/afb0fc9156254b5d38e0533274b5e3d1cb305d65/examples/hooks/bash_command_validator_example.py

"""

import json
import sys


def _validate_command(command: str) -> list[str]:
    issues = []

    if " && " in command:
        issues.append("Please try to run the commands individually.")

    if "grep" in command:
        issues.append("Please use the Grep tool.")

    return issues


def main():
    """Validate bash commands from Claude Code hooks."""
    input_data = None
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        # Exit code 1 shows stderr to the user but not to Claude
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    issues = _validate_command(command)
    if issues:
        for message in issues:
            print(f"• {message}", file=sys.stderr)
        # Shows stderr to Claude (tool already ran)
        # https://docs.claude.com/en/docs/claude-code/hooks#exit-code-2-behavior
        sys.exit(2)


if __name__ == "__main__":
    main()
