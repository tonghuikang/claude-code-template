"""
Claude Code Hook: Stop Validator.

Validates that edits are followed by tests and include confirmation phrase.
"""

import json

PHRASE_TO_CHECK = "I have addressed every query from the user."

CHECKING_INSTRUCTIONS = """
Review your work by invoking the check-deliverables skill:

Use the Skill tool with skill: "check-deliverables" to verify all deliverables have been met.
"""

BASH_AFTER_EDIT_REMINDER = (
    "It seems that you edited something, and did not run a bash function."
)


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

        # Always run check-deliverables on every query
        issues.append(CHECKING_INSTRUCTIONS)

        if has_edits:
            if not ran_bash_after_edit:
                issues.append(BASH_AFTER_EDIT_REMINDER)

    return issues
