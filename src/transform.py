"""Transform module for Species Observation ETL.

Handles data cleaning, taxonomy parsing, date normalization,
and Darwin Core standard vocabulary mapping.
"""

from datetime import datetime
import re
from typing import Any, Dict, List, Optional, Tuple

# Darwin Core basisOfRecord controlled vocabulary mapping
BASIS_OF_RECORD_MAPPING = {
    "human_observation": "HumanObservation",
    "visual": "HumanObservation",
    "field_notes": "HumanObservation",
    "camera_trap": "MachineObservation",
    "museum_specimen": "PreservedSpecimen",
}

# Regex pattern to separate scientific taxon names from authorship
# Matches Genus + species (+ subspecies) in group 1, and authorship in group 2
TAXON_AUTH_PATTERN = re.compile(
    r"^([A-Z][a-z]+(?:\s+[a-z\-]+)*)(?:\s+([\(\[]?[A-Z].*|\d{4}.*))?$"
)

# Supported input date/datetime formats in prioritized order
DATE_FORMATS = [
    ("%Y-%m-%d %H:%M:%S", True),
    ("%Y-%m-%dT%H:%M:%S", True),
    ("%d/%m/%Y %H:%M:%S", True),
    ("%d/%m/%Y", False),
    ("%Y-%m-%d", False),
    ("%B %d, %Y", False),
    ("%b %d, %Y", False),
    ("%d-%m-%Y", False),
    ("%m/%d/%Y", False),
]


def parse_date_to_iso(date_str: Optional[str]) -> str:
    """Parses a date or datetime string into standard ISO 8601 format.

    Returns:
        ISO 8601 formatted string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).
        If input is empty or unparseable, returns empty string.
    """
    if not date_str or not str(date_str).strip():
        return ""

    cleaned = str(date_str).strip()

    for fmt, has_time in DATE_FORMATS:
        try:
            dt = datetime.strptime(cleaned, fmt)
            if has_time:
                return dt.strftime("%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # If already in valid ISO format with time zone or seconds, try fromisoformat
    try:
        dt = datetime.fromisoformat(cleaned)
        if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and "T" not in cleaned and " " not in cleaned:
            return dt.strftime("%Y-%m-%d")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass

    return cleaned


def parse_taxon_name(taxon_str: Optional[str]) -> Tuple[str, str]:
    """Splits a raw taxonomic name into scientificName and scientificNameAuthorship.

    Args:
        taxon_str: Raw taxon string (e.g. "Canis lupus Linnaeus, 1758").

    Returns:
        Tuple of (scientificName, scientificNameAuthorship).
    """
    if not taxon_str or not str(taxon_str).strip():
        return "", ""

    cleaned = str(taxon_str).strip()
    match = TAXON_AUTH_PATTERN.match(cleaned)

    if match:
        name = match.group(1).strip() if match.group(1) else ""
        authorship = match.group(2).strip() if match.group(2) else ""
        return name, authorship

    return cleaned, ""


def map_basis_of_record(record_type: Optional[str]) -> str:
    """Maps internal/source record_type to Darwin Core basisOfRecord standard term.

    Args:
        record_type: Raw record type from source database.

    Returns:
        Standard DwC basisOfRecord string.
    """
    if not record_type or not str(record_type).strip():
        return "HumanObservation"

    cleaned = str(record_type).strip().lower()
    return BASIS_OF_RECORD_MAPPING.get(cleaned, "HumanObservation")


def _format_int_or_empty(val: Any) -> str:
    """Formats an integer or returns empty string if null/None."""
    if val is None or str(val).strip() == "" or str(val).lower() in ("none", "null", "nan"):
        return ""
    try:
        return str(int(float(val)))
    except (ValueError, TypeError):
        return ""


def _format_float_or_empty(val: Any) -> str:
    """Formats a float or returns empty string if null/None."""
    if val is None or str(val).strip() == "" or str(val).lower() in ("none", "null", "nan"):
        return ""
    try:
        f = float(val)
        return f"{f:g}"
    except (ValueError, TypeError):
        return ""


def _format_str_or_empty(val: Any) -> str:
    """Cleans string value or returns empty string if null/None."""
    if val is None or str(val).lower() in ("none", "null", "nan"):
        return ""
    return str(val).strip()


def transform_record(raw: Dict[str, Any]) -> Dict[str, str]:
    """Transforms a single raw database observation record into a Darwin Core occurrence record.

    Args:
        raw: Dictionary representing a row from raw_observations.

    Returns:
        Dictionary with Darwin Core column names and formatted values.
    """
    sci_name, sci_authorship = parse_taxon_name(raw.get("taxon_name"))

    return {
        "occurrenceID": _format_str_or_empty(raw.get("obs_code")),
        "basisOfRecord": map_basis_of_record(raw.get("record_type")),
        "scientificName": sci_name,
        "scientificNameAuthorship": sci_authorship,
        "vernacularName": _format_str_or_empty(raw.get("vernacular")),
        "individualCount": _format_int_or_empty(raw.get("count")),
        "eventDate": parse_date_to_iso(raw.get("obs_date")),
        "decimalLatitude": _format_float_or_empty(raw.get("lat")),
        "decimalLongitude": _format_float_or_empty(raw.get("lon")),
        "coordinateUncertaintyInMeters": _format_int_or_empty(raw.get("coordinate_accuracy_meters")),
        "locality": _format_str_or_empty(raw.get("locality_name")),
        "recordedBy": _format_str_or_empty(raw.get("observer")),
        "occurrenceRemarks": _format_str_or_empty(raw.get("notes")),
    }


def transform_all(records: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Transforms a list of raw observation records into Darwin Core records.

    Args:
        records: List of raw database row dictionaries.

    Returns:
        List of Darwin Core transformed dictionaries.
    """
    return [transform_record(r) for r in records]
