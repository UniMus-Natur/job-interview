# Requirements traceability

Every requirement stated in `README.md`, `TASK_ISSUE_TEMPLATE.md` and
`DWC_MAPPING.md`, with where it is satisfied and how it is verified.

---

## 1. ETL transformation

| # | Requirement | Source | Implementation | Verification |
| :-- | :-- | :-- | :-- | :-- |
| 1.1 | Read records from table `raw_observations` in `data/observations.db` | Issue | `pipeline.extract()` — opened `mode=ro` so the source cannot be modified | `TestEndToEnd.test_every_source_row_is_present` compares the output row count against `SELECT COUNT(*)` on the source |
| 1.2 | Transform into the DwC terms in `DWC_MAPPING.md` | Issue | `transform.to_occurrence()`; column order defined once in `DWC_COLUMNS` and the header generated from it | `TestEndToEnd.test_header_matches_specification_exactly` |
| 1.3 | Standardise all dates to ISO 8601 | Issue, mapping §1 | `dates.parse_event_date()` | `TestDateParsing` (7 cases); `TestEndToEnd.test_every_event_date_is_iso_8601` asserts the pattern across all rows |
| 1.4 | Map `record_type` to the `basisOfRecord` controlled vocabulary | Issue, mapping §1 | `transform.BASIS_OF_RECORD`; unmapped input raises `UnmappedRecordType` | `TestBasisOfRecord` covers all five source types and the unmapped case |
| 1.5 | Split `scientificName` from `scientificNameAuthorship` | Issue, mapping §1 | `names.split_authorship()` | `TestAuthorshipSplitting` (6 cases) |
| 1.6 | Export to `output/dwc_occurrences.csv` | Issue | `pipeline.load()`; default path in `__main__.py` | Generated at run time; deliberately excluded by the repository's `.gitignore` (`output/*`), so it is reproduced rather than shipped. `make verify` |

## 2. Reproducibility and execution

| # | Requirement | Source | Implementation |
| :-- | :-- | :-- | :-- |
| 2.1 | Language agnostic | Issue | Python 3.10+, **standard library only** — no third-party dependencies to resolve |
| 2.2 | Dockerfile building and running in a single command | Issue (recommended) | Multi-stage `Dockerfile`. The command given in the issue works verbatim: `docker build -t dwc-etl . && docker run --rm -v $(pwd)/output:/app/output dwc-etl` |
| 2.3 | Dependency definition file as the alternative | Issue | `pyproject.toml` (PEP 621), plus `docker-compose.yml` and a `Makefile` |
| 2.4 | Clear execution instructions in the PR description | Issue | PR body, and `SOLUTION.md` |

## 3. Code quality

| # | Requirement | Source | Implementation |
| :-- | :-- | :-- | :-- |
| 3.1 | Clean, readable, modular | Issue, README | Four modules, one concern each: `dates`, `names`, `transform`, `pipeline` |
| 3.2 | Reasonable error handling | Issue | Typed exceptions — `UnparseableDate`, `UnmappedRecordType`, empty `occurrenceID` — raised rather than swallowed; the CLI returns a non-zero exit code |
| 3.3 | Inline documentation / docstrings | README | Module and function docstrings; the non-obvious decisions are documented where they are made |
| 3.4 | Tests (stated as optional) | Issue | 23 unit and end-to-end tests, `python -m unittest discover -s tests` |
| 3.5 | Typed | Rubric (exceptional) | Type hints throughout; `from __future__ import annotations` |
| 3.6 | Separation of extract, transform and load | Rubric (exceptional) | Three independently callable functions in `pipeline.py` |

## 4. CSV output format

| # | Requirement | Source | Implementation | Verification |
| :-- | :-- | :-- | :-- | :-- |
| 4.1 | Header contains the exact DwC term names | Mapping §2.1 | `DWC_COLUMNS` | `test_header_matches_specification_exactly` |
| 4.2 | UTF-8 encoding | Mapping §2.2 | `open(..., encoding="utf-8")` | Diacritics preserved (`Kráľova hoľa`, `Mária Horváthová`) |
| 4.3 | Comma delimiter | Mapping §2.3 | `csv.DictWriter` default | Output inspection |
| 4.4 | Standard quoting for fields containing commas or quotes | Mapping §2.4 | `csv.QUOTE_MINIMAL` | `High Tatras National Park, Valley area` is quoted in the output |
| 4.5 | NULL as empty string, never `None`/`null`/`NaN` | Mapping §2.5 | `_text`, `_integer`, `_decimal` helpers | `test_no_null_placeholders_leaked_into_output` scans every cell |
| 4.6 | `occurrenceID` must not be empty | Mapping §1 | `to_occurrence()` raises on an empty identifier | `test_empty_occurrence_id_rejected`; `test_occurrence_ids_are_unique_and_populated` |

