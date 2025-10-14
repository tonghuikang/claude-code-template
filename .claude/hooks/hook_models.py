"""
Pydantic models for Claude Code hook input structures.

Defines type-safe models for hook events and tool inputs.
"""

from pydantic import BaseModel, ConfigDict


class BashToolInput(BaseModel):
    # https://docs.claude.com/en/api/agent-sdk/python#bash
    command: str


class EditToolInput(BaseModel):
    # https://docs.claude.com/en/api/agent-sdk/python#edit
    old_string: str
    new_string: str
    file_path: str


class WriteToolInput(BaseModel):
    # https://docs.claude.com/en/api/agent-sdk/python#write
    content: str
    file_path: str


class UserPromptSubmitHook(BaseModel):
    # https://docs.claude.com/en/docs/claude-code/hooks#userpromptsubmit-input
    hook_event_name: str
    prompt: str

    model_config = ConfigDict(extra="allow")


class PostToolUseHook(BaseModel):
    # https://docs.claude.com/en/docs/claude-code/hooks#posttooluse-input
    hook_event_name: str
    tool_name: str
    tool_input: dict

    model_config = ConfigDict(extra="allow")


class GenericHook(BaseModel):
    # https://docs.claude.com/en/docs/claude-code/hooks#hook-input
    hook_event_name: str

    model_config = ConfigDict(extra="allow")
