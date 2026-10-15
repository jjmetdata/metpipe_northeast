# GHCNh verification and parallel dataset

Verification date: October 14, 2026. The original dataset is retained.

**Publication completed:** `GHCNh_2005_2024_routine_v1` contains **3,497,180
routine-hour records**, twenty stations and 400 station-years. Every station-year's
row and element counts matched the availability audit before commit. The original
`public.weather_observations` stayed at **5,381,350 rows**; its data and views
were not overwritten or changed. No reconstruction estimates or 2025 data were added.
An immediate rerun verified the same version and counts without appending rows.
All 95 automated tests passed.

## What passed

The 2020–2024 overlap contains **873,773 exact UTC report-time pairs** across
twenty stations and 100 station-years. All **500 station-year/core-element
compatibility checks passed**: temperature, dew point, RH, station pressure and
wind speed. Missing values were excluded from paired differences, not set to zero.

Mean annual-comparison MAE is 0.0247°C for temperature and dew point, 0.0997 hPa
for station pressure and 0.0789 m/s for wind speed. Maximum paired pressure
difference is 0.1691 hPa. Most differences are consistent with source reporting
precision; this does not independently establish sensor accuracy. The two NOAA
archives often represent the **same underlying reports**, not independent sensors.

The engineering gates were written before the comparison. Each station-year
needs at least 500 common valid observations per core element, and both its median
and 95th-percentile absolute differences must be within the following limits:

| Element | Median limit | 95th-percentile limit |
|---|---:|---:|
| Temperature | 0.3°C | 1.1°C |
| Dew point | 0.3°C | 1.1°C |
| RH | 2 percentage points | 7 percentage points |
| Station pressure | 0.2 hPa | 0.6 hPa |
| Wind speed | 0.6 m/s | 1.2 m/s |

These are reproducible compatibility checks for adding a parallel research
dataset, **not a replacement approval or official NOAA certification**. See the
local `outputs/audits/network_ghcnh_verification/` folder for the frozen protocol,
all annual metrics, report-time overlap, largest discrepancies and summary.

## Limitations remain

- GHCNh is not uniformly more complete than LCDv1; see the availability audit.
- Earlier years were checked for source identity, QC handling and hourly/element
  availability, not against an independent reference archive. The modern overlap
  does not establish historical sensor homogeneity or independently validate gaps.
- Gust and precipitation differences are diagnostic only. One paired rainfall
  difference reaches 5.344 mm, despite small typical differences. Accumulation
  duration/report timing requires dedicated verification before rainfall totals.
- PC24 uses an exact 24-hour-earlier report time; missing prior observations
  remain missing. It is diagnostic, not a separate meteorological-skill gate.
- 2025 is not added: the network-wide post-August station-pressure gap remains.
- Unknown/calculated source QC stays explicit in provenance. Passing numeric
  compatibility does not promote unknown QC into certified measurements.

## Additive storage design

`sql/migrations/002_ghcnh_parallel_dataset.sql` creates an isolated
`ghcnh_parallel` schema. It does not change `public.weather_observations` or the
existing hourly/daily/monthly/annual analysis views. It does not union sources,
overwrite an observation or fill a missing value.

- `ghcnh_parallel.dataset_versions`: immutable named import version and verification.
- `ghcnh_parallel.source_files`: 400 station-year identities, URLs, raw paths and SHA256 hashes.
- `ghcnh_parallel.hourly_observations`: one coherent routine record per UTC hour,
  including the actual report time, source/QC/measurement flags and SI values.

Full original Parquet reports remain on disk, including unselected reports and
cloud fields. The new table is a normalized routine-hour dataset, **not a copy of
every raw source row**. Numeric wind bearing is separated from calm/variable
states. Rainfall is deliberately named `precipitation_reported_mm`, not a validated
hourly accumulation. Trace and missing are distinct.

Existing notebooks continue to read the original public views; selecting the
parallel dataset is an explicit future analysis choice. Keep the raw files at
the paths recorded in `source_files`, including audit-cache directories. If a
file is lost, recover it from its recorded URL and verify SHA256 before use.

The original dataset already includes GHCNh for 2005–2019 and LCDv1 for 2020–2024.
Thus the new version supplies a consistent GHCNh 2005–2024 interface, not a second
independent observing network. Never combine the two datasets by counting their
overlapping records twice.

## Reproduce

From the project root using `.venv`:

```bash
.venv/bin/python analysis/verify_network_ghcnh.py
# Explicit database writes; requires complete passing verification:
.venv/bin/python analysis/add_parallel_ghcnh.py --publish
```

The import checks all 400 source hashes, publishes in one transaction, verifies
station-year row and element counts against the availability audit, and checks
that the original observation count is unchanged. Rerunning verifies the same
immutable version instead of appending duplicates. Raw-source changes require a
new version and fresh review, not silently rewriting this one.

## Inspect in DataGrip

Refresh the database and enable the `ghcnh_parallel` schema. Then:

```sql
SELECT *
FROM ghcnh_parallel.hourly_observations
WHERE dataset_version = 'GHCNh_2005_2024_routine_v1'
  AND station = 'BOS'
  AND hour_utc >= TIMESTAMPTZ '2024-01-01 00:00+00'
  AND hour_utc < TIMESTAMPTZ '2025-01-01 00:00+00'
ORDER BY hour_utc;
```

Publication completion is recorded in
`outputs/audits/network_ghcnh_verification/parallel_ingestion_summary.json` and
`ghcnh_parallel.dataset_versions.status`; verification alone is not ingestion.
