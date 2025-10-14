"""
Claude Code Hook: Post-Bash Command Validator.

Validates bash commands after execution.
"""


def validate_bash_command(command: str) -> list[str]:
    """Validate bash command after execution."""
    issues = []

    if " && " in command:
        issues.append("Please try to run the commands individually.")

    return issues
