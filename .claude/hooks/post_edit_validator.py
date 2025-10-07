"""
Claude Code Hook: Edit Content Validator.

Validates content from Edit or Write operations.
"""


def validate_content(content: str, filepath: str) -> list[str]:
    """Validate content from Edit or Write operations."""
    issues = []

    if "except Exception" in content and ".py" in filepath:
        issues.append("Please consider catching a more specific exception.")

    if "if TYPE_CHECKING:" in content and ".py" in filepath:
        # note the closing double inverted comma
        issues.append("Could you avoid using `if TYPE_CHECKING`?")

    if "Any" in content and ".py" in filepath:
        # note the closing double inverted comma
        issues.append("Could you use a more specific typing?")

    return issues
