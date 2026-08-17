"""Pipeline coordinator module for Species Observation ETL."""

import logging
from pathlib import Path
from typing import Dict, Optional

from src.extract import extract_raw_observations
from src.load import load_to_csv
from src.transform import transform_all

logger = logging.getLogger(__name__)


def run_pipeline(
    db_path: str | Path = "data/observations.db",
    output_path: str | Path = "output/dwc_occurrences.csv",
) -> Dict[str, any]:
    """Executes the full Species Observation ETL pipeline.

    Args:
        db_path: Path to the source SQLite database.
        output_path: Path to the target Darwin Core CSV.

    Returns:
        Dictionary containing summary execution statistics.
    """
    logger.info("Starting Species Observation ETL pipeline...")
    logger.info(f"Extracting observations from: {db_path}")

    raw_records = extract_raw_observations(db_path)
    logger.info(f"Extracted {len(raw_records)} records from source database.")

    logger.info("Transforming records to Darwin Core standards...")
    dwc_records = transform_all(raw_records)

    logger.info(f"Writing {len(dwc_records)} records to {output_path}...")
    saved_path = load_to_csv(dwc_records, output_path)
    logger.info(f"ETL pipeline completed successfully. Output saved to: {saved_path}")

    return {
        "status": "success",
        "records_extracted": len(raw_records),
        "records_transformed": len(dwc_records),
        "output_path": str(saved_path),
    }
