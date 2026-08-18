# Verification

What was checked before submission, how, and the result. Every command below is
reproducible from a clean checkout.

---

## 1. Correctness and accuracy

### Header matches the specification exactly

```bash
head -n 1 output/dwc_occurrences.csv
```

```
occurrenceID,basisOfRecord,scientificName,scientificNameAuthorship,vernacularName,individualCount,eventDate,decimalLatitude,decimalLongitude,coordinateUncertaintyInMeters,locality,recordedBy,occurrenceRemarks
```

Asserted, not eyeballed: `DWC_COLUMNS` is defined once and the header is written
from it, so the two cannot drift, and
`TestEndToEnd.test_header_matches_specification_exactly` compares the written
header against that definition.

### Row count preserved

12 source rows in, 12 occurrences out.
`TestEndToEnd.test_every_source_row_is_present` compares the written row count
against `SELECT COUNT(*)` on the source rather than against a hard-coded 12, so
the assertion still holds if the source changes.

### Every date is ISO 8601

`TestEndToEnd.test_every_event_date_is_iso_8601` asserts
`^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$` across all rows. Per-format cases:

| Input | Output |
| :-- | :-- |
| `2023-05-12` | `2023-05-12` |
| `14/08/2022` | `2022-08-14` |
| `2023-09-01 16:45:00` | `2023-09-01T16:45:00` |
| `03/11/2022 08:15:00` | `2022-11-03T08:15:00` |
| `June 4, 2021` | `2021-06-04` |
| `May 12, 2023` | `2023-05-12` |

### basisOfRecord within the controlled vocabulary

`TestEndToEnd.test_basis_of_record_within_controlled_vocabulary` asserts the set
of emitted values is a subset of the three permitted terms. All five source
types are covered individually in `TestBasisOfRecord`; an unrecognised type
raises rather than defaulting.

### Authorship separation

| Input | scientificName | scientificNameAuthorship |
| :-- | :-- | :-- |
| `Canis lupus Linnaeus, 1758` | `Canis lupus` | `Linnaeus, 1758` |
| `Lynx lynx (Linnaeus, 1758)` | `Lynx lynx` | `(Linnaeus, 1758)` |
| `Ursus arctos` | `Ursus arctos` | *(empty)* |
| `Rupicapra rupicapra tatrica` | `Rupicapra rupicapra tatrica` | *(empty)* |

### Null handling

`TestEndToEnd.test_no_null_placeholders_leaked_into_output` scans **every cell**
of the output for `None`, `null`, `NULL`, `NaN` and `nan`. The two NULL
`coordinate_accuracy_meters` values (rows 4 and 10) emit as empty strings.

### Identifiers

`test_occurrence_ids_are_unique_and_populated` asserts every `occurrenceID` is
non-empty and that no value repeats.

```bash
python3 -m unittest discover -s tests -v     # 23 tests
```

---

## 2. Reproducibility

Three execution paths were run, and all three produce a **byte-identical** CSV.

### Docker — the command from the task issue, verbatim

```bash
docker build -t dwc-etl .
docker run --rm -v "$(pwd)/output:/app/output" dwc-etl
```

Runs as an unprivileged user; the output directory is a mount point, so the CSV
is written to the host.

### Docker Compose

```bash
docker compose run --rm etl
```

The service names its image so an existing build is reused rather than
rebuilt on every invocation.

### Clean checkout and virtual environment

Verified from a fresh clone in a temporary directory, to confirm no dependence
on the development working directory and no hard-coded paths:

```bash
git clone --branch feature/dwc-etl <fork-url> /tmp/fresh && cd /tmp/fresh
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
dwc-etl --verbose
python3 -m unittest discover -s tests
```

23 tests pass from the fresh clone, and the CSV it produces is byte-identical to
the one produced by both Docker paths.

The output file is **not committed** — the repository's `.gitignore` excludes
`output/*` by design, so the dataset is reproduced by running the pipeline
rather than shipped in the branch.

There are **no third-party dependencies** — the standard library only — so there
is nothing to resolve at install time and no version to conflict.

---

## 3. Code organisation

| | |
| :-- | :-- |
| Modules | `dates`, `names`, `transform`, `pipeline`, `__main__` — one concern each |
| ETL phases | `extract()`, `transform()`, `load()` are independently callable and independently tested |
| Typing | Type hints throughout; `from __future__ import annotations` |
| Errors | `UnparseableDate`, `UnmappedRecordType`, and an explicit rejection of an empty `occurrenceID`; raised, never swallowed; the CLI exits non-zero |
| Input safety | The source database is opened `mode=ro` and cannot be modified |
| Configuration | Paths are CLI arguments with defaults, not constants |

---

## 4. Documentation

| Document | Contents |
| :-- | :-- |
| Pull request description | How to run, approach, decisions, a verification table |
| `SOLUTION.md` | Structure, and the reasoning behind each judgement call |
| `REQUIREMENTS.md` | Every stated requirement traced to its implementation and its test |
| `VERIFICATION.md` | This document |
| Docstrings | Module and function level; the non-obvious decisions are documented where they are made |

---

## 5. What is asserted rather than assumed

The distinction matters more than the count of tests.

- The header is compared against the specification, not inspected by eye.
- The row count is compared against the source, not against a literal `12`.
- Null placeholders are searched for across every cell, not spot-checked.
- Date formats are enumerated explicitly; an unknown format raises rather than
  producing a plausible wrong date.
- An unmapped `record_type` raises rather than defaulting, because an invented
  controlled-vocabulary value is indistinguishable from a real one afterwards.

The assumptions that remain — day-first reading of `DD/MM/YYYY`, WGS84
coordinates, English vernacular names — are stated in `REQUIREMENTS.md` §8 so
they can be disagreed with explicitly rather than discovered later.
