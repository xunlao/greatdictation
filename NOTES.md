# NOTES

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
