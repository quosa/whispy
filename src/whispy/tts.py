"""Text-to-speech.

Two backends:
- macOS `say` command (default, zero dependencies, always available on Mac)
- Piper TTS (optional, better quality, requires separate install)
"""

from __future__ import annotations

import subprocess
import sys
from typing import Protocol


class TTSBackend(Protocol):
    """Interface for TTS backends."""

    def speak(self, text: str) -> None: ...


class MacOSSayTTS:
    """Text-to-speech using macOS built-in `say` command.

    Available voices (run `say -v ?` to list all):
    - English: Samantha, Daniel, Karen, Moira
    - French: Thomas, Amelie, Audrey
    """

    def __init__(self, voice: str = "Samantha", rate: int = 180) -> None:
        if sys.platform != "darwin":
            raise RuntimeError("macOS `say` command is only available on macOS")
        self.voice = voice
        self.rate = rate

    def speak(self, text: str) -> None:
        """Speak text through the system speaker. Blocks until done."""
        if not text.strip():
            return
        cmd = ["say", "-v", self.voice, "-r", str(self.rate), text]
        subprocess.run(cmd, check=True)


class PiperTTS:
    """Text-to-speech using Piper (via command-line binary).

    Requires Piper to be installed and a voice model downloaded.
    See: https://github.com/rhasspy/piper
    """

    def __init__(self, model_path: str, piper_bin: str = "piper") -> None:
        self.model_path = model_path
        self.piper_bin = piper_bin

    def speak(self, text: str) -> None:
        """Synthesize speech and play through speakers."""
        if not text.strip():
            return
        # Piper outputs WAV to stdout; pipe to aplay/afplay for playback
        play_cmd = "afplay" if sys.platform == "darwin" else "aplay"

        piper_proc = subprocess.Popen(
            [self.piper_bin, "--model", self.model_path, "--output_file", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        play_proc = subprocess.Popen(
            [play_cmd, "-"],
            stdin=piper_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        piper_proc.stdin.write(text.encode("utf-8"))
        piper_proc.stdin.close()
        play_proc.wait()
        piper_proc.wait()


def create_tts(backend: str, voice: str, rate: int = 180) -> TTSBackend:
    """Factory: create the appropriate TTS backend."""
    if backend == "piper":
        return PiperTTS(model_path=voice)
    # Default to macOS say
    return MacOSSayTTS(voice=voice, rate=rate)
