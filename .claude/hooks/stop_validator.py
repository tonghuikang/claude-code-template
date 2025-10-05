"""
Claude Code Hook: Stop Validator.

Validates that edits are followed by tests and include confirmation phrase.
"""

import json

PHRASE_TO_CHECK = "I have addressed every query from the user."

CHECKING_INSTRUCTIONS = f"""
Review your work.

You will

1) Enumerate over every requirement from the user
    - State the requirement
    - Cite the user instruction
    - Reason whether you have addressed the requirement

If you have made edits, you will ALSO

1) Run tests
    - Search for appropriate tests,
    - Read up how to run the test.
    - Run the test.
2) Run the formatter
    - See CLAUDE.md for instructions

When done without errors, end your reply with `{PHRASE_TO_CHECK}`.
"""

BASH_AFTER_EDIT_REMINDER = "It seems that you did not run bash after your last edit."


def validate_stop(transcript_path: str) -> list[str]:
    """Validate that edits are followed by bash commands and include confirmation phrase."""
    issues = []

    with open(transcript_path) as f:
        lines = f.readlines()
        has_edits = False
        ran_bash_after_edit = False
        for line in lines[::-1]:  # from the last message
            transcript = json.loads(line)
            if transcript["type"] == "assistant":
                for content in transcript["message"]["content"]:
                    if content["type"] == "tool_use":
                        if content["name"] in ("Edit", "Write"):
                            has_edits = True
                        if content["name"] == "Bash":
                            ran_bash_after_edit = True
            if has_edits:
                break

        if has_edits and not ran_bash_after_edit:
            issues.append(CHECKING_INSTRUCTIONS)
            issues.append(BASH_AFTER_EDIT_REMINDER)
            return issues

        if has_edits:
            # check for phrase_to_check
            for line in lines[::-1][:1]:  # check only the last message
                transcript = json.loads(line)
                if transcript["type"] == "assistant":
                    for content in transcript["message"]["content"]:
                        if "text" in content:
                            assistant_message = content["text"]
                            if PHRASE_TO_CHECK in assistant_message:
                                return []
                    issues.append(CHECKING_INSTRUCTIONS)

    return issues
