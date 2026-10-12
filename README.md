# MetPipe Northeast

MetPipe Northeast is a multi-year data-engineering pipeline for cleaning,
storing, validating, and analyzing NOAA Local Climatological Data observations
from northeastern US airport stations. The local dataset covers twenty stations
from 2020 through 2024, including Provincetown (PVC) and Worcester (ORH).

## Pipeline

1. Download annual station CSVs from the
   [NOAA NCEI LCDv1 bulk archive](https://www.ncei.noaa.gov/data/local-climatological-data/).
2. Discover and clean every station-year source file with pandas.
3. Create or update a non-destructive PostgreSQL schema.
4. Incrementally load every cleaned station-year file with SQLAlchemy.
5. Validate coverage by station and year and query daily, monthly, and annual
   summary views.

Repeated pipeline runs are idempotent at the observation level. The
`(datetime, station)` primary key and PostgreSQL upsert prevent duplicate records,
refresh corrected values, and retain previously loaded years.

## Repository layout

```text
metpipe_phase2/
├── analysis/          # Exploratory multi-year analysis and plots
│   └── station_map.py  # Interactive airport map from NOAA CSV coordinates
├── data/
│   ├── raw/YYYY/      # Original NOAA CSVs by year (not committed)
│   └── processed/YYYY/ # Cleaned CSVs by year (not committed)
├── docs/aws/          # Local AWS reference artifacts (not committed)
├── sql/
│   ├── schema.sql     # Multi-year tables, indexes, and views
│   ├── checks.sql     # Multi-year validation queries
│   └── legacy/        # Superseded 2024-only manual ingestion SQL
├── src/
│   ├── file_utils.py  # Station-year filename parsing and discovery
│   ├── main.py        # Schema and ingestion orchestrator
│   ├── ingest.py      # Incremental cleaned-data loader
│   ├── audit_station_minutes.py # Hourly minute and coverage audit
│   └── weather_data_cleanup.py
├── tests/             # Standard-library unit tests
├── .env.example
└── requirements.txt
```

## Requirements

- Python 3.10+
- PostgreSQL
- Packages in `requirements.txt`

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Create the default local database:

```bash
createdb metpipe_northeast
```

Connection settings can be overridden with environment variables:

| Variable | Default |
| --- | --- |
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `metpipe_northeast` |
| `DB_USER` | Current operating-system user |
| `DB_PASSWORD` | No password |

`.env.example` documents these variables, but the scripts do not automatically
load a `.env` file. Export overrides in the shell before running the pipeline.

## Input naming convention

Put one station and one calendar year in each raw CSV:

```text
data/raw/<year>/<station>_hourly_<year>.csv
```

Examples:

```text
data/raw/2020/bos_hourly_2020.csv
data/raw/2024/bos_hourly_2024.csv
data/raw/2025/bos_hourly_2025.csv
data/raw/2024/pvc_hourly_2024.csv
```

The cleaner produces corresponding files such as
`data/processed/2025/bos_hourly_2025_cleaned.csv`. Flat files directly in
`data/raw/` or `data/processed/` are also accepted for older datasets. A
station-year must appear only once; duplicate files and files placed under the
wrong year folder cause an error. A CSV containing multiple calendar years must
be split before cleaning. All matching years are loaded into the same database
table, so adding an older or newer year never requires concatenating CSVs.

The cleaner expects legacy NOAA LCDv1 columns, including `DATE` and
`HourlyDryBulbTemperature`. The 2020–2024 files are in US customary units
(temperature in °F, precipitation in inches, wind speed in mph, and station
pressure in inHg). LCDv2 bulk CSVs use metric units and require explicit
conversion before mixing them with these records.

## 2020–2024 station network

There are 100 raw station-year CSVs locally. The original 2024 ALB, BOS, JFK,
and PVD files came from the earlier NOAA download; the other 96 files came
from the LCDv1 bulk archive. The archive URL format is
`https://www.ncei.noaa.gov/data/local-climatological-data/access/<year>/<LCDv1 ID>.csv`.
For example, Provincetown 2024 is
[72507364708.csv](https://www.ncei.noaa.gov/data/local-climatological-data/access/2024/72507364708.csv).

| Code | Station | GHCN ID | LCDv1 ID | Checked hourly minute |
| --- | --- | --- | --- | --- |
| ALB | Albany International Airport, NY | USW00014735 | 72518014735 | :51 |
| BOS | Boston Logan International Airport, MA | USW00014739 | 72509014739 | :54 |
| JFK | John F. Kennedy International Airport, NY | USW00094789 | 74486094789 | :51 |
| PVD | Rhode Island T. F. Green International Airport, RI | USW00014765 | 72507014765 | :51 |
| PVC | Provincetown Municipal Airport, MA | USW00064708 | 72507364708 | :56 |
| ORH | Worcester Regional Airport, MA | USW00094746 | 72510094746 | :54 |
| BDL | Bradley International Airport, CT | USW00014740 | 72508014740 | :51 |
| PWM | Portland International Jetport, ME | USW00014764 | 72606014764 | :51 |
| BTV | Burlington International Airport, VT | USW00014742 | 72617014742 | :54 |
| MHT | Manchester Boston Regional Airport, NH | USW00014710 | 74394514710 | :53 |
| AUG | Augusta State Airport, ME | USW00014605 | 72618514605 | :53 |
| BAF | Westfield-Barnes Regional Airport, MA | USW00014775 | 74491514775 | :53 |
| DDH | Bennington William H. Morse State Airport, VT | USW00054781 | 72616654781 | :54 |
| EWB | New Bedford Regional Airport, MA | USW00094726 | 72506594726 | :53 |
| HVN | Tweed-New Haven Airport, CT | USW00014758 | 72504514758 | :53 |
| HYA | Cape Cod Gateway Airport (Hyannis), MA | USW00094720 | 72506794720 | :56 |
| LEB | Lebanon Municipal Airport, NH | USW00094765 | 72611694765 | :53 |
| MVY | Martha's Vineyard Airport, MA | USW00094724 | 72506694724 | :53 |
| PYM | Plymouth Municipal Airport, MA | USW00054769 | 72506454769 | :52 |
| UUU | Newport State Airport, RI | USW00014787 | 72507914787 | :53 |

The minute values were checked from regular `FM-15` reports separately for
every year. Provincetown has the largest gaps: its scheduled-minute hourly
coverage ranges from 95.3% (2024) to 99.8% (2023). Missing hours remain missing
in the hourly view.

## Usage

Clean every discovered raw station-year file:

```bash
python3 src/weather_data_cleanup.py
```

Create or update the schema and incrementally ingest every cleaned file:

```bash
python3 src/main.py
```

Run database validation:

```bash
psql -d metpipe_northeast -f sql/checks.sql
```

Run unit tests:

```bash
python3 -m unittest discover -s tests -v
```

Generate and open an interactive map of the local station network:

```bash
python3 analysis/station_map.py
open outputs/station_map.html
```

The map reads each station's name and coordinates from its newest local raw CSV
that contains those fields. The original four 2024 order downloads omit
coordinates, so the script uses their 2023 bulk files. All 20 confirmed stations
now have local files and appear as equal circles. Future additions in
`analysis/candidate_stations.csv` appear as
hollow diamonds until their raw files are added. Historical report availability
is checked separately from field completeness and database ingestion.
Candidate coordinates were sourced from NOAA's
[LCDv2 station list](https://www.ncei.noaa.gov/oa/local-climatological-data/v2/doc/lcdv2-station-list.txt),
with New Bedford and Bennington checked against their LCDv1 files.
The generated HTML is self-contained: it uses bundled
[Natural Earth](https://www.naturalearthdata.com/about/) public-domain
boundaries and does not request map tiles or require internet access.

## Database objects

Tables:

- `station_metadata`
- `weather_observations`

Views:

- `weather_hourly`
- `weather_daily_summary`
- `weather_monthly_summary`
- `weather_annual_summary`

The monthly view uses a full month date such as `2025-01-01`, preventing
January observations from different years from being combined.

`weather_hourly` selects only regular NOAA `FM-15` reports at the representative
observation minute stored in `station_metadata`. If that report is missing in an
hour, the hour is missing in the view too. This keeps special reports from
silently replacing the scheduled hourly observation. Audit the raw station-year
files before loading new years:

```bash
python3 src/audit_station_minutes.py
```

The audit uses `FM-15` reports to show the dominant minute and the exact-minute
hourly coverage for each station-year. The 2020–2024 archive files have stable
minutes for each of the twenty stations; the checked values are seeded in
`sql/schema.sql`. Ingestion stops if a new file's dominant minute differs from
the stored value. A future reporting-schedule change needs an explicit review
and a year-aware metadata update.

## Migrating from the original 2024 schema

The original `northeast_weather_2024` objects are not modified or deleted. The
recommended migration is to create the new `metpipe_northeast` database and run
the pipeline against the existing cleaned CSVs. This rebuilds the data in the
generic schema while preserving the old Phase 2 database as a reference.

## Data and credentials

CSV datasets, local environment files, generated plots, virtual environments,
and AWS reference PDFs are excluded from Git. Never commit database credentials
or private SSH keys.
