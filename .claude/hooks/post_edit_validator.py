"""
Claude Code Hook: Edit Content Validator.

Validates content from Edit or Write operations.
"""


def validate_edit_content(old_string: str, new_string: str, filepath: str) -> list[str]:
    """Validate content from Edit or Write operations."""
    issues = []

    if ".py" in filepath:

        if "except Exception" in new_string:
            issues.append("Please consider catching a more specific exception.")

        if "if TYPE_CHECKING:" in new_string:
            issues.append("Could you avoid using `if TYPE_CHECKING`?")

        if new_string.count("#") > old_string.count("#") + 100:
            issues.append("Please check that your new comments are necessary.")

        if "Any" in new_string:
            issues.append("Could you use a more specific typing?")

    return issues
