from __future__ import annotations

import os
import sys
import time

import click


def _get_config() -> dict[str, str]:
    """Read config from environment."""
    engine_name = os.environ.get("DICTATE_ENGINE", "openai-whisper")
    cleanup = os.environ.get("DICTATE_CLEANUP", "0")
    return {"engine": engine_name, "cleanup": cleanup}


def run() -> None:
    """Main entry point for the Mac desktop client."""
    from dictate.core.engines.registry import ENGINE_KEYS, get_engine
    from dictate.desktop.hotkey import HoldToTalkListener
    from dictate.desktop.paste import paste_text, restore_clipboard, save_clipboard
    from dictate.desktop.recorder import record_audio

    config = _get_config()
    engine_name = config["engine"]
    use_cleanup = config["cleanup"] == "1"

    env_var = ENGINE_KEYS[engine_name]
    api_key = os.environ.get(env_var, "")
    if not api_key:
        click.echo(f"Error: {env_var} not set.", err=True)
        sys.exit(1)

    engine = get_engine(engine_name, api_key=api_key)

    vocab: list[str] = []
    vocab_path = os.environ.get("DICTATE_VOCAB_FILE")
    if vocab_path and os.path.exists(vocab_path):
        with open(vocab_path) as f:
            vocab = [line.strip() for line in f if line.strip()]

    recording = False
    record_start: float = 0.0

    def on_press() -> None:
        nonlocal recording, record_start
        recording = True
        record_start = time.monotonic()
        click.echo("Recording...", err=True)

    def on_release() -> None:
        nonlocal recording
        if not recording:
            return
        recording = False
        duration = time.monotonic() - record_start

        if duration < 0.3:
            click.echo("Too short, skipping.", err=True)
            return

        click.echo("Transcribing...", err=True)

        audio = record_audio(duration_s=duration)
        transcript = engine.transcribe(audio, vocab=vocab)
        text = transcript.text

        if use_cleanup:
            openai_key = os.environ.get("OPENAI_API_KEY", "")
            if openai_key:
                from dictate.core.cleanup import cleanup

                text = cleanup(text, api_key=openai_key, vocab=vocab)

        old_clipboard = save_clipboard()
        paste_text(text)
        time.sleep(0.1)
        restore_clipboard(old_clipboard)

        click.echo(f"Pasted: {text}", err=True)

    click.echo(
        f"Dictation ready (engine={engine_name}, cleanup={'on' if use_cleanup else 'off'}). "
        "Hold Right Option to talk. Ctrl+C to quit.",
        err=True,
    )

    listener = HoldToTalkListener(on_press=on_press, on_release=on_release)
    try:
        listener.start()
    except KeyboardInterrupt:
        listener.stop()
        click.echo("\nStopped.", err=True)
