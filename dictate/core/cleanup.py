from __future__ import annotations

from dataclasses import dataclass

import httpx

API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4.1-mini"

SYSTEM_PROMPT = (
    "You are a dictation post-processor. "
    "Fix punctuation, capitalization, and remove filler words (um, uh, like, you know, so). "
    "If a vocabulary list is provided, correct any misspelled vocabulary terms "
    "to their exact spelling. "
    "Do not add content, do not change meaning, and never add words "
    "that the speaker did not say. "
    "Return only the cleaned text, nothing else."
)


@dataclass
class CleanupConfig:
    api_key: str
    model: str = DEFAULT_MODEL

    @property
    def config(self) -> dict[str, str]:
        return {"model": self.model, "api_url": API_URL}


def cleanup(
    text: str,
    *,
    api_key: str | None = None,
    vocab: list[str] | None = None,
    model: str = DEFAULT_MODEL,
) -> str:
    if api_key is None:
        return text

    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    user_content = text
    if vocab:
        user_content = f"Vocabulary terms: {', '.join(vocab)}\n\nText: {text}"

    messages.append({"role": "user", "content": user_content})

    resp = httpx.post(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "messages": messages},
        timeout=30,
    )
    resp.raise_for_status()

    return resp.json()["choices"][0]["message"]["content"]
