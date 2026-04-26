"""
Claude Code Hook: Pre-Bash Command Validator.

Validates bash commands before execution.
"""


def validate_pre_bash_command(command: str) -> list[str]:
    """Validate bash command before execution."""
    issues = []

    if command.startswith("python"):
        issues.append("Please use `uv run python ...`")

    return issues
