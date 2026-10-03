# NOTES

## 2026-10-03 (Phase 6)
- Parakeet local engine via parakeet-mlx (mlx-community/parakeet-tdt-0.6b-v3).
- Lazy-loaded: model downloaded on first transcribe call, reused for subsequent calls.
- Takes file path not bytes, so audio is written to a temp file before transcription.
- No API key required — registered in ENGINE_KEYS with empty string env var.
- parakeet-mlx is an optional extra (`pip install .[local]`).
- Registry, CLI eval, and server all updated to handle keyless engines.

## 2026-10-03 (Phase 5)
- FastAPI server: POST /transcribe with bearer token auth (DICTATE_API_TOKEN env var).
- Accepts audio file upload, optional engine param. Returns `{"text": "..."}`.
- Cleanup runs when DICTATE_CLEANUP=1 and OPENAI_API_KEY is set.
- Server deps (fastapi, python-multipart, uvicorn) are optional extras (`pip install .[server]`).
- `dictate serve` CLI command starts uvicorn. Health check at GET /health.
- iOS Shortcut design: Action Button → record audio → POST to server → copy result to clipboard.
- HTTPBearer returns 401 for missing auth, 403 for wrong token — FastAPI's default behavior.

## 2026-10-03 (Phase 4)
- Mac desktop client: hold-to-talk dictation with Right Option key.
- Quartz CGEventTap for global hotkey (kCGEventFlagsChanged on keycode 61). Requires Accessibility permission.
- sounddevice for mic recording — bundles PortAudio, clean blocking API.
- pyobjc NSPasteboard for clipboard save/restore, CGEventPost for synthetic Cmd+V paste.
- macOS-only deps (sounddevice, pyobjc-framework-Cocoa, pyobjc-framework-Quartz) are optional extras (`pip install .[mac]`), keeping core cross-platform.
- `dictate listen` command as entry point, with ImportError fallback message for non-Mac platforms.
- Recordings under 0.3s are discarded (accidental taps).
- Test mocking: each test fixture must invalidate cached desktop module imports (`monkeypatch.delitem`) so fresh mocks bind correctly.

## 2026-10-02 (Phase 3)
- LLM cleanup step using OpenAI chat completions (gpt-4.1-mini by default).
- System prompt instructs: fix punctuation/caps, remove filler words, correct vocab spelling, never add content.
- CleanupConfig exposes `config` property so cache fingerprint captures model/URL.
- Eval harness runs each engine both raw and with cleanup when OPENAI_API_KEY is set.
- `dictate transcribe --cleanup` flag for CLI usage.
- Note: gpt-4.1-nano scheduled for shutdown 2026-10-23; using gpt-4.1-mini instead.

## 2026-10-02 (Phase 2)
- Eval harness: scorer (WER via jiwer, vocab accuracy), cache (JSON per clip/engine/config), harness runner, report formatter.
- Cache keyed by `{clip_id}_{engine}_{fingerprint}.json` where fingerprint is a 12-char SHA-256 of engine config + vocab + cleanup config — rerunning scoring makes zero API calls; changing any of those invalidates the cache.
- Cost estimates hardcoded per engine for now; prices from provider docs at time of implementation.
- Added jiwer as runtime dep for WER scoring (uses rapidfuzz under the hood).

## 2026-10-03
- Phase 1: Four cloud engines implemented.
- OpenAI Whisper (`whisper-1`) as baseline; OpenAI's newer `gpt-transcribe` (released July 2026) as the upgrade.
- Deepgram uses `keyterm` param (not `keywords`) for Nova-3 vocab boosting.
- Groq is OpenAI-compatible endpoint with `whisper-large-v3-turbo`.
- OpenAI and Groq engines pass vocab as a `prompt` field; Deepgram uses `keyterm` query params.
- Added httpx as a runtime dependency for all engine HTTP calls.
- Note: `whisper-1` deprecated Aug 2026, removal Feb 2027. `gpt-transcribe` is the long-term replacement.

## 2026-10-02
- Phase 0: Skeleton created. uv project with ruff, pytest, click CLI.
- Dependencies: click (CLI framework), pytest/ruff/respx/httpx (dev).
