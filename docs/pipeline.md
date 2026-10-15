# Pipeline guide

## Layers

| Schema | Purpose | Time / units |
| --- | --- | --- |
| `public` | Preserved LCDv1 observations and historical adapter output | Legacy fixed UTC−5 / customary fields |
| `ghcnh_parallel` | Source-preserving GHCNh routine reports | UTC / SI |
| `metpipe_final` | Per-element reconciled, observed-only hourly snapshot | UTC / SI |
| `metpipe_aux` | CQX auxiliary observations, outside the core twenty | UTC / SI |

The preferred interface is `metpipe_final.weather_hourly_utc`, policy
`observed_2005_2024_v1`. Its 3,506,400 rows form a complete hourly calendar across
20 stations. Individual values may be NULL. The source archives often contain
the same underlying reports and must not be counted as independent samples.

## Load files

LCDv1 inputs use `data/raw/<year>/<station>_hourly_<year>.csv`. Each file must
contain one station and one calendar year. The cleaner writes matching files to
`data/processed/<year>/`; older flat layouts are also accepted. Duplicate
station-years and wrong-year folders are rejected.

```bash
python src/weather_data_cleanup.py
python src/main.py
```

The LCDv1 cleaner expects customary units and fields such as `DATE` and
`HourlyDryBulbTemperature`. Do not feed metric LCDv2 files through it unchanged.

For the legacy historical backfill:

```bash
python src/ghcnh_backfill.py --start 2005 --end 2019
psql -d metpipe_northeast -f sql/backfill_checks.sql
```

This adapter caches NOAA Parquet files, retains raw UTC/SI provenance and converts
to the legacy table's convention. It is restricted to 2005–2019 and cannot
overwrite LCDv1 rows. File hashes make completed source-year loads repeatable.

## Build the finalized source layer

The consistent GHCNh dataset was audited over all 400 station-years and compared
with LCDv1 at matching report times. Publication uses separate schemas and never
unions the archives as extra observations.

```bash
# Read the audit reports and complete their source checks before publication.
python analysis/add_parallel_ghcnh.py --publish
python analysis/publish_final_observations.py --publish
```

These commands write to PostgreSQL. They are not needed to read an existing
dataset or view the saved notebooks. The original publication and compatibility
records are in [network verification](network_ghcnh_verification.md) and
[finalized observations](finalized_observations.md).

The policy considers each element separately. Meaningful unresolved conflicts
become NULL; verified fallbacks retain their own actual report times and evidence.
Known-bad primary QC is not a reason to accept an unchecked secondary value.

## Check the result

```bash
psql -d metpipe_northeast -f sql/checks.sql
python analysis/audit_finalized_availability.py
python analysis/export_availability.py
python -m unittest discover -s tests -v
```

Audits are read-only. The availability exporter uses the small report snapshots
under `reports/`, so regenerating the README charts needs no database connection.

Keep new stations, sampling policies and source revisions versioned. Do not
silently rerun an older scientific study against changed inputs.
