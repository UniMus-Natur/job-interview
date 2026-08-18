"""Unit tests for the transformation rules.

Run with:  python -m unittest discover -s tests
"""
from __future__ import annotations

import csv
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dwc_etl.dates import UnparseableDate, parse_event_date
from dwc_etl.names import split_authorship
from dwc_etl.pipeline import run
from dwc_etl.transform import (DWC_COLUMNS, UnmappedRecordType,
                               map_basis_of_record, to_occurrence)


class TestDateParsing(unittest.TestCase):
    def test_iso_date_unchanged(self):
        self.assertEqual(parse_event_date("2023-05-12"), "2023-05-12")

    def test_day_first_slash_format(self):
        self.assertEqual(parse_event_date("14/08/2022"), "2022-08-14")

    def test_iso_datetime_becomes_iso_8601_timestamp(self):
        self.assertEqual(parse_event_date("2023-09-01 16:45:00"),
                         "2023-09-01T16:45:00")

    def test_day_first_with_time(self):
        self.assertEqual(parse_event_date("03/11/2022 08:15:00"),
                         "2022-11-03T08:15:00")

    def test_textual_month(self):
        self.assertEqual(parse_event_date("June 4, 2021"), "2021-06-04")
        self.assertEqual(parse_event_date("May 12, 2023"), "2023-05-12")

    def test_absent_values_become_empty(self):
        self.assertEqual(parse_event_date(None), "")
        self.assertEqual(parse_event_date("   "), "")

    def test_unrecognised_format_raises(self):
        with self.assertRaises(UnparseableDate):
            parse_event_date("summer 1963")


class TestAuthorshipSplitting(unittest.TestCase):
    def test_bare_authorship(self):
        self.assertEqual(split_authorship("Canis lupus Linnaeus, 1758"),
                         ("Canis lupus", "Linnaeus, 1758"))

    def test_parenthesised_authorship(self):
        self.assertEqual(split_authorship("Lynx lynx (Linnaeus, 1758)"),
                         ("Lynx lynx", "(Linnaeus, 1758)"))

    def test_binomial_without_authorship(self):
        self.assertEqual(split_authorship("Ursus arctos"), ("Ursus arctos", ""))

    def test_trinomial_is_not_mistaken_for_authorship(self):
        """A subspecies epithet must survive: position is not evidence."""
        self.assertEqual(split_authorship("Rupicapra rupicapra tatrica"),
                         ("Rupicapra rupicapra tatrica", ""))

    def test_multiple_authors(self):
        self.assertEqual(split_authorship("Genus species Müller & Schmidt, 1801"),
                         ("Genus species", "Müller & Schmidt, 1801"))

    def test_absent_value(self):
        self.assertEqual(split_authorship(None), ("", ""))


class TestBasisOfRecord(unittest.TestCase):
    def test_all_source_types_map(self):
        for source, expected in (
            ("human_observation", "HumanObservation"),
            ("visual", "HumanObservation"),
            ("field_notes", "HumanObservation"),
            ("camera_trap", "MachineObservation"),
            ("museum_specimen", "PreservedSpecimen"),
        ):
            with self.subTest(source=source):
                self.assertEqual(map_basis_of_record(source), expected)

    def test_unknown_type_raises_rather_than_guessing(self):
        with self.assertRaises(UnmappedRecordType):
            map_basis_of_record("carrier_pigeon")


class TestNullHandling(unittest.TestCase):
    def test_nulls_become_empty_strings(self):
        row = {
            "id": 1, "obs_code": "OBS-1", "taxon_name": "Ursus arctos",
            "vernacular": None, "obs_date": "2023-01-01", "lat": None, "lon": None,
            "coordinate_accuracy_meters": None, "locality_name": None,
            "record_type": "visual", "count": None, "observer": None, "notes": None,
        }
        occurrence = to_occurrence(row)
        for term in ("vernacularName", "individualCount", "decimalLatitude",
                     "coordinateUncertaintyInMeters", "locality", "recordedBy",
                     "occurrenceRemarks"):
            with self.subTest(term=term):
                self.assertEqual(occurrence[term], "")

    def test_empty_occurrence_id_rejected(self):
        row = {"id": 1, "obs_code": "  ", "taxon_name": "X", "vernacular": None,
               "obs_date": "2023-01-01", "lat": None, "lon": None,
               "coordinate_accuracy_meters": None, "locality_name": None,
               "record_type": "visual", "count": None, "observer": None, "notes": None}
        with self.assertRaises(ValueError):
            to_occurrence(row)


class TestEndToEnd(unittest.TestCase):
    """The full pipeline against the supplied database."""

    @classmethod
    def setUpClass(cls):
        cls.database = Path(__file__).resolve().parents[1] / "data" / "observations.db"
        cls.tmp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.tmp.name) / "dwc_occurrences.csv"
        cls.written = run(cls.database, cls.output)
        with cls.output.open(encoding="utf-8", newline="") as handle:
            cls.rows = list(csv.DictReader(handle))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_source_row_is_present(self):
        with sqlite3.connect(f"file:{self.database}?mode=ro", uri=True) as con:
            source_rows = con.execute("SELECT COUNT(*) FROM raw_observations").fetchone()[0]
        self.assertEqual(self.written, source_rows)
        self.assertEqual(len(self.rows), source_rows)

    def test_header_matches_specification_exactly(self):
        with self.output.open(encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle))
        self.assertEqual(header, list(DWC_COLUMNS))

    def test_occurrence_ids_are_unique_and_populated(self):
        ids = [row["occurrenceID"] for row in self.rows]
        self.assertTrue(all(ids))
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_event_date_is_iso_8601(self):
        import re
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$")
        for row in self.rows:
            with self.subTest(occurrence=row["occurrenceID"]):
                self.assertRegex(row["eventDate"], pattern)

    def test_basis_of_record_within_controlled_vocabulary(self):
        allowed = {"HumanObservation", "MachineObservation", "PreservedSpecimen"}
        self.assertTrue({row["basisOfRecord"] for row in self.rows} <= allowed)

    def test_no_null_placeholders_leaked_into_output(self):
        forbidden = {"None", "null", "NULL", "NaN", "nan"}
        for row in self.rows:
            for term, value in row.items():
                with self.subTest(occurrence=row["occurrenceID"], term=term):
                    self.assertNotIn(value, forbidden)


if __name__ == "__main__":
    unittest.main(verbosity=2)
