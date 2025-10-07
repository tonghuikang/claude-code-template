"""
Claude Code Hook: Stop Validator.

Validates that edits are followed by tests and include confirmation phrase.
"""

import json

PHRASE_TO_CHECK = "I have addressed every query from the user."

CHECKING_INSTRUCTIONS = """
Review your work.

You will

1) Enumerate over every requirement from the user
    - State the requirement
    - Cite the user instruction
    - Add to the todo `TodoWrite` tool

2) Check whether the user instruction is followed
    - For each item in the todo list
    - Reason whether you have addressed the requirement

If you have made edits, you will ALSO

1) Run tests
    - Search for appropriate tests,
    - Read up how to run the test.
    - Run the test.
2) Run the formatter
    - See CLAUDE.md for instructions
"""

BASH_AFTER_EDIT_REMINDER = "It seems that you did not run bash after your last edit."

TODO_AFTER_EDIT_REMINDER = (
    "It seems that you did not use the TodoWrite tool after your last edit."
)


def validate_stop(transcript_path: str) -> list[str]:
    """Validate that edits are followed by bash commands and include confirmation phrase."""
    issues = []

    with open(transcript_path) as f:
        lines = f.readlines()
        has_edits = False
        ran_bash_after_edit = False
        use_todo_after_edit = False
        for line in lines[::-1]:  # from the last message
            transcript = json.loads(line)
            if transcript["type"] == "assistant":
                for content in transcript["message"]["content"]:
                    if content["type"] == "tool_use":
                        if content["name"] in ("Edit", "Write"):
                            has_edits = True
                        if content["name"] == "Bash":
                            ran_bash_after_edit = True
                        if content["name"] == "TodoWrite":
                            use_todo_after_edit = True
            if has_edits:
                break

        if has_edits:
            if (not ran_bash_after_edit) or (not use_todo_after_edit):
                issues.append(CHECKING_INSTRUCTIONS)
            if not ran_bash_after_edit:
                issues.append(BASH_AFTER_EDIT_REMINDER)
            if not use_todo_after_edit:
                issues.append(TODO_AFTER_EDIT_REMINDER)

    return issues
