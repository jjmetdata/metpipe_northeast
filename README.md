# MetPipe Northeast

MetPipe Northeast is a local data-engineering pipeline for cleaning, storing,
validating, and analyzing 2024 NOAA weather observations from four northeastern
US airport stations: Albany (ALB), Boston (BOS), New York–JFK (JFK), and
Providence (PVD).

## Pipeline

1. Download Local Climatological Data CSVs from the
   [NOAA NCEI data tools](https://www.ncei.noaa.gov/cdo-web/datatools/lcd).
2. Clean and standardize the source files with Python and pandas.
3. Create PostgreSQL tables, constraints, station metadata, and analytical views.
4. Load the cleaned station data with SQLAlchemy.
5. Validate coverage, row counts, duplicates, and summary views.

## Repository layout

```text
metpipe_phase2/
├── analysis/          # Exploratory analysis and plots
├── data/
│   ├── raw/           # Original NOAA CSVs (not committed)
│   └── processed/     # Cleaned CSVs (not committed)
├── docs/aws/          # Local AWS reference artifacts (not committed)
├── sql/
│   ├── schema.sql     # PostgreSQL tables, constraints, and views
│   ├── checks.sql     # Manual validation queries
│   └── legacy/        # Superseded manual ingestion SQL
├── src/
│   ├── main.py        # Schema and ingestion orchestrator
│   ├── ingest.py      # Cleaned-data loader
│   └── weather_data_cleanup.py
├── .env.example
└── requirements.txt
```

## Requirements

- Python 3.10+
- PostgreSQL
- The Python packages in `requirements.txt`

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Create the local database before running the pipeline:

```bash
createdb northeast_weather_2024_phase2
```

The scripts read these optional environment variables:

| Variable | Default |
| --- | --- |
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `northeast_weather_2024_phase2` |
| `DB_USER` | Current operating-system user |
| `DB_PASSWORD` | No password |

Copy `.env.example` to `.env` as a reference and export the values in your shell.
The scripts do not automatically load `.env`.

## Usage

Place downloaded files in `data/raw/` using the naming pattern
`<station>_hourly_2024.csv`, then run:

```bash
python3 src/weather_data_cleanup.py
python3 src/main.py
```

`src/main.py` recreates the pipeline tables and views before ingesting the
cleaned files, so it is intended for development runs against the Phase 2
database.

Run the validation queries with `psql`:

```bash
psql -d northeast_weather_2024_phase2 -f sql/checks.sql
```

## Database objects

The pipeline creates two tables:

- `station_metadata`
- `northeast_weather_2024`

It also creates hourly, daily, and monthly analytical views:

- `northeast_weather_2024_hourly`
- `northeast_weather_2024_daily_summary`
- `northeast_weather_2024_monthly_summary`

## Data and credentials

CSV datasets, local environment files, generated plots, and AWS reference PDFs
are intentionally excluded from Git. Do not commit database credentials or other
secrets.
