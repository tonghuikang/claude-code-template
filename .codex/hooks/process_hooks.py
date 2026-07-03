"""Codex hook dispatcher.

Thin wrapper: parses Codex hook payloads and routes them to the shared
business logic in the repository-level hooks/ directory.

Codex accepts two response protocols; this dispatcher uses both:
- Stop emits JSON ({"continue": true} / {"decision": "block", ...}).
- Tool and prompt events use exit codes like the Claude Code dispatcher
  (exit 2 + stderr blocks; exit 0 with no output allows).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))

from hook_models import (
    GenericHook,
    NotificationHook,
    PostToolUseHook,
    PreToolUseHook,
    StopHook,
    UserPromptSubmitHook,
    parse_hook_payload,
)
from check_bash_post import check_bash_post
from check_bash_pre import check_bash_pre
from check_edit import check_edit
from check_prompt import check_prompt
from check_stop import check_stop
from notification import speak


def _debug_log(message: str) -> None:
    """Append debug output used for hook troubleshooting."""
    try:
        from pathlib import Path
        import time

        log_path = Path("/tmp/codex_stop_hook.log")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with log_path.open("a", encoding="utf-8") as fp:
            fp.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def _emit(msg: str) -> None:
    sys.stdout.write(msg)
    sys.stdout.flush()


def _hook_ok_response() -> str:
    """Continue normal execution for the Stop hook."""
    return json.dumps({"continue": True})


def _hook_block_response(reason: str) -> str:
    """Ask Codex to block continuation with a reason."""
    return json.dumps({"decision": "block", "reason": reason})


def _message_text(raw_message: Any) -> str:
    if isinstance(raw_message, str):
        return raw_message.strip()
    return ""


def _handle_stop_hook(hook: StopHook) -> None:
    message = _message_text(hook.last_assistant_message) or "Task complete."
    speak(message)

    if hook.stop_hook_active:
        _emit(_hook_ok_response())
        return

    issues = check_stop(hook.transcript_path, hook.last_assistant_message)
    if issues:
        _emit(_hook_block_response(" ".join(issues)))
        return

    _emit(_hook_ok_response())


def _handle_notification_hook(hook: NotificationHook) -> None:
    if hook.message:
        speak(hook.message)


def _exit_two(issues: list[str]) -> None:
    """Block the tool call: exit 2 with the issues on stderr (shown to the model)."""
    for issue in issues:
        print(issue, file=sys.stderr)
    sys.exit(2)


def _handle_user_prompt_hook(hook: UserPromptSubmitHook) -> None:
    messages = check_prompt(hook.prompt) if hook.prompt else []
    if messages:
        _emit(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": "\n".join(messages),
                    }
                }
            )
        )


def _handle_pre_tool_use_hook(hook: PreToolUseHook) -> None:
    if hook.tool_name == "Bash":
        command = _message_text(hook.tool_input.get("command"))
        if command:
            issues = check_bash_pre(command)
            if issues:
                _exit_two(issues)


_PATCH_FILE_HEADER = re.compile(
    r"^[*]{3} (?:Add|Update|Delete) File: (.+)$", re.MULTILINE
)


def _edit_fields(tool_name: str, tool_input: dict[str, Any]) -> tuple[str, str, str]:
    """Normalize Edit/Write/apply_patch payloads to (old, new, file_path)."""
    if tool_name == "Edit":
        return (
            _message_text(tool_input.get("old_string")),
            _message_text(tool_input.get("new_string")),
            _message_text(tool_input.get("file_path")),
        )
    if tool_name == "Write":
        return (
            "",
            _message_text(tool_input.get("content")),
            _message_text(tool_input.get("file_path")),
        )
    # apply_patch: the patch text carries both content and file names
    patch = _message_text(tool_input.get("patch") or tool_input.get("input"))
    file_paths = " ".join(_PATCH_FILE_HEADER.findall(patch))
    return "", patch, file_paths


def _handle_post_tool_use_hook(hook: PostToolUseHook) -> None:
    if hook.tool_name == "Bash":
        command = _message_text(hook.tool_input.get("command"))
        if command:
            issues = check_bash_post(command)
            if issues:
                _exit_two(issues)
    elif hook.tool_name in ("Edit", "Write", "apply_patch"):
        old_string, new_string, file_path = _edit_fields(
            hook.tool_name, hook.tool_input
        )
        if new_string or file_path:
            issues = check_edit(old_string, new_string, file_path)
            if issues:
                _exit_two(issues)


def load_hook_input() -> (
    GenericHook
    | NotificationHook
    | StopHook
    | UserPromptSubmitHook
    | PreToolUseHook
    | PostToolUseHook
):
    """Load and parse JSON input from stdin."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        _debug_log(f"JSON decode failed: {exc}")
        return GenericHook.from_payload({})
    except OSError as exc:
        _debug_log(f"Input read failed: {exc}")
        return GenericHook.from_payload({})
    except Exception as exc:
        _debug_log(f"Hook input read failed: {type(exc).__name__}: {exc}")
        return GenericHook.from_payload({})

    return parse_hook_payload(payload)


def main() -> None:
    """Route hook events to the appropriate checks."""
    hook_input = load_hook_input()
    try:
        if isinstance(hook_input, StopHook):
            _handle_stop_hook(hook_input)
        elif isinstance(hook_input, NotificationHook):
            _handle_notification_hook(hook_input)
            _emit(_hook_ok_response())
        elif isinstance(hook_input, UserPromptSubmitHook):
            _handle_user_prompt_hook(hook_input)
        elif isinstance(hook_input, PreToolUseHook):
            _handle_pre_tool_use_hook(hook_input)
        elif isinstance(hook_input, PostToolUseHook):
            _handle_post_tool_use_hook(hook_input)
        # Unknown events: exit 0 with no output (default allow)
    except SystemExit:
        raise
    except Exception as exc:  # defensive: never break the agent loop
        _debug_log(f"Unhandled exception: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
