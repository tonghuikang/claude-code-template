"""
Claude Code Hook: Notification Speaker.

Speaks notification messages using the platform's TTS command.
"""

import subprocess
from sys import platform


def process_notification(message: str) -> None:
    """Speak a notification message via the platform's TTS command."""
    if not message:
        return
    if platform == "darwin":
        cmd = ["say", message]
    elif platform.startswith("linux"):
        cmd = ["spd-say", message]
    else:
        return
    subprocess.Popen(
        cmd,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )
