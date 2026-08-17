# Darwin Core (DwC) Mapping Specification

This document provides the specification for transforming raw species observation records from `data/observations.db` (table `raw_observations`) into a Darwin Core (DwC) compliant CSV dataset saved at `output/dwc_occurrences.csv`.

---

## 1. Target CSV Schema & Mapping Rules

Your solution should generate a CSV file named `output/dwc_occurrences.csv` containing the following Darwin Core standard columns:

| Target DwC Term | Source Column | Transformation / Formatting Rules |
| :--- | :--- | :--- |
| `occurrenceID` | `obs_code` | Unique identifier for the occurrence record (e.g., `OBS-2023-001`). Must not be empty. |
| `basisOfRecord` | `record_type` | Map source types to standard DwC terms:<br>- `human_observation`, `visual`, `field_notes` &rarr; `HumanObservation`<br>- `camera_trap` &rarr; `MachineObservation`<br>- `museum_specimen` &rarr; `PreservedSpecimen` |
| `scientificName` | `taxon_name` | The full scientific name, stripped of authorship if authorship is parsed separately (or full taxon name if unparsed). |
| `scientificNameAuthorship` | `taxon_name` | Extracted authorship string (e.g. `Linnaeus, 1758` or `(Linnaeus, 1758)`), or empty if no author is present in `taxon_name`. |
| `vernacularName` | `vernacular` | Common name of the species in English (e.g., `Gray Wolf`). |
| `individualCount` | `count` | Integer count of individuals observed. Leave blank/empty string if `NULL`. |
| `eventDate` | `obs_date` | Must be standardized to ISO 8601 format (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`). Parse varied formats such as `DD/MM/YYYY`, `Month DD, YYYY`, and timestamp strings. |
| `decimalLatitude` | `lat` | Decimal degree latitude formatted as float (WGS84). |
| `decimalLongitude` | `lon` | Decimal degree longitude formatted as float (WGS84). |
| `coordinateUncertaintyInMeters` | `coordinate_accuracy_meters` | Integer distance in meters representing spatial uncertainty. Leave blank if `NULL`. |
| `locality` | `locality_name` | Text description of the location. |
| `recordedBy` | `observer` | Name of the person or entity responsible for recording the observation. |
| `occurrenceRemarks` | `notes` | Additional notes or comments regarding the observation. |

---

## 2. CSV Output Format Requirements

1. **Header**: The first row of the CSV file must contain the exact DwC term names listed above.
2. **Encoding**: UTF-8 encoding.
3. **Delimiter**: Standard comma (`,`).
4. **Quoting**: Standard CSV quoting rules (quote text fields containing commas or quotes).
5. **Null handling**: `NULL` values should be represented as empty strings (`""`), not `"None"`, `"null"`, or `"NaN"`.

---

## 3. Reference Links

- [Darwin Core Quick Reference Guide](https://dwc.tdwg.org/terms/)
- [DwC Basis of Record Vocabulary](https://rs.gbif.org/vocabulary/gbif/basis_of_record.xml)
