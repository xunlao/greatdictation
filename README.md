# greatdictation

Personal push-to-talk dictation tool for Mac and iPhone. Hold a hotkey (or press the Action Button), speak, and cleaned-up text lands wherever your cursor is.

## Quick start

```bash
# Clone and install
git clone https://github.com/xunlao/greatdictation.git
cd greatdictation
uv sync

# Set at least one engine key
export OPENAI_API_KEY=sk-...

# Transcribe a file
dictate transcribe recording.wav

# With LLM cleanup (fixes punctuation, removes filler words)
dictate transcribe recording.wav --cleanup
```

## Desktop client (Mac)

Hold Right Option to record, release to transcribe and paste into the active app.

```bash
uv pip install -e '.[mac]'
export OPENAI_API_KEY=sk-...
dictate listen
```

Requires Accessibility permission: System Settings > Privacy & Security > Accessibility, then add your terminal.

### Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DICTATE_ENGINE` | `openai-whisper` | STT engine to use |
| `DICTATE_CLEANUP` | `0` | Set to `1` to enable LLM cleanup |
| `DICTATE_VOCAB_FILE` | | Path to a text file with one term per line |

## Phone server

A FastAPI endpoint for an iOS Shortcut on the Action Button.

```bash
uv pip install -e '.[server]'
export DICTATE_API_TOKEN=your-secret-token
export OPENAI_API_KEY=sk-...
dictate serve --host 0.0.0.0 --port 8000
```

**Endpoints:**

- `POST /transcribe` — upload audio, get text back. Requires `Authorization: Bearer <token>`.
- `GET /health` — returns `{"status": "ok"}`.

**iOS Shortcut:** Action Button > Record Audio > Get Contents of URL (POST multipart to `https://your-server/transcribe` with Bearer header) > Copy to Clipboard.

## Engines

Every engine implements the same interface, so swapping is a config change.

| Engine | Env var | Notes |
|--------|---------|-------|
| `openai-whisper` | `OPENAI_API_KEY` | Whisper-1, the baseline |
| `openai-transcribe` | `OPENAI_API_KEY` | gpt-transcribe, newer model |
| `deepgram` | `DEEPGRAM_API_KEY` | Nova-3, supports vocab boosting via keyterms |
| `groq` | `GROQ_API_KEY` | whisper-large-v3-turbo, fast |
| `parakeet` | (none) | Local, offline via parakeet-mlx on Apple Silicon |

```bash
# Use a specific engine
dictate transcribe recording.wav --engine deepgram

# Local engine (no API key needed)
uv pip install -e '.[local]'
dictate transcribe recording.wav --engine parakeet
```

## Eval

Compare engines on your own recordings. Each clip is `eval/data/<id>.wav` + `<id>.txt` (the text you meant to say). Vocabulary terms go in `eval/vocab.txt`.

```bash
# Run all engines that have keys set
dictate eval --data-dir eval/data --vocab-file eval/vocab.txt

# Run specific engines
dictate eval --engine deepgram --engine openai-transcribe
```

Metrics: word error rate (WER), vocab accuracy, latency (p50/p90), estimated cost per audio minute. Results are cached by clip, engine, and config — rerunning never re-bills an API. When `OPENAI_API_KEY` is set, each engine is evaluated both raw and with LLM cleanup.

## Project structure

```
dictate/
    core/           # Engine interface, pipeline, config (no macOS imports)
        engines/    # One file per provider
        cleanup.py  # LLM post-processing via OpenAI
    desktop/        # macOS hotkey client
    server/         # FastAPI endpoint for phone
    eval/           # Harness, scorer, cache, report
tests/              # Mocked unit tests + live tests (skipped without keys)
```

## Development

```bash
uv sync
uv run ruff check
uv run pytest
```

Live tests (hit real APIs) are skipped when the corresponding key is missing. Run them explicitly:

```bash
export OPENAI_API_KEY=sk-...
uv run pytest -m live
```

## Optional dependency groups

| Extra | Install | What |
|-------|---------|------|
| `mac` | `uv pip install -e '.[mac]'` | sounddevice, pyobjc (desktop client) |
| `server` | `uv pip install -e '.[server]'` | FastAPI, uvicorn (phone endpoint) |
| `local` | `uv pip install -e '.[local]'` | parakeet-mlx (offline engine, Apple Silicon) |
