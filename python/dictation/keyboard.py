from __future__ import annotations

import unicodedata


class KeyboardOutputError(RuntimeError):
    pass


_PUNCTUATION = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
)


def keyboard_safe_text(text: str) -> str:
    """Convert recognized text to characters supported by a US HID keyboard."""
    normalized = unicodedata.normalize("NFKD", text.translate(_PUNCTUATION))
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return without_accents.encode("ascii", errors="replace").decode("ascii")


def chunks(text: str, size: int = 120) -> list[str]:
    if size <= 0:
        raise ValueError("Chunk size must be greater than zero")
    return [text[index : index + size] for index in range(0, len(text), size)]


def type_with_ch9328(text: str) -> None:
    """Send text through the UNO Q Bridge to the CH9328 UART adapter."""
    safe_text = keyboard_safe_text(text)
    if not safe_text:
        return

    try:
        from arduino.app_utils import Bridge
    except ImportError as exc:
        raise KeyboardOutputError(
            "Arduino Bridge is unavailable; keyboard output must run on the UNO Q"
        ) from exc

    for part in chunks(safe_text):
        try:
            Bridge.call("type_text", part)
        except Exception as exc:
            raise KeyboardOutputError(f"Unable to send text to CH9328: {exc}") from exc
