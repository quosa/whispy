"""Tests for whispy configuration."""

import tempfile
from pathlib import Path

from whispy.config import WhispyConfig, load_config, parse_args


def test_default_config():
    config = WhispyConfig()
    assert config.language == "en"
    assert config.llm_model == "qwen3:8b"
    assert config.whisper_model == "small"
    assert config.tts_backend == "say"
    assert config.sample_rate == 16000


def test_system_prompt_english():
    config = WhispyConfig(language="en")
    assert "Whispy" in config.system_prompt
    assert "children" in config.system_prompt


def test_system_prompt_french():
    config = WhispyConfig(language="fr")
    assert "Whispy" in config.system_prompt
    assert "français" in config.system_prompt


def test_resolved_tts_voice_defaults():
    assert WhispyConfig(language="en").resolved_tts_voice == "Samantha"
    assert WhispyConfig(language="fr").resolved_tts_voice == "Thomas"


def test_resolved_tts_voice_custom_override():
    config = WhispyConfig(language="en", tts_voice="Daniel")
    assert config.resolved_tts_voice == "Daniel"


def test_load_config_from_toml():
    toml_content = b"""
[whispy]
language = "fr"
llm_model = "mistral-nemo:12b"
whisper_model = "medium"
tts_rate = 160
"""
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
        f.write(toml_content)
        f.flush()
        config = load_config(Path(f.name))

    assert config.language == "fr"
    assert config.llm_model == "mistral-nemo:12b"
    assert config.whisper_model == "medium"
    assert config.tts_rate == 160
    # Unchanged defaults
    assert config.tts_backend == "say"
    assert config.sample_rate == 16000


def test_load_config_missing_file():
    config = load_config(Path("/nonexistent/config.toml"))
    # Should return defaults when file doesn't exist
    assert config.language == "en"


def test_parse_args_defaults():
    config = parse_args([])
    assert config.language == "en"
    assert config.llm_model == "qwen3:8b"


def test_parse_args_overrides():
    config = parse_args(["-l", "fr", "-m", "mistral-nemo:12b", "--whisper-model", "medium"])
    assert config.language == "fr"
    assert config.llm_model == "mistral-nemo:12b"
    assert config.whisper_model == "medium"
