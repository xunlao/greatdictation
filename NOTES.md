# NOTES

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
