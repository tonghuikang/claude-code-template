"""Codex Stop hook handler for the final assistant response."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from sys import platform


def _debug_log(message: str) -> None:
    """Append a tiny debug line for hook troubleshooting."""
    try:
        log_path = Path("/tmp/codex_stop_hook.log")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with log_path.open("a", encoding="utf-8") as fp:
            fp.write(f"[{timestamp}] {message}\n")
    except Exception:
        return


def _coerce_message_text(value: Any) -> str:
    """Convert a payload fragment into plain text."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            text = _coerce_message_text(item)
            if text:
                parts.append(text)
        return "".join(parts)
    if isinstance(value, dict):
        for key in ("text", "content", "message", "output"):
            if key in value and value[key] is not None:
                return _coerce_message_text(value[key])
    return ""


def _extract_assistant_message(record: dict[str, Any]) -> str:
    """Return assistant content from one transcript record, if present."""
    if not isinstance(record, dict):
        return ""

    message = record.get("message")
    if isinstance(message, dict):
        if message.get("role") == "assistant":
            return _coerce_message_text(message.get("content"))
        return ""

    if record.get("role") == "assistant":
        return _coerce_message_text(record.get("content"))

    return ""


def _resolve_transcript_path(raw_path: Any) -> str:
    """Resolve a transcript path against multiple likely bases."""
    if not isinstance(raw_path, str) or not raw_path.strip():
        return ""

    candidate = Path(raw_path)
    if candidate.is_file():
        return str(candidate)

    cwd_candidate = Path.cwd() / raw_path
    if cwd_candidate.is_file():
        return str(cwd_candidate)

    script_dir_candidate = Path(__file__).resolve().parent.parent / raw_path
    if script_dir_candidate.is_file():
        return str(script_dir_candidate)

    return ""


def _extract_last_message_in_records(records: Any) -> str:
    """Extract the last assistant message from transcript-like data."""
    if not isinstance(records, list):
        return ""

    message = ""
    for item in records:
        if isinstance(item, dict):
            candidate = _extract_assistant_message(item)
            if candidate:
                message = candidate
    return message


def _extract_last_assistant_message_from_transcript(transcript_path: str) -> str:
    """Return the last assistant message from a transcript file."""
    path = Path(transcript_path)
    if not path.is_file():
        return ""

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return ""

    # JSONL transcript format
    last_message = ""
    raw_lines = raw.splitlines()
    if len(raw_lines) > 1:
        for raw_line in raw_lines:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            message = _extract_assistant_message(record)
            if message:
                last_message = message
    else:
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                transcript = payload.get("transcript")
                if isinstance(transcript, list):
                    candidate = _extract_last_message_in_records(transcript)
                    if candidate:
                        return candidate
        except json.JSONDecodeError:
            pass

    return last_message


def _extract_message_from_payload(payload: dict[str, Any]) -> str:
    """Try multiple payload keys and transcript content shapes."""
    for key in (
        "last_assistant_message",
        "assistant_message",
        "final_message",
        "message",
        "output",
    ):
        text = _coerce_message_text(payload.get(key))
        if text:
            return text

    transcript_field = payload.get("transcript")
    if isinstance(transcript_field, str):
        resolved = _resolve_transcript_path(transcript_field)
        if resolved:
            candidate = _extract_last_assistant_message_from_transcript(resolved)
            if candidate:
                return candidate
    elif isinstance(transcript_field, list):
        message = _extract_last_message_in_records(transcript_field)
        if message:
            return message

    return ""


def _extract_transcript_path(payload: dict[str, Any]) -> str:
    """Resolve transcript path from common stop hook keys."""
    for key in ("transcript_path", "transcript_file", "session_transcript_path"):
        resolved = _resolve_transcript_path(payload.get(key))
        if resolved:
            return resolved

    # Nested metadata variants
    meta = payload.get("metadata")
    if isinstance(meta, dict):
        for key in ("transcript_path", "transcript_file", "session_transcript_path"):
            resolved = _resolve_transcript_path(meta.get(key))
            if resolved:
                return resolved

    return ""


def validate_stop(transcript_path: str) -> list[str]:
    """Validate the final stop transcript contents."""
    if not transcript_path:
        return []

    path = Path(transcript_path)
    if not path.is_file():
        return ["Missing transcript file for stop validation."]

    try:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ["Unable to read stop transcript file for validation."]

    assistant_messages: list[str] = []
    for raw_line in raw_lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        message = _extract_assistant_message(record)
        if message:
            assistant_messages.append(message)

    return []


def speak(message: str) -> None:
    """Speak notification text via OS TTS on macOS."""
    if platform != "darwin":
        return

    message = message.strip()
    if not message:
        return

    escaped = message.replace('"', r'\\"')
    commands = [
        ["/usr/bin/say", message],
        ["say", message],
        ["/usr/bin/osascript", "-e", f'say "{escaped}"'],
        ["/usr/bin/afplay", "/System/Library/Sounds/Ping.aiff"],
    ]

    for command in commands:
        try:
            subprocess.run(
                command,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )
            return
        except FileNotFoundError:
            continue


def _speak_if_needed(message: str) -> None:
    if message:
        speak(message)
    else:
        speak("Task complete.")


def _hook_ok_response() -> str:
    """Return a response format accepted by the Stop hook."""
    # Keep this intentionally minimal: continue indicates normal completion.
    return json.dumps({"continue": True})


def _hook_block_response(reason: str) -> str:
    return json.dumps({"decision": "block", "reason": reason})


def _emit(msg: str) -> None:
    sys.stdout.write(msg)
    sys.stdout.flush()


def _process_stop_main_logic() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        _debug_log(f"JSON decode failed: {exc}")
        _speak_if_needed("")
        _emit(_hook_ok_response())
        return
    except OSError as exc:
        _debug_log(f"Input read failed: {exc}")
        _speak_if_needed("")
        _emit(_hook_ok_response())
        return

    if not isinstance(hook_input, dict):
        _debug_log(f"Non-dict payload: {type(hook_input).__name__}")
        _emit(_hook_ok_response())
        return

    transcript_path = _extract_transcript_path(hook_input)
    message_for_speech = _extract_message_from_payload(hook_input)

    if not message_for_speech and transcript_path:
        from_transcript = _extract_last_assistant_message_from_transcript(transcript_path)
        if from_transcript:
            message_for_speech = from_transcript

    _speak_if_needed(message_for_speech)

    if hook_input.get("stop_hook_active"):
        _emit(_hook_ok_response())
        return

    issues = validate_stop(transcript_path)
    if issues:
        _emit(_hook_block_response(" ".join(issues)))
        return

    _emit(_hook_ok_response())


def main() -> None:
    _debug_log("hook_start")
    try:
        _process_stop_main_logic()
    except Exception as exc:
        _debug_log(f"main_unhandled: {type(exc).__name__}: {exc}")
        _speak_if_needed("")
        _emit(_hook_ok_response())


if __name__ == "__main__":
    main()
