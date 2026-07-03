"""Codex hook dispatcher for Stop and Notification events.

Thin wrapper: parses Codex hook payloads and routes them to the shared
business logic in the repository-level hooks/ directory.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))

from hook_models import (  # noqa: E402
    GenericHook,
    NotificationHook,
    StopHook,
    parse_hook_payload,
)
from process_notification import process_notification  # noqa: E402
from process_stop import validate_stop  # noqa: E402


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
    process_notification(message)

    if hook.stop_hook_active:
        _emit(_hook_ok_response())
        return

    issues = validate_stop(hook.transcript_path)
    if issues:
        _emit(_hook_block_response(" ".join(issues)))
        return

    _emit(_hook_ok_response())


def _handle_notification_hook(hook: NotificationHook) -> None:
    if hook.message:
        process_notification(hook.message)


def load_hook_input() -> GenericHook | NotificationHook | StopHook:
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
    """Route hook events and emit Codex Stop hook response JSON."""
    hook_input = load_hook_input()
    try:
        if isinstance(hook_input, StopHook):
            _handle_stop_hook(hook_input)
            return
        if isinstance(hook_input, NotificationHook):
            _handle_notification_hook(hook_input)
            _emit(_hook_ok_response())
            return

        _emit(_hook_ok_response())
    except Exception as exc:  # defensive
        _debug_log(f"Unhandled exception: {type(exc).__name__}: {exc}")
        _emit(_hook_ok_response())


if __name__ == "__main__":
    main()
