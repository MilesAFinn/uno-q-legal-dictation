from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    mode: str
    language: str
    alsa_device: str
    sample_rate: int
    whisper_cli: str
    whisper_model: Path | None
    speech_phrases_file: Path

    @classmethod
    def from_environment(cls, mode: str | None = None) -> "Settings":
        selected_mode = (mode or os.getenv("DICTATION_MODE", "local")).lower()
        if selected_mode not in {"local", "azure"}:
            raise ValueError("DICTATION_MODE must be 'local' or 'azure'")

        app_root = Path(__file__).resolve().parents[2]
        model = os.getenv(
            "WHISPER_MODEL", str(app_root / "vendor/models/ggml-tiny.en.bin")
        )
        return cls(
            mode=selected_mode,
            language=os.getenv("SPEECH_LANGUAGE", "en-US"),
            alsa_device=os.getenv("ALSA_DEVICE", "default"),
            sample_rate=int(os.getenv("SAMPLE_RATE", "16000")),
            whisper_cli=os.getenv(
                "WHISPER_CLI", str(app_root / "vendor/bin/whisper-cli")
            ),
            whisper_model=Path(model).expanduser(),
            speech_phrases_file=Path(
                os.getenv(
                    "SPEECH_PHRASES_FILE",
                    str(app_root / "config" / "speech-phrases.txt"),
                )
            ).expanduser(),
        )
