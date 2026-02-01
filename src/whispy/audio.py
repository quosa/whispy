"""Audio capture and playback.

Uses sounddevice for microphone recording and speaker output.
Audio is captured at 16 kHz mono (what Whisper expects).
"""

from __future__ import annotations

import io
import sys
import wave

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None


def _require_sounddevice() -> None:
    if sd is None:
        raise RuntimeError(
            "sounddevice is not installed. Install it with:\n"
            "  uv pip install sounddevice\n"
            "On macOS you may also need: brew install portaudio"
        )


class Recorder:
    """Record audio from the microphone."""

    def __init__(self, sample_rate: int = 16000) -> None:
        _require_sounddevice()
        self.sample_rate = sample_rate
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def start(self) -> None:
        """Start recording from the default microphone."""
        self._frames = []
        self._status_errors: list[str] = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def _callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: object,
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            self._status_errors.append(str(status))
        self._frames.append(indata.copy())

    def stop(self) -> np.ndarray:
        """Stop recording and return audio as a float32 numpy array."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._frames:
            audio = np.concatenate(self._frames, axis=0).flatten()
            return audio
        return np.array([], dtype=np.float32)

    def get_diagnostics(self, audio: np.ndarray, sample_rate: int) -> dict:
        """Return recording diagnostics for debugging."""
        duration = audio.size / sample_rate if audio.size > 0 else 0.0
        peak = float(np.max(np.abs(audio))) if audio.size > 0 else 0.0
        return {
            "duration_s": round(duration, 1),
            "peak_amplitude": round(peak, 4),
            "is_silent": peak < 0.001,
            "stream_errors": list(self._status_errors),
        }


def play_audio(audio: np.ndarray, sample_rate: int) -> None:
    """Play a numpy audio array through the default speaker."""
    _require_sounddevice()
    sd.play(audio, samplerate=sample_rate)
    sd.wait()


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    """Convert a float32 numpy array to WAV file bytes."""
    audio_int16 = (audio * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    return buf.getvalue()


def wav_bytes_to_audio(wav_data: bytes) -> tuple[np.ndarray, int]:
    """Convert WAV bytes to a float32 numpy array and sample rate."""
    buf = io.BytesIO(wav_data)
    with wave.open(buf, "rb") as wf:
        sample_rate = wf.getframerate()
        audio_bytes = wf.readframes(wf.getnframes())
        audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32767
    return audio_float32, sample_rate


# -- Terminal key reading (for push-to-talk) --------------------------------

if sys.platform in ("darwin", "linux"):
    import termios
    import tty

    def wait_for_key() -> str:
        """Block until a single key is pressed. Returns the character."""
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)  # cbreak: single-char read, Ctrl+C still works
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

else:
    def wait_for_key() -> str:
        """Fallback: wait for Enter key."""
        input()
        return "\n"