## 5. Field mapping

All thirteen terms from `DWC_MAPPING.md` §1.

| DwC term | Source column | Handling |
| :-- | :-- | :-- |
| `occurrenceID` | `obs_code` | Verbatim; empty value rejected |
| `basisOfRecord` | `record_type` | Controlled vocabulary; unmapped raises |
| `scientificName` | `taxon_name` | Authorship removed when present |
| `scientificNameAuthorship` | `taxon_name` | Parenthesised or `Surname, YYYY`; empty when absent |
| `vernacularName` | `vernacular` | Verbatim; empty when NULL |
| `individualCount` | `count` | Integer; empty when NULL |
| `eventDate` | `obs_date` | ISO 8601 date or datetime |
| `decimalLatitude` | `lat` | Decimal degrees |
| `decimalLongitude` | `lon` | Decimal degrees |
| `coordinateUncertaintyInMeters` | `coordinate_accuracy_meters` | Integer; empty when NULL |
| `locality` | `locality_name` | Verbatim |
| `recordedBy` | `observer` | Verbatim |
| `occurrenceRemarks` | `notes` | Verbatim |

## 6. Edge cases

Those named in `docs/INTERVIEWER_GUIDE.md`, and two further cases present in the
data but not listed there.

| Case | Input | Output | Test |
| :-- | :-- | :-- | :-- |
| ISO date | `2023-05-12` | `2023-05-12` | `test_iso_date_unchanged` |
| Day-first date | `14/08/2022` | `2022-08-14` | `test_day_first_slash_format` |
| ISO datetime | `2023-09-01 16:45:00` | `2023-09-01T16:45:00` | `test_iso_datetime_becomes_iso_8601_timestamp` |
| Textual month | `June 4, 2021` | `2021-06-04` | `test_textual_month` |
| **Day-first with time** — not listed in the guide | `03/11/2022 08:15:00` | `2022-11-03T08:15:00` | `test_day_first_with_time` |
| NULL accuracy (rows 4, 10) | `NULL` | `""` | `test_nulls_become_empty_strings` |
| Bare authorship | `Canis lupus Linnaeus, 1758` | `Canis lupus` + `Linnaeus, 1758` | `test_bare_authorship` |
| Parenthesised authorship | `Lynx lynx (Linnaeus, 1758)` | `Lynx lynx` + `(Linnaeus, 1758)` | `test_parenthesised_authorship` |
| No authorship | `Ursus arctos` | unchanged, authorship empty | `test_binomial_without_authorship` |
| **Trinomial** — not listed in the guide | `Rupicapra rupicapra tatrica` | unchanged, authorship empty | `test_trinomial_is_not_mistaken_for_authorship` |

The last is the reason authorship is matched by structure rather than by
position: a rule taking everything after the second word would reduce the name
to a binomial and discard the subspecies epithet without error.

## 7. Submission

| # | Requirement | Status |
| :-- | :-- | :-- |
| 7.1 | Fork the repository | `nmbu-ccoulter/job-interview` |
| 7.2 | Feature branch | `feature/dwc-etl` |
| 7.3 | Commit the solution | Six atomic commits |
| 7.4 | Pull request against `main` of the original repository | Opened |
| 7.5 | Reference the issue | `Closes #3` — the issue is #3 in this repository, though the template text refers to #1 |
| 7.6 | PR explains how to run, and the key decisions | Both sections present |

## 8. Stated assumptions

1. **`DD/MM/YYYY` is read day-first.** The notation is genuinely ambiguous:
   `03/11/2022` is 3 November or 11 March depending on convention. `14/08/2022`
   in this dataset can only be day-first, and the localities are European, so
   day-first is applied consistently — recorded here as an assumption rather
   than presented as a detection. Converting *from* an ambiguous notation is
   the direction in which a wrong guess is silent and unrecoverable.

2. **Coordinates are already WGS84.** The mapping specifies WGS84 output; the
   source carries no datum column, so the values are passed through unchanged
   rather than transformed.

3. **`vernacular` is already English.** The mapping states English common
   names; no language detection is applied.
