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


class WebFetchToolInput(BaseModel):
    url: str
    prompt: str = ""


# Hook lifecycle: UserPromptSubmit -> PreToolUse -> Notification -> PostToolUse -> Stop


class GenericHook(BaseModel):
    # https://docs.claude.com/en/docs/claude-code/hooks#hook-input
    hook_event_name: str

    model_config = ConfigDict(extra="allow")


class UserPromptSubmitHook(GenericHook):
    # https://docs.claude.com/en/docs/claude-code/hooks#userpromptsubmit-input
    prompt: str


class PreToolUseHook(GenericHook):
    # https://docs.claude.com/en/docs/claude-code/hooks#pretooluse-input
    tool_name: str
    tool_input: dict


class NotificationHook(GenericHook):
    # https://docs.claude.com/en/docs/claude-code/hooks#notification-input
    message: str = ""


class PostToolUseHook(GenericHook):
    # https://docs.claude.com/en/docs/claude-code/hooks#posttooluse-input
    tool_name: str
    tool_input: dict


class StopHook(GenericHook):
    # https://docs.claude.com/en/docs/claude-code/hooks#stop-input
    last_assistant_message: str = ""
    transcript_path: str = ""
    stop_hook_active: bool = False
