# MetPipe Northeast — Codex Project Guidance

## Project purpose

MetPipe Northeast is a portfolio data-engineering pipeline that cleans, stores,
validates, and analyzes multi-year NOAA observations from northeastern US
weather stations.

## Current behavior

- Raw files follow `data/raw/<year>/<station>_hourly_<year>.csv`.
- Cleaned files go to `data/processed/<year>/`; legacy flat files are accepted.
- A station-year is unique and its CSV must contain only that calendar year.
- Every matching station-year file is cleaned and ingested independently.
- PostgreSQL ingestion is incremental and idempotent by `(datetime, station)`.
- Daily, monthly, and annual summaries retain the observation year.
- Current local data covers twenty stations for 2020–2024, including PVC
  (Provincetown) and ORH (Worcester).
- `src/audit_station_minutes.py` checks the FM-15 minute and exact hourly
  coverage by station-year; the twenty verified minutes are seeded in schema.sql.
- The hourly view includes only FM-15 rows at the station's checked minute.

## Important paths

- `README.md` — setup, migration, and usage documentation
- `src/file_utils.py` — strict station-year filename parsing and discovery
- `src/main.py` — database setup and ingestion orchestration
- `src/weather_data_cleanup.py` — raw CSV cleaning
- `src/ingest.py` — incremental cleaned CSV ingestion
- `sql/schema.sql` — generic multi-year schema and views
- `sql/checks.sql` — multi-year database validation queries
- `sql/legacy/ingest.sql` — archived 2024-only manual ingestion
- `data/raw/` and `data/processed/` — local data ignored by Git

## Database

The default database is `metpipe_northeast`. Connection settings use
`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`.

The schema is non-destructive. Do not reintroduce unconditional DROP statements
into the normal pipeline. Use explicit migrations for future schema changes.

## Commands

```bash
python3 src/weather_data_cleanup.py
python3 src/main.py
psql -d metpipe_northeast -f sql/checks.sql
python3 -m unittest discover -s tests -v
```
