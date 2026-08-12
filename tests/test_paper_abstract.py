"""The abstract has to stay inside the journal's 150-250 word window."""

from __future__ import annotations

from pathlib import Path
import re


PAPER = Path(__file__).resolve().parents[1] / "paper"


def abstract_words() -> list[str]:
    source = (PAPER / "focus.tex").read_text(encoding="utf-8")
    body = source.split(r"\abstract{", 1)[1].split(r"\keywords", 1)[0]
    body = re.sub(r"\$[^$]*\$", " MATH ", body)  # one inline formula, one word
    body = re.sub(r"\\[a-zA-Z]+|[${}\\]", " ", body).replace("---", " ")
    return [word for word in body.split() if re.search(r"[A-Za-z]", word)]


def test_abstract_length() -> None:
    assert 150 <= len(abstract_words()) <= 250
