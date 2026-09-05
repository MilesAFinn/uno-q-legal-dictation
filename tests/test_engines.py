from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from dictation.config import Settings
from dictation.engines import AzureSpeechEngine, WhisperCppEngine, create_engine


class EngineFactoryTests(unittest.TestCase):
    def test_creates_azure_engine(self) -> None:
        settings = Settings.from_environment("azure")
        self.assertIsInstance(create_engine(settings), AzureSpeechEngine)

    def test_local_mode_requires_model(self) -> None:
        settings = replace(Settings.from_environment("local"), whisper_model=None)
        with self.assertRaisesRegex(RuntimeError, "WHISPER_MODEL"):
            WhisperCppEngine(settings)


if __name__ == "__main__":
    unittest.main()
