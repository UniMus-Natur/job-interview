# Species Observation ETL Challenge: SQLite to Darwin Core CSV

Welcome to the data engineering & software development coding assessment!

This exercise evaluates your ability to work with raw biodiversity observation data, clean and transform non-standard records, follow domain specifications (**Darwin Core**), and package your solution reproducibly using modern software practices.

---

## 📋 Task Overview

You are given a sample SQLite database containing raw species observation records (`data/observations.db`). 

Your task is to build a script in **any programming language of your choice** that extracts the raw observation records, cleans and transforms them into standard **Darwin Core (DwC) Occurrences**, and writes the formatted dataset to `output/dwc_occurrences.csv`.

For exact field mappings and data cleaning rules, refer to **[`DWC_MAPPING.md`](./DWC_MAPPING.md)**.

For the full task prompt and issue reference, see **[`TASK_ISSUE_TEMPLATE.md`](./TASK_ISSUE_TEMPLATE.md)** (or Issue #1 on GitHub).

---

## 📁 Repository Structure

```
├── data/
│   └── observations.db         # Sample SQLite database containing raw observations
├── output/
│   └── .gitkeep                # Output folder where dwc_occurrences.csv should be saved
├── scripts/
│   └── generate_db.py          # Python script used to seed data/observations.db
├── docs/
│   └── INTERVIEWER_GUIDE.md    # Internal guide and evaluation rubric for interviewers
├── DWC_MAPPING.md              # Darwin Core transformation mapping specification
├── TASK_ISSUE_TEMPLATE.md      # Template for the GitHub Issue describing the task
└── README.md                   # Candidate instructions (this file)
```

---

## 🛠️ Technical Requirements & Expectations

1. **Language Agnostic**: Choose whichever language you are most comfortable with (e.g. Python, R, Node.js/TypeScript, Go, Rust, Julia, etc.).
2. **Environment & Reproducibility**:
   - **Recommended**: Include a `Dockerfile` (and/or `docker-compose.yml`) so your transformation script can be built and executed in an isolated container.
   - **Alternative**: If not using Docker, provide clear dependency management files (e.g. `pyproject.toml`, `requirements.txt`, `package.json`, `Cargo.toml`, `Pipfile`, etc.) and step-by-step setup commands.
3. **Data Quality & Transformation**:
   - Parse and standardize varied date formats into ISO 8601 (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`).
   - Map record types to official Darwin Core `basisOfRecord` controlled vocabulary.
   - Separate scientific names from authorship where applicable.
   - Ensure clean null handling (empty strings in CSV output).
4. **Code Quality**:
   - Write structured, readable, and maintainable code.
   - Include brief inline documentation or docstrings where helpful.

---

## 🚀 How to Submit Your Solution

1. **Fork** this repository to your personal GitHub account.
2. Create a working branch in your fork (e.g. `git checkout -b feature/dwc-etl`).
3. Implement your solution and commit your work.
4. Ensure your script generates `output/dwc_occurrences.csv` cleanly.
5. Create a **Pull Request (PR)** from your fork back to the `main` branch of this repository.
6. In your PR title and description:
   - Reference the task issue (e.g. `Closes #1` or `Fixes #1`).
   - Include instructions on how to run your code / Docker container.
   - Summarize your approach and any notable implementation choices.

---

## 📊 Evaluation Criteria

We evaluate submissions based on:
- **Correctness & Accuracy**: Does the output CSV strictly match the required DwC mapping, ISO date standards, and header names?
- **Reproducibility**: Is the execution environment clearly defined (Docker/venv) and easy to run?
- **Code Organization & Craft**: Is the code clean, modular, properly typed/formatted, and easy to maintain?
- **Documentation**: Are setup and execution steps clearly documented in your PR description?

---

## ℹ️ Setup Instructions for Interviewers

If you are setting up this repository for a new interview round:
1. Push this codebase to a public (or shared template) GitHub repository.
2. Create **Issue #1** using the text from `TASK_ISSUE_TEMPLATE.md`.
3. Provide the repository link and Issue #1 link to the candidate.