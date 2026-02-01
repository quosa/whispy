# Whispy — Voice AI Assistant for Kids

## Overview

A macOS terminal application that lets children (ages 7 and 11) talk to an AI
assistant using their laptop's microphone and speaker. The assistant listens,
thinks, and speaks back — like a conversation.

**Target languages:** English, French, Finnish

## Architecture

```
┌─────────┐    ┌────────────┐    ┌─────────┐    ┌─────────────┐    ┌─────────┐
│   Mic   │───>│ whisper.cpp │───>│   LLM   │───>│ Piper TTS   │───>│ Speaker │
│ (PyAudio)│   │   (STT)    │    │(ollama / │   │ (text-to-   │    │ (PyAudio)│
└─────────┘    └────────────┘    │ OpenAI)  │   │  speech)     │    └─────────┘
                                 └─────────┘    └─────────────┘
```

**Language: Python 3.11+**

Python is the pragmatic choice here — all four components (audio capture,
whisper.cpp, LLM clients, Piper) have mature Python bindings. A compiled
language would add complexity with no real benefit for a terminal app.

**Target hardware:** MacBook Pro M4 with 64GB RAM — more than enough to run
whisper `medium`, a 14B parameter LLM, and Piper TTS simultaneously.

**Dependency management:** `uv` — fast, handles venvs automatically.

## Technology Choices

| Component | Library | Why |
|-----------|---------|-----|
| Audio capture | `pyaudio` or `sounddevice` | Cross-platform mic access |
| Speech-to-text | `whisper-cpp-python` (bindings for whisper.cpp) | Fast, local, multilingual (EN/FR/FI all supported) |
| LLM (local) | `ollama` Python client | Simple API, many model choices, runs on Apple Silicon |
| LLM (cloud) | `openai` Python SDK | Fallback / higher quality option |
| Text-to-speech | `piper-tts` | Fast, local, good voice quality |
| Audio playback | `sounddevice` / `pyaudio` | Play generated speech |

### Model Recommendations

**Whisper STT models:**
- `small` for v1 — good balance of speed and accuracy on M4
- `medium` if accuracy is poor with child speech — your M4 handles it easily
- All models support English, French, and Finnish out of the box

**LLM models (via Ollama):**

You already have `llama3.1` and `qwen3` installed. Recommendations:

- `qwen3:8b` — your best starting point; strong multilingual (including
  French and reasonable Finnish), already installed
- `mistral-nemo:12b` — worth downloading; excellent French (Mistral is a
  French company), 12B fits easily in 64GB
- `llama3.1:8b` — solid English, decent French, weaker Finnish; good fallback

Recommendation: **start with qwen3, try mistral-nemo for French sessions.**
With 64GB you could even run a 14B model comfortably, but 8-12B is the sweet
spot for response speed with kids.

**Piper TTS voices:**
- English: `en_US-lessac-medium` or `en_GB-alan-medium`
- French: `fr_FR-siwis-medium`
- Finnish: limited availability — `fi_FI-harri-medium` if it exists, otherwise
  fall back to eSpeak (lower quality) or skip Finnish TTS in v1

## Requirements

### Functional Requirements

1. **R1 — Voice capture:** Record from laptop microphone with push-to-talk
   (press spacebar to talk, press again to stop). VAD as a future enhancement
2. **R2 — Speech-to-text:** Transcribe recorded audio to text using whisper.cpp,
   supporting EN/FR/FI
3. **R3 — LLM conversation:** Send transcription to an LLM and receive a
   text response, maintaining conversation context within a session
4. **R4 — Text-to-speech:** Convert LLM response to speech using Piper and
   play through speakers
5. **R5 — Terminal UI:** Display transcribed input and AI response as text in
   the terminal while audio plays
6. **R6 — Language selection:** User can choose language at startup (or
   auto-detect from speech)
7. **R7 — LLM backend selection:** Config flag to switch between Ollama
   (local) and OpenAI-compatible APIs (cloud, including x.ai — later phase)
8. **R8 — Kid-friendly system prompt:** Default system prompt that keeps
   responses simple, age-appropriate, and helpful for homework

### Non-Functional Requirements

1. **NF1 — Response latency:** Total round-trip (end of speech → start of
   audio playback) under 5 seconds on Apple Silicon with local models
