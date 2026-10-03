from __future__ import annotations

import re

import jiwer


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref = normalize_text(reference)
    hyp = normalize_text(hypothesis)
    if not ref and not hyp:
        return 0.0
    if not ref:
        return 1.0
    return jiwer.wer(ref, hyp)


def vocab_accuracy(reference: str, hypothesis: str, *, vocab: list[str]) -> float:
    if not vocab:
        return 1.0
    ref_lower = reference.lower()
    terms_in_ref = [term for term in vocab if term.lower() in ref_lower]
    if not terms_in_ref:
        return 1.0
    hyp_lower = hypothesis.lower()
    correct = sum(1 for term in terms_in_ref if term.lower() in hyp_lower)
    return correct / len(terms_in_ref)
