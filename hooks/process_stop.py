"""
Shared Hook Logic: Stop Validator.

Validates the final assistant transcript before the agent stops.
Dependency-free so it can run under the system python used by Codex.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
