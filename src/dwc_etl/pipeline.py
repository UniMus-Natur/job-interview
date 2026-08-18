"""Extract, transform and load phases, kept separate."""
from __future__ import annotations

import csv
import logging
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

from .transform import DWC_COLUMNS, to_occurrence

logger = logging.getLogger(__name__)

SOURCE_TABLE = "raw_observations"


def extract(database: Path, table: str = SOURCE_TABLE) -> list[dict[str, Any]]:
    """Read every raw observation. The source database is opened read-only."""
    if not database.exists():
        raise FileNotFoundError(f"database not found: {database}")

    uri = f"file:{database.as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()

    logger.info("extracted %d row(s) from %s", len(rows), database)
    return [dict(row) for row in rows]


def transform(rows: Iterable[Mapping[str, Any]]) -> Iterator[dict[str, str]]:
    """Map each raw row onto Darwin Core terms."""
    for row in rows:
        yield to_occurrence(row)


def load(
    occurrences: Iterable[Mapping[str, str]],
    destination: Path,
    columns: Sequence[str] = DWC_COLUMNS,
) -> int:
    """Write the occurrences to CSV. Returns the number of data rows written.

    UTF-8, comma-delimited, minimal quoting, and empty strings for absent
    values — never the literal 'None', 'null' or 'NaN'.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(columns), quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n", extrasaction="raise", restval="",
        )
        writer.writeheader()
        for occurrence in occurrences:
            writer.writerow(occurrence)
            written += 1

    logger.info("wrote %d occurrence(s) to %s", written, destination)
    return written


def run(database: Path, destination: Path) -> int:
    """Run the full pipeline and return the number of occurrences written."""
    return load(transform(extract(database)), destination)
