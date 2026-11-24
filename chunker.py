import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import tiktoken


def clean_rfc_text(raw: str) -> str:
    """Remove page breaks, headers, and footers from RFC text.

    A typical page boundary looks like:
        last line of body text
        (blank lines)
        [Page N]
        \f
        RFC xxxx ... date
        (two blank lines)
        first line of next page

    If the next page starts with an unindented line, keep one blank
    line to separate sections. Otherwise, keep no blank line.

    This may merge separate paragraphs, but avoids splits within
    sentences or diagrams.
    """

    pieces = raw.split("\f")
    pages: list[str] = []
    for i, piece in enumerate(pieces):
        lines = piece.strip("\n").split("\n")
        if i > 0:
            # drop the header, except in the first piece
            lines = lines[1:]
        if i < len(pieces) - 1:
            # drop the footer, except in the last piece
            lines = lines[:-1]
        # drop blank lines around header and footer
        page = "\n".join(lines).strip("\n")
        if page:
            pages.append(page)

    text = pages[0]
    for page in pages[1:]:
        text += ("\n" if page[0].isspace() else "\n\n") + page
    return text


def split_paragraphs(text: str) -> list[str]:
    # one or more blank lines is two or more \n in a row
    return re.split(r"\n\n+", text)


def split_oversized(text: str, max_tokens: int,
                    count: Callable[[str], int]) -> list[str]:
    """Split a paragraph by lines into pieces of at most max_tokens."""
    pieces: list[str] = []
    current = ""
    for line in text.split("\n"):
        candidate = line if not current else current + "\n" + line
        if count(candidate) <= max_tokens:
            current = candidate
        else:
            pieces.append(current)
            current = line
    pieces.append(current)
    return pieces


def _overlap_tail(prev_chunk: str, piece: str, overlap_tokens: int,
                  max_tokens: int, count: Callable[[str], int]) -> str:
    """Copy the last few lines of the previous chunk to the start of the new chunk as overlap.
    The overlap plus piece must fit in max_tokens.
    If possible, start at the first line of a paragraph.
    """
    lines = prev_chunk.split("\n")

    start = len(lines)
    para_start = None

    while start > 0:
        tail = "\n".join(lines[start - 1:])
        if count(tail) > overlap_tokens or count(tail + "\n\n" + piece) > max_tokens:
            break
        start -= 1
        if start == 0 or not lines[start - 1]:
            para_start = start

    if para_start is not None:
        start = para_start
    return "\n".join(lines[start:])


def chunk_text(text: str, max_tokens: int, overlap_tokens: int,
               count: Callable[[str], int]) -> list[str]:
    """Split cleaned text into chunks.
    The unit is a paragraph. If it fits, add it to the current chunk. If not, start a new chunk.
    """
    # each chunk has at most max_tokens tokens
    pieces: list[str] = []
    for paragraph in split_paragraphs(text):
        pieces.extend(split_oversized(paragraph, max_tokens, count))

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = piece if not current else current + "\n\n" + piece
        if count(candidate) <= max_tokens:
            current = candidate
            continue

        # piece does not fit, so close the current chunk
        chunks.append(current)

        tail = _overlap_tail(current, piece, overlap_tokens, max_tokens, count)
        current = piece if not tail else tail + "\n\n" + piece

    chunks.append(current)
    return chunks


_ENCODING = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_ENCODING.encode(text))


@dataclass
class Chunk:
    text: str    # text of the chunk
    source: str  # the RFC it comes from
    index: int   # position of the chunk in this RFC, from 0


def load_rfc_chunks(path: str | Path, max_tokens: int = 400,
                    overlap_tokens: int = 50) -> list[Chunk]:
    """Read one RFC, clean it, split it into chunks, and record the source of each chunk."""
    text = clean_rfc_text(Path(path).read_text(encoding="utf-8"))
    # rfc4271.txt -> RFC 4271
    source = f"RFC {Path(path).stem.removeprefix('rfc')}"
    texts = chunk_text(text, max_tokens, overlap_tokens, count_tokens)
    return [Chunk(text=t, source=source, index=i) for i, t in enumerate(texts)]


def load_rfc_dir(dir: str | Path, max_tokens: int = 400,
                 overlap_tokens: int = 50) -> list[Chunk]:
    """Read all rfc*.txt files in dir."""
    chunks: list[Chunk] = []
    for path in sorted(Path(dir).glob("rfc*.txt")):
        chunks.extend(load_rfc_chunks(path, max_tokens, overlap_tokens))
    return chunks
