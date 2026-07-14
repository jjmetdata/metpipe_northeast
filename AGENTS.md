# MetPipe Northeast — Codex Project Guidance

## Project purpose

MetPipe Northeast is a portfolio data-engineering project that cleans, stores,
validates, and analyzes historical NOAA observations from northeastern US
weather stations.

## Current status

Phase 2 is a local PostgreSQL pipeline for BOS, ALB, JFK, and PVD. The workflow
is data cleaning, schema creation, ingestion, and manual SQL validation.

## Important paths

- `README.md` — setup and usage documentation
- `src/main.py` — database setup and ingestion orchestration
- `src/weather_data_cleanup.py` — raw CSV cleaning
- `src/ingest.py` — cleaned CSV ingestion
- `sql/schema.sql` — schema, constraints, station metadata, and views
- `sql/checks.sql` — database validation queries
- `sql/legacy/ingest.sql` — older manual ingestion implementation
- `data/raw/` — local source data; ignored by Git
- `data/processed/` — local cleaned data; ignored by Git

## Database

The default database name is `northeast_weather_2024_phase2`. Connection
settings are controlled by the `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and
`DB_PASSWORD` environment variables.

## Commands

```bash
python3 src/weather_data_cleanup.py
python3 src/main.py
psql -d northeast_weather_2024_phase2 -f sql/checks.sql
```
