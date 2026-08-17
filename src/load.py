"""Load module for Species Observation ETL.

Exports transformed Darwin Core records to a clean CSV file.
"""

import csv
from pathlib import Path
from typing import Dict, List

# Target Darwin Core headers in exact expected order
DWC_HEADERS = [
    "occurrenceID",
    "basisOfRecord",
    "scientificName",
    "scientificNameAuthorship",
    "vernacularName",
    "individualCount",
    "eventDate",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters",
    "locality",
    "recordedBy",
    "occurrenceRemarks",
]


def load_to_csv(records: List[Dict[str, str]], output_path: str | Path) -> Path:
    """Writes Darwin Core occurrence records to a CSV file.

    Args:
        records: List of transformed record dictionaries.
        output_path: Target CSV file path.

    Returns:
        Path object to the written CSV file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, mode="w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=DWC_HEADERS,
            delimiter=",",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            # Filter and sanitize row according to headers
            row = {field: record.get(field, "") for field in DWC_HEADERS}
            writer.writerow(row)

    return path
