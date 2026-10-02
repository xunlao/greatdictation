# CLAUDE.md

## Project
Personal push-to-talk dictation tool. The spec is SPEC.md; read it before starting a phase.

## Stack
Python 3.12, uv, ruff, pytest, type hints everywhere.

## Rules
- Work one phase at a time, on its own branch.
- Write the tests for a phase before the code.
- Keep dictate/core free of macOS-only imports so it runs on Linux.
- Every engine gets tests with mocked HTTP. Live tests skip when the key is missing.
- Never commit API keys, recordings, eval/data/ or eval/vocab.txt. Keys come from environment variables.
- Look up current model IDs and API shapes in each provider's docs. Don't guess them.
- Don't add a dependency without saying why in the PR description.
- Ask before changing the Engine interface.

## Notes
Log decisions, dead ends and anything surprising in NOTES.md, newest first.
