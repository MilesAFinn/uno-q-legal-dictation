# UNO Q Legal Dictation
September 2026

This Arduino project captures a short utterance from a USB microphone and
transcribes it with either a local `whisper.cpp` model or Azure Speech. Temporary
audio is deleted automatically. An Adafruit CH9328 breakout provides USB keyboard
output without requiring a Windows companion application. Timekeeping and an
e-ink display are deferred until the speech pipeline is proven.

## Current milestone

- Capture mono 16 kHz, 16-bit WAV audio through ALSA.
- Select `local` or `azure` transcription at runtime.
- Print the transcript to the console.
- Save a transcript only when `--save-transcript` is supplied.
- Accept an existing WAV file for testing without a microphone.
- Optionally type completed text into the focused Windows application.

## Project structure

```text
uno_q_legal_dictation/
|-- app.yaml
|-- data/
|   `-- input.wav          # optional App Lab file-input slot
|-- python/
|   |-- main.py
|   |-- requirements.txt
|   `-- dictation/
|-- sketch/
|   |-- sketch.ino
|   `-- sketch.yaml
`-- tests/
```

## UNO Q prerequisites

Connect a USB microphone through a powered USB-C hub. On the UNO Q Debian side,
verify that Advanced Linux Sound Architecture ("ALSA") can see it:

```bash
python3 python/main.py --list-microphones
```

Install the Python dependency used by Azure mode:

```bash
sudo apt install -y python3-venv
python3 -m venv ~/.venvs/uno-q-legal-dictation
~/.venvs/uno-q-legal-dictation/bin/python -m pip install -r python/requirements.txt
```

Do not put Azure credentials in this repository or in `app.yaml`.

## Azure mode

Store the Azure Speech region and key outside the repository in
`~/.config/uno-q-legal-dictation/azure.env`, then limit access to the board's
`arduino` user:

```bash
mkdir -p ~/.config/uno-q-legal-dictation
chmod 700 ~/.config/uno-q-legal-dictation
nano ~/.config/uno-q-legal-dictation/azure.env
chmod 600 ~/.config/uno-q-legal-dictation/azure.env
```

The protected file contains `SPEECH_REGION` and `SPEECH_KEY`. Never print,
screenshot, or commit it. Run a five-second cloud transcription with the secure
launcher:

```bash
scripts/dictate-azure --seconds 5
```

The launcher uses the stable Plantronics ALSA card name and the isolated Python
environment. It also accepts normal options such as `--audio-file` and
`--save-transcript`. `ALSA_DEVICE`, `AZURE_SPEECH_ENV_FILE`, and
`DICTATION_PYTHON` can override its defaults.

Azure phrase hints are loaded from `config/speech-phrases.txt`. Add one legal,
patent, client, or proper-name phrase per line; blank lines and lines beginning
with `#` are ignored. `SPEECH_PHRASES_FILE` can select a different list. Phrase
hints improve recognition likelihood but do not force Azure to produce specific
text.

The Python Speech SDK supports Linux ARM64 on supported Debian releases. For a
production version, replace the long-lived API key with stronger secret handling.

## Local mode

The app includes an ARM64 `whisper.cpp` executable and the English `tiny.en`
model. No environment variables or network connection are required:

```bash
python3 python/main.py --mode local --seconds 5
```

`WHISPER_CLI` and `WHISPER_MODEL` can still override the bundled files.

## Test with an existing WAV file

```bash
python3 python/main.py --mode local --audio-file sample.wav
python3 python/main.py --mode azure --audio-file sample.wav
```

For the Run button, place the audio at `data/input.wav`. If that file is
present, the app transcribes it instead of opening a microphone. Remove or rename
it to return to microphone capture. `AUDIO_FILE` may also supply a path without a
command-line argument. Local input must be mono, 16 kHz, 16-bit PCM WAV.

## CH9328 keyboard output

The CH9328 is powered by and connected to the Windows computer through its own
USB-C port. Connect only these signals between the UNO Q and CH9328:

| UNO Q | CH9328 |
| --- | --- |
| D1 / TX | RX |
| GND | GND |

Do not connect the CH9328 VCC pin to the UNO Q. Both boards already have power,
and they need only a common ground and the 3.3 V UART data signal.

Before applying power, configure the CH9328 for Mode 3 as documented by Adafruit:
switch 2 OFF, switches 3 and 4 ON. The sketch sends transparent ASCII at the
default 9600 baud. Connect the CH9328 USB-C port to Windows.

Keyboard output is deliberately opt-in. Place the cursor in a harmless test
document, then run:

```bash
python3 python/main.py --mode local --seconds 5 --output keyboard
```

There is a three-second warning before typing begins. Use `--output both` to print
and type, or change the delay with `--keyboard-delay`. The current implementation
uses a US keyboard layout and converts smart punctuation and accented Latin text
to ASCII. Unsupported symbols become `?`.

## Privacy defaults

- Audio is held in a temporary directory and deleted after transcription.
- Transcripts are printed but not stored by default.
- `.env`, models, recordings, and transcript files are excluded from Git.
- Cloud mode should only be used when permitted for the information being dictated.

## Planned milestones

1. Prove USB microphone capture on the UNO Q. *** done *** 
2. Benchmark local `whisper.cpp` transcription.*** DEFER***
3. Configure and test Azure Speech transcription.  *** done *** 
4. Add a physical push-to-talk button and local/cloud selector.
5. Bench-test CH9328 keyboard output in a disposable text document.
6. Add an e-ink status and review display.
7. Integrate with PatVault.com API "Q send me patent number eight one two three four five six."
8. Add CSV timekeeping as a separate module.
