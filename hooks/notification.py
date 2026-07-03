"""
Shared Hook Logic: Notification Speaker.

Speaks notification messages via a Kokoro TTS subprocess on all platforms.
Dependency-free so it can run under the system python used by Codex; the
Kokoro subprocess itself runs under the project venv python.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

NOTIFY_KOKORO = Path(__file__).with_name("notify_kokoro.py")


def _notification_python() -> str:
    project_python = Path(__file__).resolve().parents[1] / ".venv" / "bin" / "python3"
    if project_python.exists():
        return str(project_python)
    return sys.executable


def speak(message: str) -> None:
    """Speak a notification message via a Kokoro TTS subprocess."""
    if not message:
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
