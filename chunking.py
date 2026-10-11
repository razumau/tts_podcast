import math
import re
from collections.abc import Iterator

PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")


def split_text(text: str, max_chars: int) -> list[str]:
    """Split text into as few parts of at most max_chars as possible, keeping the parts about the same length.

    Parts break between paragraphs when that keeps them reasonably even, otherwise between sentences.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    by_sentence = _partition(list(_units(text, max_chars, by_sentence=True)), max_chars)
    by_paragraph = _partition(list(_units(text, max_chars, by_sentence=False)), max_chars)
    if len(by_paragraph) == len(by_sentence) and min(map(len, by_paragraph)) >= len(text) / len(by_paragraph) / 2:
        return by_paragraph
    return by_sentence


def _units(text: str, max_chars: int, by_sentence: bool) -> Iterator[tuple[str, str]]:
    """Yield (separator before the unit, unit): paragraphs or sentences, and words of sentences over max_chars.

    A word longer than max_chars (no real article has one) is cut into pieces.
    """
    for paragraph in PARAGRAPH_BREAK.split(text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        separator = "\n\n"
        if not by_sentence and len(paragraph) <= max_chars:
            yield separator, paragraph
            continue
        for sentence in SENTENCE_END.split(paragraph):
            if len(sentence) <= max_chars:
                yield separator, sentence
            else:
                for word in sentence.split():
                    for start in range(0, len(word), max_chars):
                        yield separator, word[start : start + max_chars]
                        separator = " "
            separator = " "


def _partition(units: list[tuple[str, str]], max_chars: int) -> list[str]:
    """Pack units into as few parts as possible, making the longest part as short as possible."""
    # Greedy packing gives the fewest parts, but leaves the last one short: 1,000 + 1,000 + 100
    parts_count = len(_pack(units, max_chars))
    total = sum(len(separator) + len(unit) for separator, unit in units)
    low = max(math.ceil(total / parts_count), *(len(unit) for _, unit in units))
    high = max_chars
    while low < high:
        cap = (low + high) // 2
        if len(_pack(units, cap)) <= parts_count:
            high = cap
        else:
            low = cap + 1
    return _pack(units, low)


def _pack(units: list[tuple[str, str]], cap: int) -> list[str]:
    parts, current = [], ""
    for separator, unit in units:
        if not current:
            current = unit
        elif len(current) + len(separator) + len(unit) > cap:
            parts.append(current)
            current = unit
        else:
            current += separator + unit
    if current:
        parts.append(current)
    return parts
