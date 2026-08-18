"""Command line entry point: python -m dwc_etl"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .pipeline import run

DEFAULT_DATABASE = Path("data/observations.db")
DEFAULT_OUTPUT = Path("output/dwc_occurrences.csv")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dwc_etl",
        description="Transform raw species observations into Darwin Core occurrences.",
    )
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE,
                        help=f"source SQLite database (default: {DEFAULT_DATABASE})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"destination CSV (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--verbose", action="store_true", help="log each phase")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    try:
        written = run(args.database, args.output)
    except Exception as exc:                      # surfaced, never swallowed
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {written} occurrence(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
