from __future__ import annotations

import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from main import validate_local_wav


class AudioFileTests(unittest.TestCase):
    def write_wav(self, path: Path, *, channels: int, width: int, rate: int) -> None:
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(width)
            wav_file.setframerate(rate)
            wav_file.writeframes(b"\x00" * channels * width * 160)

    def test_accepts_whisper_compatible_wav(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audio_file = Path(directory) / "input.wav"
            self.write_wav(audio_file, channels=1, width=2, rate=16000)
            validate_local_wav(audio_file)

    def test_rejects_wrong_sample_rate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audio_file = Path(directory) / "input.wav"
            self.write_wav(audio_file, channels=1, width=2, rate=44100)
            with self.assertRaisesRegex(ValueError, "16 kHz"):
                validate_local_wav(audio_file)


if __name__ == "__main__":
    unittest.main()
