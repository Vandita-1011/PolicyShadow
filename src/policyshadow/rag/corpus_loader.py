"""Loads and chunks the knowledge corpus (paragraph-level chunks)."""

from pathlib import Path

CORPUS_DIR = Path(__file__).parent / "corpus"


def load_chunks() -> list[dict]:
    chunks = []
    for path in sorted(CORPUS_DIR.glob("*.txt")):
        text = path.read_text().strip()
        for para in text.split("\n\n"):
            para = para.strip()
            if para:
                chunks.append({"source": path.name, "text": para})
    return chunks
