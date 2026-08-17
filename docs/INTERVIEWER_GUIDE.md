# Interviewer Evaluation Guide

This guide is intended for hiring managers and technical interviewers reviewing candidate submissions for the **Species Observation ETL (SQLite to Darwin Core CSV)** challenge.

---

## 🎯 Candidate Assignment Summary

The candidate was asked to:
1. Fork the repo and write a script in any language to extract data from `data/observations.db`.
2. Clean and map the 12 raw observation records into standard Darwin Core terms in `output/dwc_occurrences.csv`.
3. Provide a reproducible environment (Docker container or virtualenv definition).
4. Open a Pull Request referencing Issue #1.

---

## 📋 Evaluation Rubric

| Criteria | 🔴 Developing / Below Expectation | 🟡 Satisfactory (Pass) | 🟢 Exceptional |
| :--- | :--- | :--- | :--- |
| **Reproducibility** | Missing environment setup; script fails due to unhandled external dependencies or hardcoded paths. | Clean virtualenv or standard `Dockerfile` provided with clear run instructions in PR. | Multi-stage Docker build, clean volume mounting, Makefile or CLI runner included. |
| **Data Mapping & Transformation** | Dates unformatted or incorrect ISO parsing; missing DwC terms or improper headers; `NULL` exported as `"None"`/`"NaN"`. | All 12 rows correctly parsed into ISO 8601; `basisOfRecord` correctly mapped; correct CSV headers & empty string for NULLs. | Robust date parser handling arbitrary date formats; regex/AST parsing for scientific name authorship splitting. |
| **Code Structure & Quality** | Monolithic script without modularity; global variables; no error handling. | Modular functions/classes; clean naming conventions; basic error handling for DB/file operations. | Type hints / interfaces; clear separation of extraction, transformation, and load (ETL) phases; automated unit tests. |
| **Git & PR Hygiene** | Single huge commit; no issue reference; empty PR description. | Clear PR title referencing `#1`; detailed description with setup steps and brief explanation of approach. | Atomic commits; well-structured PR comments; helpful verification commands provided in PR. |

---

## 🧪 How to Verify a Candidate's Submission

1. **Checkout the candidate's branch**:
   ```bash
   git fetch origin pull/<PR_NUMBER>/head:candidate-submission
   git checkout candidate-submission
   ```

2. **Run their Docker container or script**:
   - If using Docker:
     ```bash
     docker build -t dwc-test .
     docker run --rm -v $(pwd)/output:/app/output dwc-test
     ```
   - If using Python/venv:
     ```bash
     python3 -m venv .venv && source .venv/bin/activate
     pip install -r requirements.txt  # or poetry install / uv sync
     python main.py                   # or candidate's entrypoint
     ```

3. **Check the Output CSV**:
   - Verify `output/dwc_occurrences.csv` exists.
   - Inspect headers and first few rows:
     ```bash
     head -n 5 output/dwc_occurrences.csv
     ```
   - Verify key transformations:
     - `eventDate`: Check that `14/08/2022` became `2022-08-14` and `June 4, 2021` became `2021-06-04`.
     - `basisOfRecord`: Check that `camera_trap` became `MachineObservation` and `human_observation` became `HumanObservation`.
     - `scientificNameAuthorship`: Check that authorship (e.g., `Linnaeus, 1758`) was isolated if attempted.

---

## 💡 Key Edge Cases in `data/observations.db`

- **Date formats**: `2023-05-12` (ISO), `14/08/2022` (DD/MM/YYYY), `2023-09-01 16:45:00` (ISO datetime), `June 4, 2021` (textual month).
- **Missing values**: `coordinate_accuracy_meters` and `count` are `NULL` on rows 4 & 10. Output must produce empty fields `""`.
- **Scientific name authorship**: `Canis lupus Linnaeus, 1758` vs `Lynx lynx (Linnaeus, 1758)` vs `Ursus arctos` (no author).
