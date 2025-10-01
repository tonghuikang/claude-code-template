"""

Claude Code Hook: Edit Content Validator.

Edited from
https://github.com/anthropics/claude-code/blob/afb0fc9156254b5d38e0533274b5e3d1cb305d65/examples/hooks/bash_command_validator_example.py

"""

import json
import sys


def _validate_content(content: str) -> list[str]:
    issues = []

    if "except Exception" in content:
        issues.append("Please consider catching a more specific exception.")

    if "if TYPE_CHECKING:" in content:
        # note the closing double inverted comma
        issues.append("Could you avoid using `if TYPE_CHECKING`?")

    return issues


def main():
    """Validate bash commands from Claude Code hooks."""
    # https://docs.claude.com/en/docs/claude-code/hooks#posttooluse-input

    input_data = None
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        # Exit code 1 shows stderr to the user but not to Claude
        sys.exit(1)

    content = None

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name == "Edit":
        content = tool_input.get("new_string", "")
    elif tool_name == "Write":
        content = tool_input.get("content", "")
    else:
        sys.exit(0)

    if content is None:
        return

    issues = _validate_content(content)
    if issues:
        for message in issues:
            print(f"• {message}", file=sys.stderr)
        # Shows stderr to Claude (tool already ran)
        # https://docs.claude.com/en/docs/claude-code/hooks#exit-code-2-behavior
        sys.exit(2)


if __name__ == "__main__":
    main()
