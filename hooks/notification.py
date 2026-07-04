"""
Shared Hook Logic: Notification Speaker.

Speaks notification messages via a Kokoro TTS subprocess on all platforms.
Dependency-free so it can run under the system python used by Codex; the
Kokoro subprocess itself runs under the project venv python.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

NOTIFY_KOKORO = Path(__file__).with_name("notify_kokoro.py")
NARRATE_FLAG = Path.home() / ".narrate_mute"
MUTE_SECONDS = 60 * 60  # `ssn` mutes narration for 1 hour


def _notification_python() -> str:
    project_python = Path(__file__).resolve().parents[1] / ".venv" / "bin" / "python3"
    if project_python.exists():
        return str(project_python)
    return sys.executable


def _narration_enabled() -> bool:
    """Read the mute-since timestamp from the home dir; default is to narrate."""
    try:
        mute_since = float(NARRATE_FLAG.read_text().strip())
    except (OSError, ValueError):
        return True
    return time.time() - mute_since >= MUTE_SECONDS


def speak(message: str) -> None:
    """Speak a notification message via a Kokoro TTS subprocess."""
    if not message or not _narration_enabled():
        return

    cmd = [_notification_python(), str(NOTIFY_KOKORO), message]

    try:
        subprocess.Popen(
            cmd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return
