from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
import wave
from pathlib import Path

from dictation.audio import AudioCaptureError, list_capture_devices, record_wav
from dictation.config import Settings
from dictation.engines import TranscriptionError, create_engine
from dictation.keyboard import KeyboardOutputError, type_with_ch9328


APP_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AUDIO_FILE = APP_ROOT / "data" / "input.wav"


def validate_local_wav(audio_file: Path) -> None:
    try:
        with wave.open(str(audio_file), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
    except (OSError, wave.Error) as exc:
        raise ValueError(f"Not a readable WAV file: {audio_file}") from exc

    if (channels, sample_width, sample_rate) != (1, 2, 16000):
        raise ValueError(
            "Local audio files must be mono, 16 kHz, 16-bit PCM WAV "
            f"(received {channels} channel(s), {sample_rate} Hz, "
            f"{sample_width * 8}-bit)"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UNO Q legal dictation prototype")
    parser.add_argument("--mode", choices=("local", "azure"))
    parser.add_argument("--seconds", type=int, default=5)
    parser.add_argument(
        "--audio-file",
        type=Path,
        default=Path(os.environ["AUDIO_FILE"]) if os.getenv("AUDIO_FILE") else None,
        help="transcribe a 16-bit WAV file instead of recording; defaults to AUDIO_FILE",
    )
    parser.add_argument("--save-transcript", type=Path)
    parser.add_argument(
        "--output",
        choices=("console", "keyboard", "both"),
        default="console",
        help="send recognized text to the console, CH9328 keyboard, or both",
    )
    parser.add_argument(
        "--keyboard-delay",
        type=float,
        default=3.0,
        help="seconds to wait before typing so the target window can be focused",
    )
    parser.add_argument(
        "--list-microphones",
        action="store_true",
        help="list ALSA capture devices and exit",
    )
    return parser.parse_args()


def run() -> int:
    args = parse_args()
    try:
        if args.list_microphones:
            print(list_capture_devices())
            return 0

        settings = Settings.from_environment(args.mode)
        engine = create_engine(settings)

        selected_audio_file = args.audio_file
        if selected_audio_file is None and DEFAULT_AUDIO_FILE.is_file():
            selected_audio_file = DEFAULT_AUDIO_FILE

        if selected_audio_file:
            audio_file = selected_audio_file.expanduser().resolve()
            if not audio_file.is_file():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            if settings.mode == "local":
                validate_local_wav(audio_file)
            transcript = engine.transcribe(audio_file)
        else:
            # Temporary audio is removed as soon as transcription finishes.
            with tempfile.TemporaryDirectory(prefix="uno-q-dictation-") as directory:
                audio_file = Path(directory) / "recording.wav"
                print(f"Recording for {args.seconds} seconds in {settings.mode} mode...")
                record_wav(
                    audio_file,
                    seconds=args.seconds,
                    device=settings.alsa_device,
                    sample_rate=settings.sample_rate,
                )
                transcript = engine.transcribe(audio_file)

        if args.output in {"console", "both"}:
            print(transcript)
        if args.output in {"keyboard", "both"}:
            if args.keyboard_delay < 0:
                raise ValueError("Keyboard delay cannot be negative")
            print(
                f"Typing begins in {args.keyboard_delay:g} seconds; focus the target field.",
                file=sys.stderr,
            )
            time.sleep(args.keyboard_delay)
            type_with_ch9328(transcript)
        if args.save_transcript:
            destination = args.save_transcript.expanduser().resolve()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(transcript + "\n", encoding="utf-8")
            print(f"Transcript saved to {destination}", file=sys.stderr)
        return 0
    except (
        AudioCaptureError,
        KeyboardOutputError,
        TranscriptionError,
        FileNotFoundError,
        ValueError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
