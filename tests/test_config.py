from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from dictation.config import Settings


class SettingsTests(unittest.TestCase):
    def test_defaults_to_local_mode(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_environment()
        self.assertEqual(settings.mode, "local")
        self.assertEqual(settings.language, "en-US")
        self.assertEqual(settings.sample_rate, 16000)
        project_root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            settings.whisper_cli,
            str(project_root / "vendor/bin/whisper-cli"),
        )
        self.assertEqual(
            settings.whisper_model,
            project_root / "vendor/models/ggml-tiny.en.bin",
        )

    def test_rejects_unknown_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "DICTATION_MODE"):
            Settings.from_environment("other")


if __name__ == "__main__":
    unittest.main()
