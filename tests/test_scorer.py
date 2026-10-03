from __future__ import annotations

from dictate.eval.scorer import normalize_text, vocab_accuracy, word_error_rate


def test_normalize_text() -> None:
    assert normalize_text("Hello, World!") == "hello world"
    assert normalize_text("It's a test.") == "its a test"
    assert normalize_text("  multiple   spaces  ") == "multiple spaces"


def test_wer_perfect() -> None:
    assert word_error_rate("hello world", "hello world") == 0.0


def test_wer_completely_wrong() -> None:
    assert word_error_rate("hello world", "foo bar") == 1.0


def test_wer_partial() -> None:
    wer = word_error_rate("the quick brown fox", "the quick red fox")
    assert 0.0 < wer < 1.0


def test_wer_normalizes() -> None:
    wer = word_error_rate("Hello, World!", "hello world")
    assert wer == 0.0


def test_wer_empty_reference() -> None:
    wer = word_error_rate("", "")
    assert wer == 0.0


def test_vocab_accuracy_all_correct() -> None:
    reference = "I used pytest and ruff today"
    hypothesis = "I used pytest and ruff today"
    acc = vocab_accuracy(reference, hypothesis, vocab=["pytest", "ruff"])
    assert acc == 1.0


def test_vocab_accuracy_none_correct() -> None:
    reference = "I used pytest and ruff today"
    hypothesis = "I used pitest and rough today"
    acc = vocab_accuracy(reference, hypothesis, vocab=["pytest", "ruff"])
    assert acc == 0.0


def test_vocab_accuracy_partial() -> None:
    reference = "I used pytest and ruff today"
    hypothesis = "I used pytest and rough today"
    acc = vocab_accuracy(reference, hypothesis, vocab=["pytest", "ruff"])
    assert acc == 0.5


def test_vocab_accuracy_no_vocab_terms_in_reference() -> None:
    reference = "hello world"
    hypothesis = "hello world"
    acc = vocab_accuracy(reference, hypothesis, vocab=["pytest"])
    assert acc == 1.0


def test_vocab_accuracy_empty_vocab() -> None:
    acc = vocab_accuracy("hello", "hello", vocab=[])
    assert acc == 1.0
