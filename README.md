# Corporate Intelligence - Company Health Status

Python ETL/analytics pipeline that pulls tech company financials from Yahoo Finance (via `yfinance`), lands them in PostgreSQL following a Medallion pattern (bronze → silver → gold), and exports Excel files for BI/Power BI.

## Project Structure

- `src/data_pipeline/` – pipeline code (extract, transform, gold KPIs, health analysis, Excel export, config)
- `data/raw/` – raw scraped CSVs (ignored in git)
- `data/processed/DataTesting/` – sample transformed CSVs kept for reference
- `data/bronze|silver|gold/` – generated medallion layers (ignored in git)
- `data/output/EMPRESAS/` – per-company Excel exports (ignored in git)
- `docs/diagrams/` – ER and conceptual diagrams
- `docs/reports/` – LaTeX and simple reports
- `PowerBI/` – Power BI project files
- `requirements.txt` – Python dependencies

## Quickstart

1. Create/activate a virtualenv and install deps:
   ```powershell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
   ```
2. Ensure PostgreSQL is running and update credentials in `src/data_pipeline/config.py` if needed.
3. Run the full pipeline:
   ```powershell
   python src/data_pipeline/run_pipeline.py
   ```
4. Excel outputs will land in `data/gold/excel_export/` and per-company folders in `data/output/EMPRESAS/`.

## Notes

- Gold/bronze/silver/raw/output folders are ignored by git to keep the repo clean; rerun the pipeline to regenerate outputs.
- The sample `data/processed/DataTesting` CSVs remain tracked for reference/testing.
