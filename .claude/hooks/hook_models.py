"""
Dataclass models for Claude Code hook input structures.

Defines type-safe models for hook events and tool inputs. Plain dataclasses
(not pydantic) keep hook startup fast -- process_hooks runs on every tool call,
so the pydantic import tax is not worth paying here.
"""

from dataclasses import dataclass, fields
from typing import Any, Self


class _FromDict:
    """Build a model from a hook payload, ignoring unknown keys.

    Claude sends more fields than we model (cwd, permission_mode, ...); dropping
    the extras matches pydantic v2's default `extra='ignore'` behavior. A missing
    required field raises TypeError.
    """

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        known = {f.name for f in fields(cls)}  # type: ignore[arg-type]
        return cls(**{key: value for key, value in data.items() if key in known})


@dataclass(kw_only=True)
class BashToolInput(_FromDict):
    # https://code.claude.com/docs/en/hooks#pretooluse-input
    command: str
    timeout: int | None = None
    run_in_background: bool = False


@dataclass(kw_only=True)
class EditToolInput(_FromDict):
    # https://platform.claude.com/docs/en/api/agent-sdk/python#edit
    old_string: str
    new_string: str
    file_path: str


@dataclass(kw_only=True)
class WriteToolInput(_FromDict):
    # https://platform.claude.com/docs/en/api/agent-sdk/python#write
    content: str
    file_path: str


@dataclass(kw_only=True)
class WebFetchToolInput(_FromDict):
    # https://platform.claude.com/docs/en/api/agent-sdk/python#webfetch
    url: str
    prompt: str = ""


# Hook lifecycle: UserPromptSubmit -> PreToolUse -> Notification -> PostToolUse -> Stop


@dataclass(kw_only=True)
class GenericHook(_FromDict):
    # https://code.claude.com/docs/en/hooks#hook-input-and-output
    hook_event_name: str
    session_id: str = ""
    transcript_path: str = ""


@dataclass(kw_only=True)
class UserPromptSubmitHook(GenericHook):
    # https://code.claude.com/docs/en/hooks#userpromptsubmit
    prompt: str


@dataclass(kw_only=True)
class PreToolUseHook(GenericHook):
    # https://code.claude.com/docs/en/hooks#pretooluse
    tool_name: str
    tool_input: dict


@dataclass(kw_only=True)
class NotificationHook(GenericHook):
    # https://code.claude.com/docs/en/hooks#notification
    message: str = ""


@dataclass(kw_only=True)
class PostToolUseHook(GenericHook):
    # https://code.claude.com/docs/en/hooks#posttooluse
    tool_name: str
    tool_input: dict


@dataclass(kw_only=True)
class StopHook(GenericHook):
    # https://code.claude.com/docs/en/hooks#stop
    last_assistant_message: str = ""
    stop_hook_active: bool = False
