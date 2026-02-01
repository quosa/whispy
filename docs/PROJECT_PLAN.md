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
- `base` or `small` for fast responses (good enough for clear child speech)
- `medium` if accuracy is poor — trades speed for quality
- All models support English, French, and Finnish

**LLM models (via Ollama):**
- `llama3.2:3b` — fast, good enough for homework help
- `mistral:7b` — good multilingual support (especially French)
- `gemma2:9b` — alternative with solid multilingual capabilities

**Piper TTS voices:**
- English: `en_US-lessac-medium` or `en_GB-alan-medium`
- French: `fr_FR-siwis-medium`
- Finnish: `fi_FI-harri-medium` (check availability — Finnish voices are limited)

## Requirements

### Functional Requirements

1. **R1 — Voice capture:** Record from laptop microphone with push-to-talk
   (hold spacebar) or voice-activity detection (VAD)
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
   (local) and OpenAI (cloud)
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
- [ ] Set up dependency management (uv or pip with `requirements.txt`)
- [ ] Create configuration module (YAML or TOML config file for model paths,
      language, LLM backend, etc.)
- [ ] Add a basic CLI entry point (`python -m whispy` or `whispy` command)

### Phase 1 — Audio Capture
Get microphone input working reliably.

**Tasks:**
- [ ] Implement microphone recording with `sounddevice` (or `pyaudio`)
- [ ] Implement push-to-talk: hold spacebar to record, release to stop
- [ ] Save recorded audio to WAV buffer (in-memory, no temp files)
- [ ] Test with different mic configurations
- [ ] Fallback: simple "press Enter to start, Enter to stop" if keyboard
      listener is tricky in terminal

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
- [ ] Implement OpenAI client (using `openai` Python package)
- [ ] Create a common interface so backends are swappable via config
- [ ] Add conversation history (list of messages) for multi-turn context
- [ ] Write kid-friendly system prompt (age-appropriate, helpful, concise)
- [ ] Add language instruction to system prompt ("respond in French", etc.)
- [ ] Print response to terminal as "Assistant: ..."

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
| 10 | **Ollama backend** | Run with `--backend ollama` — works fully offline |
| 11 | **OpenAI backend** | Run with `--backend openai` — works with API key set |
| 12 | **Graceful exit** | Press Ctrl+C — app exits cleanly, no orphan processes |
| 13 | **No mic error** | Unplug mic / deny permission — app shows helpful error, doesn't crash |
| 14 | **Kid-safety check** | Ask something inappropriate — response is deflected or age-appropriate |

### Automated Tests (where practical)

- Unit tests for the LLM interface (mock Ollama/OpenAI responses)
- Unit tests for config loading
- Integration test: feed a pre-recorded WAV file through STT → LLM → TTS
  pipeline and verify each stage produces output

## Open Questions

See bottom of this document — these need answers before starting.

---

## Questions for You

1. **Push-to-talk vs. voice activity detection?**
   Push-to-talk (hold spacebar) is simpler and more reliable. VAD (auto-detect
   when someone is talking) is more natural but can be finicky with background
   noise and kids. **Recommendation: start with push-to-talk.** OK?

2. **Do you already have Ollama installed?**
   If yes, which models do you have? This helps me pick defaults. If not, I'll
   include setup instructions.

3. **OpenAI API key — do you have one?**
   If yes, I'll wire up the OpenAI backend from the start. If not, we can
   treat it as optional and focus on Ollama.

4. **Finnish TTS availability.**
   Piper has limited Finnish voice options. If Finnish TTS is important from
   day one, we may need to explore alternatives (e.g., using a cloud TTS
   API for Finnish only, or eSpeak with lower quality). **Is French + English
   sufficient for v1?**

5. **Dependency management preference?**
   Do you have a preference between `uv`, `pip` + `venv`, `poetry`, or
   `conda`? I'd suggest `uv` for simplicity — it's fast and handles venvs
   automatically.

6. **Apple Silicon or Intel Mac?**
   This affects whisper.cpp acceleration (Metal/CoreML on Apple Silicon) and
   Ollama performance. Most likely Apple Silicon given the target, but worth
   confirming.
