from __future__ import annotations

import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from .config import Settings


class TranscriptionError(RuntimeError):
    pass


def load_phrase_hints(path: Path) -> list[str]:
    if not path.is_file():
        return []

    return [
        line
        for raw_line in path.read_text(encoding="utf-8").splitlines()
        if (line := raw_line.strip()) and not line.startswith("#")
    ]


class SpeechEngine(ABC):
    @abstractmethod
    def transcribe(self, audio_file: Path) -> str:
        """Return recognized text for a WAV file."""


class WhisperCppEngine(SpeechEngine):
    def __init__(self, settings: Settings) -> None:
        if settings.whisper_model is None:
            raise TranscriptionError(
                "Set WHISPER_MODEL to a whisper.cpp model file before using local mode"
            )
        self._cli = settings.whisper_cli
        self._model = settings.whisper_model

    def transcribe(self, audio_file: Path) -> str:
        if not self._model.is_file():
            raise TranscriptionError(f"Whisper model not found: {self._model}")

        with tempfile.TemporaryDirectory(prefix="uno-q-whisper-") as directory:
            output_prefix = Path(directory) / "transcript"
            command = [
                self._cli,
                "-m",
                str(self._model),
                "-f",
                str(audio_file),
                "-otxt",
                "-of",
                str(output_prefix),
                "-nt",
            ]
            try:
                result = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError as exc:
                raise TranscriptionError(
                    f"whisper.cpp executable not found: {self._cli}"
                ) from exc

            if result.returncode != 0:
                raise TranscriptionError(
                    result.stderr.strip() or "Local transcription failed"
                )

            transcript_file = output_prefix.with_suffix(".txt")
            if not transcript_file.is_file():
                raise TranscriptionError("whisper.cpp did not produce a transcript")
            return transcript_file.read_text(encoding="utf-8").strip()


class AzureSpeechEngine(SpeechEngine):
    def __init__(self, settings: Settings) -> None:
        self._language = settings.language

    def transcribe(self, audio_file: Path) -> str:
        speech_key = os.getenv("SPEECH_KEY")
        speech_region = os.getenv("SPEECH_REGION")
        if not speech_key or not speech_region:
            raise TranscriptionError(
                "Set SPEECH_KEY and SPEECH_REGION before using Azure mode"
            )

        try:
            import azure.cognitiveservices.speech as speechsdk
        except ImportError as exc:
            raise TranscriptionError(
                "Azure Speech SDK is not installed; install python/requirements.txt"
            ) from exc

        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region,
        )
        speech_config.speech_recognition_language = self._language
        audio_config = speechsdk.audio.AudioConfig(filename=str(audio_file))
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )
        phrase_grammar = speechsdk.PhraseListGrammar.from_recognizer(recognizer)
        for phrase in load_phrase_hints(settings.speech_phrases_file):
            phrase_grammar.addPhrase(phrase)
        result = recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text.strip()
        if result.reason == speechsdk.ResultReason.NoMatch:
            raise TranscriptionError("Azure could not recognize speech in the recording")
        if result.reason == speechsdk.ResultReason.Canceled:
            details = speechsdk.CancellationDetails(result)
            raise TranscriptionError(f"Azure transcription canceled: {details.reason}")
        raise TranscriptionError(f"Unexpected Azure result: {result.reason}")


def create_engine(settings: Settings) -> SpeechEngine:
    if settings.mode == "azure":
        return AzureSpeechEngine(settings)
    return WhisperCppEngine(settings)
