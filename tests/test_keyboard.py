from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from dictation.keyboard import chunks, keyboard_safe_text


class KeyboardTextTests(unittest.TestCase):
    def test_normalizes_legal_punctuation_and_accents(self) -> None:
        text = "Client\u2019s caf\u00e9 \u2014 reviewed\u2026"
        self.assertEqual(keyboard_safe_text(text), "Client's cafe - reviewed...")

    def test_replaces_unsupported_characters(self) -> None:
        self.assertEqual(keyboard_safe_text("Section \u00a7 1"), "Section ? 1")

    def test_chunks_long_text(self) -> None:
        self.assertEqual(chunks("abcdefgh", 3), ["abc", "def", "gh"])


if __name__ == "__main__":
    unittest.main()

