"""Tests for the LLM module."""

from unittest.mock import MagicMock, patch

import pytest


def _make_ollama_response(content: str) -> dict:
    """Create a mock Ollama chat response."""
    return {"message": {"role": "assistant", "content": content}}


@pytest.fixture
def mock_ollama():
    """Patch the ollama client so tests don't need a running Ollama server."""
    with patch("whispy.llm.ollama_client") as mock:
        mock.chat = MagicMock(return_value=_make_ollama_response("Four!"))
        yield mock


def test_chat_sends_message(mock_ollama):
    from whispy.llm import OllamaLLM

    llm = OllamaLLM(model="test-model", system_prompt="Be helpful.")
    reply = llm.chat("What is 2+2?")

    assert reply == "Four!"
    mock_ollama.chat.assert_called_once()
    # After chat: system + user + assistant = 3
    assert len(llm._history) == 3
    assert llm._history[0]["role"] == "system"
    assert llm._history[1] == {"role": "user", "content": "What is 2+2?"}
    assert llm._history[2] == {"role": "assistant", "content": "Four!"}


def test_chat_maintains_history(mock_ollama):
    from whispy.llm import OllamaLLM

    llm = OllamaLLM(model="test-model", system_prompt="Be helpful.")
    llm.chat("First question")

    mock_ollama.chat.return_value = _make_ollama_response("Second answer")
    llm.chat("Second question")

    # system + user1 + assistant1 + user2 + assistant2 = 5
    assert len(llm._history) == 5
    assert llm._history[3] == {"role": "user", "content": "Second question"}
    assert llm._history[4] == {"role": "assistant", "content": "Second answer"}


def test_reset_clears_history(mock_ollama):
    from whispy.llm import OllamaLLM

    llm = OllamaLLM(model="test-model", system_prompt="Be helpful.")
    llm.chat("Question")
    llm.reset()

    # After reset: only system prompt remains
    assert len(llm._history) == 1
    assert llm._history[0]["role"] == "system"

    mock_ollama.chat.return_value = _make_ollama_response("Fresh answer")
    llm.chat("New question")

    # system + user + assistant = 3
    assert len(llm._history) == 3


def test_history_trimming(mock_ollama):
    from whispy.llm import OllamaLLM

    llm = OllamaLLM(model="test-model", system_prompt="System.", max_history=6)

    for i in range(10):
        mock_ollama.chat.return_value = _make_ollama_response(f"Answer {i}")
        llm.chat(f"Question {i}")

    # History should be trimmed to max_history
    assert len(llm._history) <= 6
    # System prompt is always preserved
    assert llm._history[0]["role"] == "system"
    assert llm._history[0]["content"] == "System."
    # Most recent exchange is kept
    assert llm._history[-1]["content"] == "Answer 9"


def test_chat_without_system_prompt(mock_ollama):
    from whispy.llm import OllamaLLM

    llm = OllamaLLM(model="test-model", system_prompt="")
    reply = llm.chat("Hello")

    assert reply == "Four!"
    # user + assistant = 2 (no system prompt)
    assert len(llm._history) == 2
    assert llm._history[0]["role"] == "user"
    assert llm._history[1]["role"] == "assistant"
