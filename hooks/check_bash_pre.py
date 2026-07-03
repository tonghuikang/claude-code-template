"""
Shared Hook Logic: Bash Command Checks (PreToolUse).

Returns advisory issues for a bash command before it runs.
"""


def check_bash_pre(command: str) -> list[str]:
    """Check a bash command before it runs."""
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
        issues.append(
            "Please use --accelerator explicitly. Even if enable_gpu: true is true, you need to specify NvidiaRtxPro6000."
        )

    return issues
