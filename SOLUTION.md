# Solution notes

## Run it

```bash
docker build -t dwc-etl .
docker run --rm -v "$(pwd)/output:/app/output" dwc-etl
```

Or without Docker (no third-party dependencies):

```bash
PYTHONPATH=src python3 -m dwc_etl --verbose
python3 -m unittest discover -s tests -v
```

`make run`, `make test`, `make docker-run` and `make verify` wrap the same commands.

## Structure

```
src/dwc_etl/
  dates.py       date parsing, one concern
  names.py       scientific name / authorship separation
  transform.py   row -> Darwin Core terms, and the controlled vocabulary
  pipeline.py    extract / transform / load, kept separate
  __main__.py    CLI
tests/           23 unit and end-to-end tests
```

## Decisions worth stating

**Dates are parsed against an explicit list of formats, not guessed.** An
unrecognised value raises rather than being silently coerced. `DD/MM/YYYY` is
genuinely ambiguous — `03/11/2022` is 3 November or 11 March depending on
convention — so day-first is applied consistently and documented as an
assumption, not presented as a detection. `14/08/2022` in this dataset can only
be day-first, which supports the choice but does not prove it for future data.

**Authorship is identified by structure, not position.** A rule that treats
everything after the second word as authorship would turn
`Rupicapra rupicapra tatrica` into `Rupicapra rupicapra` + `tatrica`, silently
discarding a subspecies epithet. Authorship is recognised only when
parenthesised, or when a capitalised surname is followed by a four-digit year.
There is a test for the trinomial case specifically.

**An unmapped `record_type` raises.** Guessing a `basisOfRecord` for an
unrecognised source type would put an invented value into a controlled
vocabulary field, where it is indistinguishable from a real one.

**Absent values become empty strings**, never `None`, `null` or `NaN`. A test
asserts no such placeholder appears anywhere in the output.

**The source database is opened read-only** (`mode=ro`). The input is never
modified.

## Verification

```bash
make verify
```

Confirms the header matches the specification exactly, and prints every parsed
date and every name/authorship split for inspection.
