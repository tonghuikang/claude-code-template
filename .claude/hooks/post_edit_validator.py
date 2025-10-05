"""
Claude Code Hook: Edit Content Validator.

Validates content from Edit or Write operations.
"""


def validate_content(content: str) -> list[str]:
    """Validate content from Edit or Write operations."""
    issues = []

    if "except Exception" in content:
        issues.append("Please consider catching a more specific exception.")

    if "if TYPE_CHECKING:" in content:
        # note the closing double inverted comma
        issues.append("Could you avoid using `if TYPE_CHECKING`?")

    return issues
