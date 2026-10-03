from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from dictate.core.engines.registry import AVAILABLE_ENGINES, ENGINE_KEYS, get_engine
from dictate.core.pipeline import transcribe as pipeline_transcribe


@click.group()
@click.version_option(package_name="dictate")
def main() -> None:
    """Personal push-to-talk dictation tool."""


@main.command()
@click.argument("audio_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--engine",
    default="openai-whisper",
    type=click.Choice(AVAILABLE_ENGINES),
    help="STT engine to use.",
)
@click.option("--vocab-file", type=click.Path(exists=True, path_type=Path), default=None)
def transcribe(audio_file: Path, engine: str, vocab_file: Path | None) -> None:
    """Transcribe an audio file."""
    env_var = ENGINE_KEYS[engine]
    api_key = os.environ.get(env_var, "")
    if not api_key:
        click.echo(f"Error: {env_var} environment variable is not set.", err=True)
        sys.exit(1)

    vocab: list[str] = []
    if vocab_file is not None:
        vocab = [line.strip() for line in vocab_file.read_text().splitlines() if line.strip()]

    audio = audio_file.read_bytes()
    eng = get_engine(engine, api_key=api_key)
    result = pipeline_transcribe(audio, engine=eng, vocab=vocab)

    click.echo(result.text)


@main.command(name="eval")
def eval_cmd() -> None:
    """Run the evaluation harness."""
    click.echo("Eval harness not yet implemented (Phase 2)")
