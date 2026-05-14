"""Codex Notification Speaker.

Plays notification messages using platform TTS:
- macOS: `say`
- Linux: `notify_kokoro.py` using Kokoro+`aplay`
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from sys import platform

NOTIFY_KOKORO = Path(__file__).with_name("notify_kokoro.py")


def process_notification(message: str) -> None:
    """Speak message using the platform-specific notification path."""
    if not message:
        return

    if platform == "darwin":
        cmd = ["say", message]
    elif platform.startswith("linux"):
        cmd = [sys.executable, str(NOTIFY_KOKORO), message]
    else:
        return

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
