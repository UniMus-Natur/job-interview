#!/usr/bin/env python3
"""CLI entrypoint for the Species Observations ETL pipeline.

Transforms raw observations from SQLite into Darwin Core CSV.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to sys.path if running as script
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pipeline import run_pipeline


def setup_logging(verbose: bool = False) -> None:
    """Configures console logging format and level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> None:
    """Main CLI command runner."""
    parser = argparse.ArgumentParser(
        description="Species Observation ETL: Transform SQLite observations to Darwin Core CSV."
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/observations.db",
        help="Path to source SQLite database file (default: data/observations.db)",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="output/dwc_occurrences.csv",
        help="Path to output Darwin Core CSV file (default: output/dwc_occurrences.csv)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed debug logs",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    try:
        results = run_pipeline(
            db_path=args.db_path,
            output_path=args.output_path,
        )
        print(f"\n[SUCCESS] Successfully processed {results['records_transformed']} records.")
        print(f"[SUCCESS] CSV file written to: {results['output_path']}")
    except Exception as e:
        logging.error(f"ETL pipeline failed: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
