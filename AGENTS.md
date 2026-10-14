# MetPipe Northeast — Codex Project Guidance

## Project purpose

MetPipe Northeast builds a traceable regional weather-observation foundation
for historical analysis and future observation-supported nowcasting. It cleans,
stores, validates and analyzes multi-year NOAA observations from northeastern
US stations. Future live sensors, station lead/lag analysis, pressure diagnostics
and model integration are planned, not implemented forecasting capabilities.
Keep published project descriptions regional and product-neutral. Do not
single out a station as a case study or disclose planned downstream uses.
Station-specific data limitations should still be documented factually.
See docs/project_purpose.md.

## Current behavior

- Raw files follow `data/raw/<year>/<station>_hourly_<year>.csv`.
- Cleaned files go to `data/processed/<year>/`; legacy flat files are accepted.
- A station-year is unique and its CSV must contain only that calendar year.
- Every matching station-year file is cleaned and ingested independently.
- PostgreSQL ingestion is incremental and idempotent by `(datetime, station)`.
- Daily, monthly, and annual summaries retain the observation year.
- The original twenty stations are retained, including PVC (Provincetown) and
  ORH (Worcester). The 2005–2019 GHCNh backfill complements preserved 2020–2024
  LCDv1 data; see docs/ingestion_2005_2024.md for validated completion state.
- `src/audit_station_minutes.py` checks the FM-15 minute and exact hourly
  coverage by station-year; the twenty verified minutes are seeded in schema.sql.
- The hourly view retains checked-minute FM-15 selection for LCDv1. GHCNh uses
  source-aware routine-report ranking, not a modern fixed minute. Specials do
  not fill missing routine hours.
- GHCNh raw Parquet files live under data/raw/ghcnh/<UTC year>/. The historical
  adapter converts UTC/SI to fixed UTC-5/customary units, retaining UTC and
  per-element raw flags. Do not mix raw SI and customary values. Missing
  precipitation is unknown; traces are separately flagged. Coded clouds are
  retained, not fully decoded. Protect existing LCDv1 rows during backfill.

## Station selection and historical expansion

- The agreed working expansion target is 2005–2024 (decision October 12, 2026).
  Older 1995–2024 and 1990–2024 windows remain historical context, not current
  station eligibility requirements. See docs/data_scope.md. Screen candidates
  back to 1990 for future readiness without assuming complete hourly coverage.
  Include non-airport observatories and cooperative stations in the search,
  distinguishing daily climate anchors from subdaily/real-time stations.
  See docs/broader_station_screen_1990_2024.md for the actual daily-core screen.
- The full selected 94-location pool has now been assessed in three nested
  windows: 2005–2024, 1995–2024 and 1990–2024. Use
  docs/all94_history_three_windows.md and docs/history_audit_registry.json;
  preserve hourly/daily roles and do not equate missing archives or unmapped QC
  with erroneous measurements. Research scripts under analysis/ do not ingest.
- Prefer usable hourly coverage within 2005–2024, geographic coverage and
  source-aware element quality. Longer histories are a secondary advantage;
  do not replace a useful modern/coastal station solely for weaker pre-2005 data.
- A station's first metadata date or a year file's existence does not establish
  hourly availability. Some early LCDv1 files contain only daily/monthly summaries.
- Historical IDs and reporting schedules can change, including within a year.
  Audit and preserve source identity; do not apply 2020–2024 fixed minutes
  blindly to older observations. See docs/station_history_2000_2024.md.

## Important paths

- `README.md` — setup, migration, and usage documentation
- `src/file_utils.py` — strict station-year filename parsing and discovery
- `src/main.py` — database setup and ingestion orchestration
- `src/weather_data_cleanup.py` — raw CSV cleaning
- `src/ingest.py` — incremental cleaned CSV ingestion
- `src/ghcnh_backfill.py` — historical source-aware adapter and SHA checkpoints
- `sql/schema.sql` — generic multi-year schema and views
- `sql/checks.sql` — multi-year database validation queries
- `sql/backfill_checks.sql` — historical provenance, units and coverage checks
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
python3 src/ghcnh_backfill.py --start 2005 --end 2019
psql -d metpipe_northeast -f sql/backfill_checks.sql
python3 -m unittest discover -s tests -v
```
