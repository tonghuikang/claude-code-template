# Repository template for Claude Code

On the Github page for this repository, "Use this template" on the top right.


# Init

You will need to init with `uv sync`. Just ask Claude how to do this.


# Example queries

You can test the Claude Code hooks on this repository itself.

`ruff`

This should trigger the `UserPromptSubmit` hook

`move if "grep" in command: from pre to post`

On attempting to stop after finishing the edit, this should trigger the instruction to test
