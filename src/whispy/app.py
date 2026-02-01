"""Main conversation loop for Whispy."""

from __future__ import annotations

import sys

from whispy.audio import Recorder, wait_for_key
from whispy.config import WhispyConfig, parse_args
from whispy.llm import OllamaLLM
from whispy.stt import STT
from whispy.tts import create_tts


def print_banner(config: WhispyConfig) -> None:
    lang_label = {"en": "English", "fr": "French"}.get(config.language, config.language)
    print("=" * 50)
    print("  Whispy - Voice AI Assistant")
    print(f"  Language : {lang_label}")
    print(f"  LLM      : {config.llm_model}")
    print(f"  Whisper  : {config.whisper_model}")
    print(f"  TTS      : {config.tts_backend} ({config.resolved_tts_voice})")
    print("=" * 50)
    print()


def print_status(msg: str) -> None:
    """Print a status message that overwrites itself."""
    sys.stdout.write(f"\r  [{msg}]")
    sys.stdout.flush()


def clear_status() -> None:
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()


def run(config: WhispyConfig) -> None:
    """Run the main conversation loop."""
    # -- Initialize components -----------------------------------------------
    print("Loading whisper model... ", end="", flush=True)
    stt = STT(model_name=config.whisper_model)
    print("ok")

    print("Connecting to Ollama... ", end="", flush=True)
    llm = OllamaLLM(
        model=config.llm_model,
        system_prompt=config.system_prompt,
        max_history=config.max_history,
    )
    print("ok")

    tts = create_tts(
        backend=config.tts_backend,
        voice=config.resolved_tts_voice,
        rate=config.tts_rate,
    )

    recorder = Recorder(sample_rate=config.sample_rate)

    print_banner(config)
    print("Press SPACE to talk, Q to quit.\n")

    # -- Conversation loop ---------------------------------------------------
    while True:
        key = wait_for_key()

        if key in ("q", "Q"):
            print("\nGoodbye!")
            break

        if key != " ":
            continue

        # --- Record ---------------------------------------------------------
        recorder.start()
        print_status("Listening... press SPACE to stop")

        while True:
            k = wait_for_key()
            if k == " ":
                break

        audio = recorder.stop()
        clear_status()

        if audio.size == 0:
            print("  (no audio captured)\n")
            continue

        duration = audio.size / config.sample_rate
        if duration < 0.3:
            print("  (too short, skipped)\n")
            continue

        # --- Transcribe -----------------------------------------------------
        print_status("Transcribing...")
        text = stt.transcribe(
            audio,
            sample_rate=config.sample_rate,
            language=config.language,
        )
        clear_status()

        if not text.strip():
            print("  (silence detected)\n")
            continue

        print(f"  You: {text}")

        # --- LLM response ---------------------------------------------------
        print_status("Thinking...")
        try:
            response = llm.chat(text)
        except RuntimeError as e:
            clear_status()
            print(f"  Error: {e}\n")
            continue
        clear_status()

        print(f"  Whispy: {response}\n")

        # --- Speak ----------------------------------------------------------
        print_status("Speaking...")
        try:
            tts.speak(response)
        except Exception as e:
            clear_status()
            print(f"  (TTS error: {e})")
        clear_status()

        print()  # blank line between turns


def main() -> None:
    """Entry point for the whispy command."""
    config = parse_args()
    try:
        run(config)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
