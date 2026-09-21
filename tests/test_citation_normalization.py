"""Unit test for the normalizer itself — deterministic, no LLM call needed."""

from policyshadow.explanation.explainer import _normalize_citations


def test_normalizes_fullwidth_brackets():
    text = "This is grounded 【evidence.txt】 and this too [other.txt]."
    result = _normalize_citations(text)
    assert result == "This is grounded [evidence.txt] and this too [other.txt]."


def test_normalizes_bracket_whitespace():
    text = "See [ padded.txt ] and [tight.txt] and [  double  padded.txt  ]."
    result = _normalize_citations(text)
    assert result == "See [padded.txt] and [tight.txt] and [double  padded.txt]."
