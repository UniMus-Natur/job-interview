# [Task] Species Observations ETL: Transform SQLite to Darwin Core CSV

> **Note to Interviewer**: Create a GitHub Issue in your repository with the content below so the candidate can reference `#1` in their Pull Request.

---

## 📌 Context & Goal

We have raw species observation logs stored in a SQLite database (`data/observations.db`). To publish these observations to biodiversity networks (like GBIF or OBIS), they must be standardized into the **Darwin Core (DwC)** format as a clean CSV file.

Your task is to write an automated ETL script (in the programming language of your choice) that reads the SQLite database, transforms and cleans the data according to the Darwin Core specification, and outputs the result to `output/dwc_occurrences.csv`.

---

## 🛠️ Requirements & Deliverables

1. **ETL Transformation**:
   - Read records from table `raw_observations` in `data/observations.db`.
   - Transform data into Darwin Core standard terms specified in [`DWC_MAPPING.md`](./DWC_MAPPING.md).
   - Standardize all dates to ISO 8601 format (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`).
   - Map `record_type` to standard `basisOfRecord` controlled vocabulary.
   - Clean taxonomy (split `scientificName` and `scientificNameAuthorship` where appropriate).
   - Export result to `output/dwc_occurrences.csv`.

2. **Reproducibility & Execution**:
   - **Language Agnostic**: You may use Python, R, Node.js, Go, Julia, Rust, or any language you prefer.
   - **Environment / Containerization**:
     - **Recommended**: A `Dockerfile` or `docker-compose.yml` that builds and runs your script seamlessly with a single command (e.g. `docker build -t dwc-etl . && docker run --rm -v $(pwd)/output:/app/output dwc-etl`).
     - **Alternative**: Virtual environment / package manager definition file (e.g., `pyproject.toml`, `requirements.txt`, `package.json`, `Cargo.toml`, etc.) along with clear execution instructions in your PR description or repository README.

3. **Code Quality**:
   - Write clean, readable, modular code with reasonable error handling.
   - (Optional bonus) Include basic tests or validation checks.

---

## 🚀 How to Submit Your Solution

1. **Fork** this repository to your personal GitHub account.
2. Create a feature branch (e.g., `feat/dwc-transformation`).
3. Develop and commit your solution.
4. Open a **Pull Request** against the `main` branch of the original repository.
5. In your PR title and description, reference this issue (e.g., `Fixes #1` or `Closes #1`).
6. In your PR description, explain:
   - How to run your script / container.
   - Key decisions or trade-offs made during mapping/transformation.
