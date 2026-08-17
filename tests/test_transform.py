"""Unit tests for Darwin Core transformation and ETL pipeline."""

import csv
from pathlib import Path
import tempfile
import unittest

from src.extract import extract_raw_observations
from src.load import DWC_HEADERS, load_to_csv
from src.pipeline import run_pipeline
from src.transform import (
    map_basis_of_record,
    parse_date_to_iso,
    parse_taxon_name,
    transform_record,
)


class TestTransform(unittest.TestCase):
    """Unit tests for data transformations."""

    def test_parse_date_to_iso(self):
        # ISO date
        self.assertEqual(parse_date_to_iso("2023-05-12"), "2023-05-12")
        # DD/MM/YYYY
        self.assertEqual(parse_date_to_iso("14/08/2022"), "2022-08-14")
        # ISO timestamp
        self.assertEqual(parse_date_to_iso("2023-09-01 16:45:00"), "2023-09-01T16:45:00")
        # Textual month
        self.assertEqual(parse_date_to_iso("June 4, 2021"), "2021-06-04")
        self.assertEqual(parse_date_to_iso("May 12, 2023"), "2023-05-12")
        # DD/MM/YYYY with time
        self.assertEqual(parse_date_to_iso("03/11/2022 08:15:00"), "2022-11-03T08:15:00")
        # None and empty
        self.assertEqual(parse_date_to_iso(None), "")
        self.assertEqual(parse_date_to_iso(""), "")

    def test_parse_taxon_name(self):
        # Binomial with author and year
        name, auth = parse_taxon_name("Canis lupus Linnaeus, 1758")
        self.assertEqual(name, "Canis lupus")
        self.assertEqual(auth, "Linnaeus, 1758")

        # Binomial with parenthesized author and year
        name, auth = parse_taxon_name("Lynx lynx (Linnaeus, 1758)")
        self.assertEqual(name, "Lynx lynx")
        self.assertEqual(auth, "(Linnaeus, 1758)")

        # Binomial without author
        name, auth = parse_taxon_name("Ursus arctos")
        self.assertEqual(name, "Ursus arctos")
        self.assertEqual(auth, "")

        # Trinomial (subspecies) without author
        name, auth = parse_taxon_name("Rupicapra rupicapra tatrica")
        self.assertEqual(name, "Rupicapra rupicapra tatrica")
        self.assertEqual(auth, "")

        # None / empty
        name, auth = parse_taxon_name(None)
        self.assertEqual(name, "")
        self.assertEqual(auth, "")

    def test_map_basis_of_record(self):
        self.assertEqual(map_basis_of_record("human_observation"), "HumanObservation")
        self.assertEqual(map_basis_of_record("visual"), "HumanObservation")
        self.assertEqual(map_basis_of_record("field_notes"), "HumanObservation")
        self.assertEqual(map_basis_of_record("camera_trap"), "MachineObservation")
        self.assertEqual(map_basis_of_record("museum_specimen"), "PreservedSpecimen")
        self.assertEqual(map_basis_of_record(None), "HumanObservation")

    def test_transform_record_null_handling(self):
        raw = {
            "obs_code": "OBS-TEST-001",
            "taxon_name": "Ursus arctos",
            "vernacular": None,
            "obs_date": "2023-05-12",
            "lat": 49.1234,
            "lon": 20.5678,
            "coordinate_accuracy_meters": None,
            "locality_name": "Test Locality",
            "record_type": "visual",
            "count": None,
            "observer": None,
            "notes": None,
        }
        res = transform_record(raw)
        self.assertEqual(res["occurrenceID"], "OBS-TEST-001")
        self.assertEqual(res["vernacularName"], "")
        self.assertEqual(res["individualCount"], "")
        self.assertEqual(res["coordinateUncertaintyInMeters"], "")
        self.assertEqual(res["recordedBy"], "")
        self.assertEqual(res["occurrenceRemarks"], "")
        self.assertEqual(res["scientificNameAuthorship"], "")


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests executing the full pipeline against data/observations.db."""

    def test_full_pipeline_run(self):
        db_path = Path("data/observations.db")
        self.assertTrue(db_path.exists(), "Source database data/observations.db should exist")

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "dwc_occurrences.csv"
            res = run_pipeline(db_path=db_path, output_path=out_file)

            self.assertEqual(res["status"], "success")
            self.assertEqual(res["records_extracted"], 12)
            self.assertEqual(res["records_transformed"], 12)
            self.assertTrue(out_file.exists())

            with open(out_file, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.assertEqual(reader.fieldnames, DWC_HEADERS)
                rows = list(reader)
                self.assertEqual(len(rows), 12)

                # Check row 1
                row1 = rows[0]
                self.assertEqual(row1["occurrenceID"], "OBS-2023-001")
                self.assertEqual(row1["scientificName"], "Canis lupus")
                self.assertEqual(row1["scientificNameAuthorship"], "Linnaeus, 1758")
                self.assertEqual(row1["basisOfRecord"], "HumanObservation")
                self.assertEqual(row1["eventDate"], "2023-05-12")

                # Check row 2 (date DD/MM/YYYY, MachineObservation)
                row2 = rows[1]
                self.assertEqual(row2["occurrenceID"], "OBS-2023-002")
                self.assertEqual(row2["basisOfRecord"], "MachineObservation")
                self.assertEqual(row2["eventDate"], "2022-08-14")


if __name__ == "__main__":
    unittest.main()