2. **NF2 — Simplicity:** Single `python whispy.py` command to run (after
   one-time setup)
3. **NF3 — Offline capable:** Works fully offline with Ollama + local
   whisper + Piper models
4. **NF4 — macOS compatibility:** Tested on macOS 14+ with Apple Silicon

## Project Phases

### Phase 0 — Project Scaffolding
Set up the Python project structure, dependency management, and configuration.

**Tasks:**
- [ ] Create project structure (`src/whispy/`, `tests/`, `pyproject.toml`)
- [ ] Set up dependency management with `uv`
- [ ] Create configuration module (YAML or TOML config file for model paths,
      language, LLM backend, etc.)
- [ ] Add a basic CLI entry point (`python -m whispy` or `whispy` command)

### Phase 1 — Audio Capture
Get microphone input working reliably.

**Tasks:**
- [ ] Implement microphone recording with `sounddevice`
- [ ] Implement push-to-talk: press spacebar to start recording, press again
      to stop (simpler than hold-to-talk in a terminal)
- [ ] Save recorded audio to WAV buffer (in-memory, no temp files)
- [ ] Test with MacBook Pro built-in mic

### Phase 2 — Speech-to-Text (whisper.cpp)
Transcribe captured audio to text.

**Tasks:**
- [ ] Integrate `whisper-cpp-python` bindings
- [ ] Download and configure whisper models (`base` to start)
- [ ] Implement transcription function: WAV buffer → text string
- [ ] Add language parameter support (EN/FR/FI)
- [ ] Test transcription accuracy with child speech samples
- [ ] Print transcription to terminal as "You said: ..."

### Phase 3 — LLM Integration
Send transcribed text to an LLM and get a response.

**Tasks:**
- [ ] Implement Ollama client (using `ollama` Python package)
- [ ] Create a backend interface so we can add OpenAI-compatible APIs later
- [ ] Add conversation history (list of messages) for multi-turn context
- [ ] Write kid-friendly system prompt (age-appropriate, helpful, concise)
- [ ] Add language instruction to system prompt ("respond in French", etc.)
- [ ] Print response to terminal as "Assistant: ..."
- [ ] Default model: `qwen3:8b` (already installed)

### Phase 4 — Text-to-Speech (Piper)
Convert LLM response text to spoken audio.

**Tasks:**
- [ ] Integrate `piper-tts` or call Piper binary
- [ ] Download voice models for EN, FR (FI if available)
- [ ] Implement synthesis function: text → WAV audio
- [ ] Play synthesized audio through speakers
- [ ] Match TTS language/voice to selected language

### Phase 5 — Integration & Conversation Loop
Wire everything together into a working conversation.

**Tasks:**
- [ ] Build main conversation loop:
      `listen → transcribe → think → speak → repeat`
- [ ] Add graceful exit (Ctrl+C or "goodbye" voice command)
- [ ] Add terminal UI: show conversation history, current state
      ("Listening...", "Thinking...", "Speaking...")
- [ ] Handle errors gracefully (model not loaded, mic not available, etc.)
- [ ] Test full end-to-end flow

### Phase 6 — Polish & Multi-language
Refine the experience and ensure multilingual support works.

**Tasks:**
- [ ] Test with French speech input and output
- [ ] Test with Finnish speech input and output (TTS voice availability)
- [ ] Tune whisper model size for accuracy vs. speed tradeoff
- [ ] Tune LLM system prompt for kid-friendly responses
- [ ] Add setup script or instructions for first-time model downloads
- [ ] Write README with setup and usage instructions

## Quality Criteria & E2E Testing

### Manual E2E Test Script

Run through this checklist to verify the full flow works:

