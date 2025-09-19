# DataMorph
Transforming data into a new shape. Pre-processing and conversion of Excel to Structured DB.

## Dataset Converter & Preprocessor

A web app to **convert MS-Excel/CSV data into a structured database-ready format** and **pre-process existing structured data** (cleaning, renaming, splitting/joining columns, handling missing data, etc.).

---

## ✨ Features
- Upload **CSV or XLSX** files.
- Two main modes:
  - **Convert to Structured Data** – flatten nested JSON-like fields, ready for DB ingestion.
  - **Pre-process Data** – rich operations:
    - Capitalize/normalize column names
    - Strip whitespace in headers/cells
    - Handle encoding errors
    - Rename columns via map or regex
    - Handle missing values (fill/drop)
    - Remove duplicates
    - Split or join columns
- No persistent storage; files processed in-memory for security.

---

## 🚀 Quick Start (Docker)

```bash
git clone https://github.com/<your-user>/<repo>.git
cd <repo>
docker compose up --build
