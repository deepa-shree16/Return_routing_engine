
from pathlib import Path
from typing import List


def read_file(path: str) -> str:
    """Reads an entire file into a string. Raises FileNotFoundError if missing."""
    return Path(path).read_text(encoding="utf-8")


def read_lines(path: str) -> List[str]:
    """Reads a file and returns its non-empty, non-whitespace-only lines
    (used for .jsonl files, one JSON object per line)."""
    text = Path(path).read_text(encoding="utf-8")
    return [line for line in text.splitlines() if line.strip()]


def write_lines(path: str, lines: List[str]) -> None:
    """Writes a list of strings to a file, one per line (overwrites existing content)."""
    Path(path).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
