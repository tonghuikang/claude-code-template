"""
Shared Hook Logic: Edit/Write Content Checks.

Returns advisory issues for content from Edit or Write operations.
"""


def check_edit(old_string: str, new_string: str, filepath: str) -> list[str]:
    """Check content from an Edit or Write operation."""
    issues = []

    if ".py" in filepath:
        if "except Exception" in new_string:
            issues.append("Please consider catching a more specific exception.")

        if "if TYPE_CHECKING:" in new_string:
            issues.append("Could you avoid using `if TYPE_CHECKING`?")

        if "Any" in new_string:
            issues.append("Could you use a more specific typing?")

    return issues
