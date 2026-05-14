"""Speak a notification message via Kokoro TTS, played through `aplay`."""

from __future__ import annotations

import subprocess
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

SAMPLE_RATE = 24000


def _play_wav(path: Path) -> None:
    players = [
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


def main() -> None:
    message = " ".join(sys.argv[1:]).strip()
    if not message:
        return

    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device="cpu")
    chunks: list[np.ndarray] = []
    for _, _, audio in pipeline(message, voice="af_heart"):
        chunks.append(audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio))

    if not chunks:
        return

    waveform = np.concatenate(chunks)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fh:
        path = Path(fh.name)

    try:
        sf.write(str(path), waveform, SAMPLE_RATE)
        _play_wav(path)
    finally:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
