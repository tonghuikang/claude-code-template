"""
Claude Code Hook: Notification Speaker.

Speaks notification messages using the platform's TTS command.
On macOS this is `say`; on Linux it's a Kokoro TTS subprocess.
"""

import subprocess
import sys
from pathlib import Path
from sys import platform

NOTIFY_KOKORO = Path(__file__).with_name("notify_kokoro.py")


def _notification_python() -> str:
    project_python = Path(__file__).resolve().parents[2] / ".venv" / "bin" / "python3"
    if project_python.exists():
        return str(project_python)
    return sys.executable


def process_notification(message: str) -> None:
    """Speak a notification message via the platform's TTS command."""
    if not message:
        return
    if platform == "darwin":
        cmd = ["say", message]
    elif platform.startswith("linux"):
        cmd = [_notification_python(), str(NOTIFY_KOKORO), message]
    else:
        return
    subprocess.Popen(
        cmd,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )
