"""
Claude Code Hook: Pre-Bash Command Validator.

Validates bash commands before execution.
"""


def validate_pre_bash_command(command: str) -> list[str]:
    """Validate bash command before execution."""
    issues = []

    if command.startswith("python"):
        issues.append("Please use `uv run python ...`")

    if command.startswith("kaggle"):
        issues.append("Please use `uv run kaggle ...`")

    if (
        "kaggle" in command
        and "adapter-validation" in command
        and "push" in command
        and "--accelerator" not in command
    ):
        issues.append("Please use --accelerator explicitly. Even if enable_gpu: true is true, you need to specify NvidiaRtxPro6000.")

    return issues
