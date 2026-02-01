"""Configuration for Whispy."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    raise RuntimeError("Python 3.11+ is required")

SYSTEM_PROMPTS = {
    "en": (
        "You are Whispy, a friendly and helpful AI assistant talking to children.\n"
        "Keep your answers simple, clear, and short — 2-3 sentences for simple "
        "questions, a bit more for complex ones.\n"
        "Use words that kids aged 7-11 can understand.\n"
        "For homework questions, help them understand the concept rather than "
        "just giving the answer.\n"
        "Be encouraging, patient, and kind.\n"
        "If you don't know something, say so honestly.\n"
        "Never use complicated jargon.\n"
        "IMPORTANT: Never use emojis, emoticons, or smileys in your responses. "
        "Your responses will be read aloud by a text-to-speech system."
    ),
    "fr": (
        "Tu es Whispy, un assistant IA amical et utile qui parle avec des enfants.\n"
        "Garde tes réponses simples, claires et courtes — 2-3 phrases pour les "
        "questions simples, un peu plus pour les questions complexes.\n"
        "Utilise des mots que des enfants de 7 à 11 ans peuvent comprendre.\n"
        "Pour les questions de devoirs, aide-les à comprendre le concept plutôt "
        "que de simplement donner la réponse.\n"
        "Sois encourageant, patient et gentil.\n"
        "Si tu ne sais pas quelque chose, dis-le honnêtement.\n"
        "Réponds toujours en français.\n"
        "IMPORTANT : N'utilise jamais d'emojis, d'émoticônes ou de smileys dans "
        "tes réponses. Tes réponses seront lues à voix haute par un système de "
        "synthèse vocale."
    ),
}

# macOS voices for the `say` command
MACOS_VOICES = {
    "en": "Samantha",
    "fr": "Thomas",
}


@dataclass
class WhispyConfig:
    """Runtime configuration."""

    language: str = "en"
    whisper_model: str = "small"
    llm_model: str = "qwen3:8b"
    tts_backend: str = "say"  # "say" (macOS built-in) or "piper"
    tts_voice: str = ""  # auto-selected from language if empty
    tts_rate: int = 155  # words-per-minute for macOS say (default ~200 is too fast)
    sample_rate: int = 16000  # audio sample rate (whisper expects 16kHz)
    max_history: int = 20  # max conversation messages kept in memory

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPTS.get(self.language, SYSTEM_PROMPTS["en"])

    @property
    def resolved_tts_voice(self) -> str:
        if self.tts_voice:
            return self.tts_voice
        return MACOS_VOICES.get(self.language, MACOS_VOICES["en"])


def load_config(config_path: Path | None = None) -> WhispyConfig:
    """Load configuration from a TOML file, if it exists."""
    config = WhispyConfig()
    if config_path and config_path.exists():
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        whispy = data.get("whispy", {})
        for key in (
            "language",
            "whisper_model",
            "llm_model",
            "tts_backend",
            "tts_voice",
            "tts_rate",
            "sample_rate",
            "max_history",
        ):
            if key in whispy:
                setattr(config, key, whispy[key])
    return config


def parse_args(argv: list[str] | None = None) -> WhispyConfig:
    """Parse CLI arguments and merge with config file."""
    parser = argparse.ArgumentParser(
        prog="whispy",
        description="Whispy — Voice AI assistant for kids",
    )
    parser.add_argument(
        "-l", "--language",
        choices=["en", "fr"],
        default=None,
        help="conversation language (default: en)",
    )
    parser.add_argument(
        "-m", "--model",
        default=None,
        help="Ollama model name (default: qwen3:8b)",
    )
    parser.add_argument(
        "--whisper-model",
        default=None,
        help="Whisper model size: tiny, base, small, medium (default: small)",
    )
    parser.add_argument(
        "--tts",
        choices=["say", "piper"],
        default=None,
        help="TTS backend (default: say)",
    )
    parser.add_argument(
        "-c", "--config",
        default=None,
        help="path to config.toml file",
    )

    args = parser.parse_args(argv)

    # Load base config from file
    config_path = Path(args.config) if args.config else Path("config.toml")
    config = load_config(config_path if config_path.exists() else None)

    # CLI overrides
    if args.language is not None:
        config.language = args.language
    if args.model is not None:
        config.llm_model = args.model
    if args.whisper_model is not None:
        config.whisper_model = args.whisper_model
    if args.tts is not None:
        config.tts_backend = args.tts

    return config
