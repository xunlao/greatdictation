from __future__ import annotations

import click


@click.group()
@click.version_option(package_name="dictate")
def main() -> None:
    """Personal push-to-talk dictation tool."""


@main.command()
@click.argument("audio_file", type=click.Path(exists=True))
@click.option("--engine", default="openai-whisper", help="STT engine to use.")
def transcribe(audio_file: str, engine: str) -> None:
    """Transcribe an audio file."""
    click.echo(f"Transcribing {audio_file} with engine '{engine}' (not yet implemented)")


@main.command(name="eval")
def eval_cmd() -> None:
    """Run the evaluation harness."""
    click.echo("Eval harness not yet implemented (Phase 2)")
