"""
Claude Code Hook: User Prompt Validator.

Validates user prompts before processing.
"""


def validate_user_prompt(prompt: str) -> list[str]:
    """Validate user prompt content."""
    exit_zero_messages = []

    if "ruff" in prompt:
        exit_zero_messages.append("Refer to CLAUDE.md for ruff formatting instructions")

    return exit_zero_messages
