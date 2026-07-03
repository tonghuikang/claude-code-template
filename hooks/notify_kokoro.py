"""Speak a notification message via Kokoro TTS, played through the platform's audio player.

Loading torch + the Kokoro model costs ~5s, so a one-shot process pays that on
every notification. Instead, the first invocation spawns a daemon that keeps
the model in memory and listens on a Unix socket; later invocations just
forward their message to it (<0.2s). The daemon exits after IDLE_TIMEOUT of
no messages to release the ~500MB of resident memory.
"""

import os
import socket
import subprocess
import shutil
import sys
import tempfile
import time
import warnings
from pathlib import Path

SAMPLE_RATE = 24000
SOCKET_PATH = Path(tempfile.gettempdir()) / f"notify_kokoro-{os.getuid()}.sock"
IDLE_TIMEOUT = 30 * 60  # seconds without a message before the daemon exits
SPAWN_WAIT = 60  # seconds to wait for a freshly spawned daemon to come up


def _play_wav(path: Path) -> None:
    players = [
        ["afplay", str(path)],
        ["pw-play", str(path)],
        ["aplay", "-q", str(path)],
    ]
    for cmd in players:
        if not shutil.which(cmd[0]):
            continue
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return


def _send(message: str) -> bool:
    """Deliver a message to a running daemon; False if none is listening."""
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(SOCKET_PATH))
            client.sendall(message.encode("utf-8"))
        return True
    except OSError:
        return False


def notify(message: str) -> None:
    """Forward the message to the daemon, spawning it on first use."""
    if _send(message):
        return

    subprocess.Popen(
        [sys.executable, __file__, "--daemon"],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )

    deadline = time.time() + SPAWN_WAIT
    while time.time() < deadline:
        if _send(message):
            return
        time.sleep(0.2)


def daemon() -> None:
    """Load the Kokoro model once and speak messages until idle."""
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        server.bind(str(SOCKET_PATH))
    except OSError:
        if _send(""):  # another daemon is alive and will handle messages
            return
        SOCKET_PATH.unlink(missing_ok=True)  # stale socket from a dead daemon
        server.bind(str(SOCKET_PATH))
    server.listen()
    server.settimeout(IDLE_TIMEOUT)

    import numpy as np
    from kokoro import KPipeline

    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device="cpu")

    try:
        while True:
            try:
                conn, _ = server.accept()
            except TimeoutError:
                return
            with conn:
                data = b""
                while chunk := conn.recv(4096):
                    data += chunk
            message = data.decode("utf-8", errors="replace").strip()
            if not message:
                continue
            chunks = [
                audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio)
                for _, _, audio in pipeline(message, voice="af_heart")
            ]
            if chunks:
                _speak_waveform(np.concatenate(chunks))
    finally:
        server.close()
        SOCKET_PATH.unlink(missing_ok=True)


def _speak_waveform(waveform) -> None:
    import soundfile as sf

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fh:
        path = Path(fh.name)
    try:
        sf.write(str(path), waveform, SAMPLE_RATE)
        _play_wav(path)
    finally:
        path.unlink(missing_ok=True)


def main() -> None:
    # Torch emits harmless UserWarning/FutureWarning noise when Kokoro builds
    # its model; nothing here is actionable for a TTS subprocess.
    warnings.simplefilter("ignore")
    if "--daemon" in sys.argv[1:]:
        daemon()
        return
    message = " ".join(arg for arg in sys.argv[1:] if arg != "--daemon").strip()
    if message:
        notify(message)


if __name__ == "__main__":
    main()
