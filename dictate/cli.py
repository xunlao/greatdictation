from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

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
@click.option("--cleanup", "use_cleanup", is_flag=True, help="Run LLM cleanup on the result.")
def transcribe(
    audio_file: Path, engine: str, vocab_file: Path | None, use_cleanup: bool
) -> None:
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

    if use_cleanup:
        from dictate.core.cleanup import cleanup as run_cleanup

        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if not openai_key:
            click.echo("Error: OPENAI_API_KEY required for --cleanup.", err=True)
            sys.exit(1)
        result_text = run_cleanup(result.text, api_key=openai_key, vocab=vocab)
    else:
        result_text = result.text

    click.echo(result_text)


@main.command(name="eval")
@click.option(
    "--engine",
    multiple=True,
    type=click.Choice(AVAILABLE_ENGINES),
    help="Engines to evaluate (default: all with keys set).",
)
@click.option(
    "--data-dir",
    type=click.Path(exists=True, path_type=Path),
    default=Path("eval/data"),
    help="Directory with <id>.wav and <id>.txt clips.",
)
@click.option(
    "--vocab-file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option(
    "--results-dir",
    type=click.Path(path_type=Path),
    default=Path("eval/results"),
)
@click.option(
    "--cache-dir",
    type=click.Path(path_type=Path),
    default=Path("eval/cache"),
)
def eval_cmd(
    engine: tuple[str, ...],
    data_dir: Path,
    vocab_file: Path | None,
    results_dir: Path,
    cache_dir: Path,
) -> None:
    """Run the evaluation harness."""
    from dictate.eval.harness import EvalResult, load_clips, run_eval
    from dictate.eval.report import format_report, save_report

    clips = load_clips(data_dir)
    if not clips:
        click.echo(f"No clips found in {data_dir}. Add <id>.wav + <id>.txt pairs.", err=True)
        sys.exit(1)

    vocab: list[str] = []
    if vocab_file is not None:
        vocab = [line.strip() for line in vocab_file.read_text().splitlines() if line.strip()]

    engines_to_run = list(engine) if engine else [
        name for name, env_var in ENGINE_KEYS.items() if os.environ.get(env_var)
    ]
    if not engines_to_run:
        click.echo("No engines selected and no API keys found in environment.", err=True)
        sys.exit(1)

    from dictate.core.cleanup import CleanupConfig
    from dictate.core.cleanup import cleanup as run_cleanup

    openai_key = os.environ.get("OPENAI_API_KEY", "")
    cleanup_cfg: CleanupConfig | None = None
    if openai_key:
        cleanup_cfg = CleanupConfig(api_key=openai_key)

    all_results: dict[str, list[EvalResult]] = {}
    for eng_name in engines_to_run:
        env_var = ENGINE_KEYS[eng_name]
        api_key = os.environ.get(env_var, "")
        if not api_key:
            click.echo(f"Skipping {eng_name}: {env_var} not set.", err=True)
            continue
        eng = get_engine(eng_name, api_key=api_key)

        click.echo(f"Running {eng_name} (raw)...")
        results = run_eval(
            clips=clips, engine=eng, vocab=vocab, cache_dir=cache_dir, cleanup=False,
        )
        all_results[f"{eng_name}_raw"] = results

        if cleanup_cfg is not None:
            click.echo(f"Running {eng_name} (cleanup)...")

            def make_cleanup_fn(
                key: str, v: list[str], model: str
            ) -> Callable[[str], str]:
                def _fn(text: str) -> str:
                    return run_cleanup(text, api_key=key, vocab=v, model=model)
                return _fn

            cleanup_fn = make_cleanup_fn(openai_key, vocab, cleanup_cfg.config["model"])
            cleanup_results = run_eval(
                clips=clips,
                engine=eng,
                vocab=vocab,
                cache_dir=cache_dir,
                cleanup=True,
                cleanup_config=cleanup_cfg.config,
                cleanup_fn=cleanup_fn,
            )
            all_results[f"{eng_name}_cleanup"] = cleanup_results

    if not all_results:
        click.echo("No engines ran successfully.", err=True)
        sys.exit(1)

    report = format_report(all_results)
    click.echo(report)
    path = save_report(report, results_dir)
    click.echo(f"\nSaved to {path}")


@main.command()
def listen() -> None:
    """Start the hold-to-talk desktop client (Mac only)."""
    try:
        from dictate.desktop.app import run
    except ImportError:
        click.echo(
            "Desktop dependencies not installed. Run: uv pip install -e '.[mac]'",
            err=True,
        )
        sys.exit(1)
    run()
