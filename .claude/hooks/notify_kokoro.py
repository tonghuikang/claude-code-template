"""Speak a notification message via Kokoro TTS, played through `aplay`."""

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

SAMPLE_RATE = 24000


def main() -> None:
    message = " ".join(sys.argv[1:]).strip()
    if not message:
        return
    pipeline = KPipeline(lang_code="a")
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
        subprocess.run(["aplay", "-q", str(path)], check=False)
    finally:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
