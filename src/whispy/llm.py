"""LLM integration via Ollama."""

from __future__ import annotations

from typing import Protocol

try:
    import ollama as ollama_client
except ImportError:
    ollama_client = None


class LLMBackend(Protocol):
    """Interface for LLM backends.

    Any backend that implements chat() and reset() can be used.
    This makes it easy to add OpenAI-compatible APIs later.
    """

    def chat(self, message: str) -> str: ...
    def reset(self) -> None: ...


class OllamaLLM:
    """Ollama LLM backend with conversation history."""

    def __init__(
        self,
        model: str = "qwen3:8b",
        system_prompt: str = "",
        max_history: int = 20,
    ) -> None:
        if ollama_client is None:
            raise RuntimeError(
                "ollama package is not installed. Install it with:\n"
                "  uv pip install ollama\n"
                "Also make sure Ollama is running: ollama serve"
            )
        self.model = model
        self.system_prompt = system_prompt
        self.max_history = max_history
        self._history: list[dict[str, str]] = []
        if system_prompt:
            self._history.append({"role": "system", "content": system_prompt})

    def chat(self, message: str) -> str:
        """Send a message and get a response. Maintains conversation history."""
        self._history.append({"role": "user", "content": message})
        self._trim_history()

        try:
            response = ollama_client.chat(
                model=self.model,
                messages=self._history,
            )
        except Exception as e:
            # Remove the user message if the request failed
            self._history.pop()
            error_msg = str(e)
            if "connection" in error_msg.lower():
                raise RuntimeError(
                    "Cannot connect to Ollama. Is it running?\n"
                    "  Start it with: ollama serve"
                ) from e
            raise

        reply = response["message"]["content"]
        self._history.append({"role": "assistant", "content": reply})
        self._trim_history()
        return reply

    def reset(self) -> None:
        """Clear conversation history (keeps system prompt)."""
        self._history = []
        if self.system_prompt:
            self._history.append({"role": "system", "content": self.system_prompt})

    def _trim_history(self) -> None:
        """Keep history within max_history limit, preserving system prompt."""
        if len(self._history) <= self.max_history:
            return
        has_system = (
            self._history and self._history[0]["role"] == "system"
        )
        if has_system:
            system = self._history[0]
            self._history = [system] + self._history[-(self.max_history - 1) :]
        else:
            self._history = self._history[-self.max_history :]
