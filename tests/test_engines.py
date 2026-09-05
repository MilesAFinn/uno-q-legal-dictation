from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from dictation.config import Settings
from dictation.engines import (
    AzureSpeechEngine,
    WhisperCppEngine,
    create_engine,
    load_phrase_hints,
)


class EngineFactoryTests(unittest.TestCase):
    def test_creates_azure_engine(self) -> None:
        settings = Settings.from_environment("azure")
        self.assertIsInstance(create_engine(settings), AzureSpeechEngine)

    def test_local_mode_requires_model(self) -> None:
        settings = replace(Settings.from_environment("local"), whisper_model=None)
        with self.assertRaisesRegex(RuntimeError, "WHISPER_MODEL"):
            WhisperCppEngine(settings)


class PhraseHintTests(unittest.TestCase):
    def test_loads_phrases_and_ignores_comments_and_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            phrases_file = Path(directory) / "phrases.txt"
            phrases_file.write_text(
                "# Patent vocabulary\n\nPatVault\n  inter partes review  \n",
                encoding="utf-8",
            )

            self.assertEqual(
                load_phrase_hints(phrases_file),
                ["PatVault", "inter partes review"],
            )

    def test_missing_phrase_file_is_allowed(self) -> None:
        self.assertEqual(load_phrase_hints(Path("missing-phrases.txt")), [])


if __name__ == "__main__":
    unittest.main()
