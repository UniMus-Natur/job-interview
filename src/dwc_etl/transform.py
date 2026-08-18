"""Mapping of a raw observation row onto Darwin Core terms."""
from __future__ import annotations

from typing import Any, Final, Mapping

from .dates import parse_event_date
from .names import split_authorship

# DwC column order. The CSV header must match this exactly.
DWC_COLUMNS: Final[tuple[str, ...]] = (
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
)

# Source record types mapped onto the DwC basisOfRecord controlled vocabulary.
BASIS_OF_RECORD: Final[Mapping[str, str]] = {
    "human_observation": "HumanObservation",
    "visual": "HumanObservation",
    "field_notes": "HumanObservation",
    "camera_trap": "MachineObservation",
    "museum_specimen": "PreservedSpecimen",
}


class UnmappedRecordType(ValueError):
    """Raised when a source record_type has no controlled-vocabulary equivalent."""


def _text(value: Any) -> str:
    """NULL and whitespace-only values become the empty string."""
    return "" if value is None else str(value).strip()


def _integer(value: Any) -> str:
    """Render an integer, or '' when absent. Non-numeric input is preserved
    verbatim rather than silently dropped, so it is visible downstream."""
    if value is None or str(value).strip() == "":
        return ""
    try:
        return str(int(str(value).strip()))
    except ValueError:
        return str(value).strip()


def _decimal(value: Any) -> str:
    """Render a coordinate as a plain decimal, or '' when absent."""
    if value is None or str(value).strip() == "":
        return ""
    try:
        return f"{float(value):g}"
    except ValueError:
        return str(value).strip()


def map_basis_of_record(record_type: Any) -> str:
    """Map a source record type onto the DwC vocabulary.

    >>> map_basis_of_record("camera_trap")
    'MachineObservation'
    """
    key = _text(record_type).lower()
    if not key:
        return ""
    try:
        return BASIS_OF_RECORD[key]
    except KeyError as exc:
        raise UnmappedRecordType(
            f"no basisOfRecord mapping for record_type {record_type!r}"
        ) from exc


def to_occurrence(row: Mapping[str, Any]) -> dict[str, str]:
    """Transform one raw observation into a Darwin Core occurrence."""
    occurrence_id = _text(row["obs_code"])
    if not occurrence_id:
        raise ValueError(f"occurrenceID must not be empty (row id={row.get('id')})")

    name = split_authorship(row["taxon_name"])

    return {
        "occurrenceID": occurrence_id,
        "basisOfRecord": map_basis_of_record(row["record_type"]),
        "scientificName": name.scientific_name,
        "scientificNameAuthorship": name.authorship,
        "vernacularName": _text(row["vernacular"]),
        "individualCount": _integer(row["count"]),
        "eventDate": parse_event_date(row["obs_date"]),
        "decimalLatitude": _decimal(row["lat"]),
        "decimalLongitude": _decimal(row["lon"]),
        "coordinateUncertaintyInMeters": _integer(row["coordinate_accuracy_meters"]),
        "locality": _text(row["locality_name"]),
        "recordedBy": _text(row["observer"]),
        "occurrenceRemarks": _text(row["notes"]),
    }
