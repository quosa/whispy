"""Speech-to-text using whisper.cpp via pywhispercpp."""

from __future__ import annotations

import tempfile
import wave
from pathlib import Path

import numpy as np

try:
    from pywhispercpp.model import Model as WhisperModel
except ImportError:
    WhisperModel = None


class STT:
    """Speech-to-text transcription using whisper.cpp.

    Wraps pywhispercpp to transcribe audio numpy arrays to text.
    Models are downloaded automatically on first use.
    """

    def __init__(self, model_name: str = "small") -> None:
        if WhisperModel is None:
            raise RuntimeError(
                "pywhispercpp is not installed. Install it with:\n"
                "  uv pip install pywhispercpp\n"
                "You may also need: brew install cmake"
            )
        self.model = WhisperModel(model_name)

    def transcribe(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        language: str = "en",
    ) -> str:
        """Transcribe a float32 audio array to text.

        Args:
            audio: Float32 numpy array of audio samples (mono, 16kHz).
            sample_rate: Sample rate of the audio (should be 16000).
            language: Language code for transcription ('en', 'fr', etc.).

        Returns:
            Transcribed text string.
        """
        if audio.size == 0:
            return ""

        # pywhispercpp works best with file paths — write a temp WAV file
        wav_path = self._save_temp_wav(audio, sample_rate)
        try:
            segments = self.model.transcribe(wav_path, language=language)
            text = " ".join(seg.text for seg in segments).strip()
            return text
        finally:
            Path(wav_path).unlink(missing_ok=True)

    @staticmethod
    def _save_temp_wav(audio: np.ndarray, sample_rate: int) -> str:
        """Save audio to a temporary WAV file and return the path."""
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio_int16 = (audio.flatten() * 32767).astype(np.int16)
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())
        return tmp.name
