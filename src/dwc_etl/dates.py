"""Date parsing for heterogeneous source formats.

Source dates arrive in several notations. Each is parsed with an explicit,
ordered set of format strings rather than a guessing heuristic, so an
unrecognised value fails loudly instead of being silently misread.

The day/month ordering of `DD/MM/YYYY` is the one genuinely ambiguous case
(`03/11/2022` is 3 November or 11 March depending on convention). The source
is European, and `14/08/2022` in the data can only be day-first, so day-first
is applied consistently and recorded here as an assumption rather than a
detection.
"""
from __future__ import annotations

from datetime import datetime
from typing import Final

# Ordered most-specific first. Formats carrying a time produce a full
# ISO 8601 timestamp; date-only formats produce YYYY-MM-DD.
_FORMATS: Final[tuple[tuple[str, bool], ...]] = (
    ("%Y-%m-%dT%H:%M:%S", True),
    ("%Y-%m-%d %H:%M:%S", True),
    ("%d/%m/%Y %H:%M:%S", True),
    ("%d/%m/%Y %H:%M", True),
    ("%Y-%m-%d", False),
    ("%d/%m/%Y", False),
    ("%d-%m-%Y", False),
    ("%d.%m.%Y", False),
    ("%B %d, %Y", False),   # June 4, 2021
    ("%b %d, %Y", False),   # Jun 4, 2021
    ("%d %B %Y", False),    # 4 June 2021
    ("%Y/%m/%d", False),
)


class UnparseableDate(ValueError):
    """Raised when a value matches none of the supported formats."""


def parse_event_date(raw: str | None) -> str:
    """Return an ISO 8601 date or datetime, or '' when there is no value.

    >>> parse_event_date("14/08/2022")
    '2022-08-14'
    >>> parse_event_date("June 4, 2021")
    '2021-06-04'
    >>> parse_event_date("2023-09-01 16:45:00")
    '2023-09-01T16:45:00'
    >>> parse_event_date(None)
    ''
    """
    if raw is None:
        return ""
    value = raw.strip()
    if not value:
        return ""

    for fmt, has_time in _FORMATS:
        try:
            parsed = datetime.strptime(value, fmt)
        except ValueError:
            continue
        return parsed.strftime("%Y-%m-%dT%H:%M:%S" if has_time else "%Y-%m-%d")

    raise UnparseableDate(f"unrecognised date format: {raw!r}")
