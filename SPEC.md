# Personal Dictation Tool — Spec

## Goal

A push-to-talk dictation tool for my Mac, and later my iPhone, that gets my voice right
more often than Whisper does. It is a personal tool and a way to learn agentic coding;
nothing in it has to work for anyone else.

v1 is done when I can hold a hotkey, speak, release, and cleaned-up text lands in whatever
app is active, and the engine I picked beats the Whisper baseline on my own eval set.

## Not in v1

- Other users, accounts, billing, installers or an app store build
- Windows or Linux desktop clients
- Live streaming transcription; transcribing after I release the key is fine
- Any UI beyond a menu-bar icon
- A fully offline mode; a local engine is optional and comes last

## Architecture

One Python package does the work: audio in, an engine, an optional cleanup pass, text
out. The Mac client, the phone server and the eval are thin callers around it.

```
dictate/
    core/           # Engine interface, pipeline, config (no macOS imports)
        engines/    # one file per provider
        cleanup.py  # LLM post-processing
    desktop/        # macOS hotkey client (Mac only)
    server/         # FastAPI endpoint for the phone
    eval/           # harness; data/ and results/ are gitignored
tests/
SPEC.md             # this doc
CLAUDE.md           # rules for the agent
NOTES.md            # decisions log
.env.example
```

## Engines

Every speech-to-text engine sits behind one small interface, so swapping engines is a
config change and the eval can run them all the same way.

```python
@dataclass
class Transcript:
    text: str
    engine: str
    latency_ms: int

class Engine(Protocol):
    name: str
    def transcribe(self, audio: bytes, *, vocab: list[str]) -> Transcript:
        ...
```

`vocab` is my list of names and technical terms. Engines that support boosting terms use
it; the rest ignore it and the cleanup step handles spelling.

Model IDs, request shapes and prices change, so the agent looks them up in each
provider's docs when it builds an engine instead of taking them from this spec.

**Cleanup step.** An optional LLM pass after transcription fixes punctuation and
capitalization, removes filler words, and corrects the spelling of my vocabulary terms. It
must never add content or change meaning. The eval runs every engine with and without it.

## Eval

The eval decides which engine I use, and no engine or cleanup change counts as an
improvement until the eval says so.

| Engine | Runs | Why |
|--------|------|-----|
| OpenAI Whisper API | Cloud | The baseline to beat |
| OpenAI's newer transcription model | Cloud | Likely the strongest drop-in upgrade |
| Deepgram Nova-3 | Cloud | Fast, and can boost my vocabulary terms |
| Whisper large-v3-turbo on Groq | Cloud | Tests whether speed alone fixes the experience |
| Parakeet via parakeet-mlx | Mac only | Free and offline; optional, added last |

Each clip is `eval/data/<id>.wav` plus `<id>.txt`, the text I meant to say with normal
punctuation. My vocabulary list lives in `eval/vocab.txt`. All of `eval/data/` is gitignored
because the recordings are private.

### Metrics

| Metric | How |
|--------|-----|
| Word error rate | jiwer, after lowercasing and stripping punctuation |
| Vocab accuracy | Share of vocab terms in the reference that come out spelled right |
| Latency | p50 and p90 per clip, in ms |
| Cost | Estimated $ per audio minute, from prices in config |

`dictate eval` prints the table and saves it to `eval/results/<date>.md`. Engine outputs
are cached by clip, engine and config, so rerunning the scoring never re-bills an API.

## Build phases

| Phase | What gets built | Done when | Where |
|-------|----------------|-----------|-------|
| 0. Skeleton | uv project, ruff, pytest, a `dictate` CLI, CLAUDE.md, NOTES.md, .env.example, .gitignore | `uv run pytest` passes and `dictate --help` works | Cloud |
| 1. Engines | The Engine interface and the four cloud engines; `dictate transcribe clip.wav --engine deepgram` | Unit tests with mocked HTTP pass; one live test per engine, skipped when its key is missing | Cloud |
| 2. Eval harness | `dictate eval`, scoring, caching, the results table | Produces the table for every engine on a small test fixture; a cached rerun makes no API calls | Cloud; first real run on my Mac |
| 3. Cleanup | The LLM cleanup step behind a config flag | Tests show filler removed and meaning kept on fixture text; eval reports with and without it | Cloud |
| 4. Mac client | Hold a hotkey, record, transcribe, paste into the active app, restore the clipboard | Works in Slack, a browser and the terminal | Mac only |
| 5. Phone | FastAPI POST /transcribe with a bearer token, plus an iOS Shortcut on the Action Button | The Shortcut puts cleaned text on my clipboard | Server in cloud; Shortcut on the phone |
| 6. Local engine (optional) | Parakeet through parakeet-mlx | Shows up as a row in the eval table | Mac only |

## Open questions

- Public or private repo?
- Which LLM does the cleanup, and is its extra latency worth it once the eval shows the gain?
- Hold-to-talk or press-to-toggle, and which key?
- Where does the phone server run: a small hosted service or a machine at home?
- Which providers get API keys first, and what's my monthly spending cap?