| # | Test | Pass criteria |
|---|------|--------------|
| 1 | **Start app** | `python -m whispy` launches without errors, shows "Ready" prompt |
| 2 | **Mic capture** | Hold spacebar (or press Enter), speak, release — app shows "Listening..." then "Transcribing..." |
| 3 | **English STT** | Say "What is two plus two?" — transcription shown matches what was said |
| 4 | **LLM response** | App shows "Thinking..." then displays a sensible text answer (e.g., "Four" or similar) |
| 5 | **TTS playback** | Audio plays through speakers matching the displayed text |
| 6 | **French STT** | Set language to French. Say "Combien font deux plus deux?" — correct French transcription |
| 7 | **French TTS** | Response is spoken in French with a French voice |
| 8 | **Finnish STT** | Set language to Finnish. Say "Paljonko on kaksi plus kaksi?" — correct Finnish transcription |
| 9 | **Multi-turn** | Ask a follow-up question ("And if you add three more?") — response uses context from prior turn |
| 10 | **Ollama backend** | App works fully offline with local models |
| 11 | **Model switch** | Run with `--model mistral-nemo:12b` — different model works without code changes |
| 12 | **Graceful exit** | Press Ctrl+C — app exits cleanly, no orphan processes |
| 13 | **No mic error** | Unplug mic / deny permission — app shows helpful error, doesn't crash |
| 14 | **Kid-safety check** | Ask something inappropriate — response is deflected or age-appropriate |

### Automated Tests (where practical)

- Unit tests for the LLM interface (mock Ollama/OpenAI responses)
- Unit tests for config loading
- Integration test: feed a pre-recorded WAV file through STT → LLM → TTS
  pipeline and verify each stage produces output

## Decisions Made

| Question | Decision |
|----------|----------|
| Input method | Push-to-talk (spacebar) for v1. VAD as future enhancement. |
| LLM backend | Ollama only for v1. OpenAI/x.ai compatible API as later phase. |
| Default LLM model | `qwen3:8b` (already installed). `mistral-nemo:12b` recommended for French. |
| Dependency management | `uv` |
| Target hardware | MacBook Pro M4, 64GB RAM, Apple Silicon |
| Languages for v1 | English + French (STT + TTS). Finnish STT works, Finnish TTS TBD. |

## Open Questions

1. **Finnish TTS** — Piper's Finnish voice selection is limited. Options:
   - Accept lower-quality eSpeak for Finnish TTS in v1
   - Skip Finnish TTS and only support Finnish STT (you speak Finnish, it
     understands but replies in English/French)
   - Investigate cloud TTS for Finnish only (adds online dependency)
   - **What's your preference?**

---

## Future Enhancement: Voice Activity Detection (VAD)

Adding VAD later is a **medium-difficulty** task. Here's the breakdown:

### What VAD does
Instead of pressing spacebar, the app automatically detects when someone
starts and stops talking, and processes the audio.

### Implementation options (easiest → hardest)

| Approach | Difficulty | Quality | Notes |
|----------|-----------|---------|-------|
| **Silero VAD** (PyTorch model) | Low-Medium | Excellent | Best option. ~1MB model, very accurate, runs on CPU. Has a Python package (`silero-vad`). Roughly 50-100 lines of code to integrate. |
| **WebRTC VAD** (`webrtcvad`) | Low | Good | Google's VAD. Simple Python wrapper. Works well in quiet rooms, struggles with background noise. ~30 lines to integrate. |
| **Energy-based** (volume threshold) | Very Low | Poor | Just check if audio amplitude exceeds a threshold. Unreliable with kids (volume varies wildly). Not recommended. |

### What makes VAD tricky (not the detection itself, but the edges)

1. **End-of-speech detection** — How long of a silence means "done talking"?
   Kids pause mid-sentence. Too short = cuts them off. Too long = slow.
   Needs a tunable threshold (e.g., 1.5 seconds of silence).

2. **Echo cancellation** — When the assistant speaks through the laptop
   speaker, the mic picks it up and could trigger a new "listening" cycle.
   Solutions: mute mic during TTS playback (simple), or use acoustic echo
   cancellation (complex).

3. **Background noise** — Kids' environments are noisy (TV, siblings).
   Silero VAD handles this well, but needs threshold tuning.

4. **Continuous listening overhead** — The mic runs constantly and feeds
   audio chunks to the VAD model. Minimal CPU on M4 but needs a clean
   async architecture.

### Estimated scope
- With Silero VAD: ~150-200 lines of new code, plus refactoring the audio
  capture module to support both modes (push-to-talk and VAD).
- Main risk: tuning the silence threshold and handling echo from speaker
  playback.
- Recommendation: add it as a Phase 7 toggle (`--vad` flag) alongside the
  existing push-to-talk, so users can switch between modes.
