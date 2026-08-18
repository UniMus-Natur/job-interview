"""Separation of a scientific name from its authorship.

Authorship is identified by its own structure rather than by position, because
position is unreliable: `Rupicapra rupicapra tatrica` is a three-part name with
no author, and a rule that treats everything after the second word as authorship
would silently discard the subspecies epithet.

Authorship is recognised when it is either parenthesised, or begins with a
capitalised surname and contains a four-digit year.
"""
from __future__ import annotations

import re
from typing import Final, NamedTuple

# (Linnaeus, 1758) — parenthesised authorship, anchored to the end of the string
_PARENTHESISED: Final = re.compile(r"\s*(\((?:[^()]*)\))\s*$")

# Linnaeus, 1758 / L., 1758 / Müller & Schmidt, 1801 — a capitalised token
# followed by anything ending in a four-digit year
_BARE: Final = re.compile(
    r"\s+("
    r"[A-ZÀ-Þ][\w.'’-]*"          # a capitalised surname or abbreviation
    r"(?:\s*(?:&|and|et)\s*[A-ZÀ-Þ][\w.'’-]*)*"   # optional co-authors
    r"\s*,\s*\d{4}"               # , 1758
    r")\s*$"
)


class ParsedName(NamedTuple):
    """A scientific name split from its authorship."""

    scientific_name: str
    authorship: str


def split_authorship(raw: str | None) -> ParsedName:
    """Split `taxon_name` into the name and its authorship.

    >>> split_authorship("Canis lupus Linnaeus, 1758")
    ParsedName(scientific_name='Canis lupus', authorship='Linnaeus, 1758')
    >>> split_authorship("Lynx lynx (Linnaeus, 1758)")
    ParsedName(scientific_name='Lynx lynx', authorship='(Linnaeus, 1758)')
    >>> split_authorship("Rupicapra rupicapra tatrica")
    ParsedName(scientific_name='Rupicapra rupicapra tatrica', authorship='')
    """
    if raw is None:
        return ParsedName("", "")

    value = re.sub(r"\s+", " ", raw).strip()
    if not value:
        return ParsedName("", "")

    for pattern in (_PARENTHESISED, _BARE):
        match = pattern.search(value)
        if match:
            name = value[: match.start()].strip()
            if name:                       # never return an empty name
                return ParsedName(name, match.group(1).strip())

    return ParsedName(value, "")
