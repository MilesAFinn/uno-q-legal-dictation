from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class AudioCaptureError(RuntimeError):
    pass


def list_capture_devices() -> str:
    """Return ALSA's list of available capture devices."""
    arecord = shutil.which("arecord")
    if not arecord:
        raise AudioCaptureError("arecord is not installed or is not on PATH")

    result = subprocess.run(
        [arecord, "-l"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AudioCaptureError(result.stderr.strip() or "Unable to list microphones")
    return result.stdout.strip()


def record_wav(
    destination: Path,
    *,
    seconds: int,
    device: str,
    sample_rate: int,
) -> None:
    """Capture mono, 16-bit PCM audio with ALSA."""
    if seconds <= 0:
        raise ValueError("Recording duration must be greater than zero")

    arecord = shutil.which("arecord")
    if not arecord:
        raise AudioCaptureError("arecord is not installed or is not on PATH")

    command = [
        arecord,
        "-q",
        "-D",
        device,
        "-f",
        "S16_LE",
        "-r",
        str(sample_rate),
        "-c",
        "1",
        "-d",
        str(seconds),
        "-t",
        "wav",
        str(destination),
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise AudioCaptureError(result.stderr.strip() or "Microphone recording failed")

