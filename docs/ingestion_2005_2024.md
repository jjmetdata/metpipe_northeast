# MetPipe 2005–2024 ingestion

Run date: October 12, 2026. Status: **ingestion complete and validated**.

## Scope

Retain the original twenty stations: ALB, AUG, BAF, BDL, BOS, BTV, DDH, EWB,
HVN, HYA, JFK, LEB, MHT, MVY, ORH, PVC, PVD, PWM, PYM and UUU.
PSF, VSF and BDR remain backup candidates and are not ingested.

The existing 2020–2024 LCDv1 data is preserved. The dedicated GHCNh adapter
backfills local-standard-time 2005–2019 using twenty stations × sixteen UTC
source years (2005–2020): 320 Parquet files. The 2020 sources supply only the
last five hours of local-standard-time 2019.

## Preservation and reproducibility

- Database: `metpipe_northeast`.
- Pre-ingestion backup: `data/backups/metpipe_before_2005_2019_2026-10-12.dump`.
- Original observations: 1,297,439; original selected hourly reports: 874,057.
- Original-field checksum: `49070fb6deaa6c8600c9e5819d54bb13`.
- Raw historical sources: `data/raw/ghcnh/<UTC year>/<station>.parquet`.
- Source URLs and SHA-256 checkpoints: `ghcnh_ingestion_files`.
- Each file commits atomically. Identical source/scope checkpoints are skipped.
- Checkpoints track raw source bytes and scope, not converter code versions.
  A future conversion-policy change needs an explicit reviewed reprocessing
  migration; a normal repeat command does not reinterpret existing rows.
- Both loaders protect rows from the other source dataset against overwrite.

Run from the project root with the project virtual environment:

```bash
.venv/bin/python src/ghcnh_backfill.py --start 2005 --end 2019
psql -d metpipe_northeast -f sql/backfill_checks.sql
.venv/bin/python analysis/validate_backfill.py
.venv/bin/python -m unittest discover -s tests -v
```

## Semantics and limitations

- `weather_observations.datetime` uses fixed UTC-5 local standard time, without
  daylight saving changes, consistent with the existing LCDv1 records.
- The compatibility columns use °F, inches, mph and inHg. GHCNh SI values are
  explicitly converted; UTC and raw per-element values/flags remain available.
- `weather_hourly_utc` exposes SI units and UTC. Use actual
  `observation_datetime_utc`, not just the hourly bucket, for lag/model joins.
- Known failed source-specific/integrated QC is masked. Unmapped, unchecked or
  calculated flags are retained and require application-specific screening;
  this ingestion is not a certification that every retained value is correct.
- Synthetic and daily/monthly summary values are excluded from numeric point
  observations. Raw field provenance remains available.
- Historical hourly selection favors routine METAR, then other regular reports,
  then synoptic reports; within that priority, core completeness and latest
  observation break ties. Specials remain stored but cannot fill routine gaps.
- Only scheduled METAR hourly precipitation enters the primary amount column.
  Trace is zero plus a flag. Blanks remain NULL, never automatically dry hours.
  Accumulations/special values remain in source metadata and cached sources.
- Legacy LCDv1 trace treatment is unchanged; its original trace provenance is
  not recovered by this backfill. Source consistency must be considered for
  rainfall analysis. Daily/monthly/annual sums are available-value sums, not
  certified complete precipitation totals.
- The archive/selection policy changes at 2020. Evaluate that source boundary
  before trend analysis or model training; unit conversion alone does not make
  the two archives scientifically homogeneous.
- Coded cloud and ceiling metadata is preserved, not fully decoded into a
  uniform cloud/visibility product. PVC and other historical gaps remain real.
- Station moves, instrument changes and archive revisions are not homogenized.
  Chronological validation is required before forecasting use.

## Validation results

The load contains **5,381,350 point observations**: 4,083,911 new GHCNh records
and 1,297,439 preserved LCDv1 records. All original 20 stations have observations
in all 20 years: 400 station-year combinations. All 320 scoped source-file
checkpoints are present and their row sum matches the historical table count.

The hourly view contains **3,495,851 selected routine hours** (2,621,794 GHCNh
and 874,057 LCDv1). It represents 4,798 of the 4,800 possible station-months.
PVC has no selected routine observations for October and November 2006; those
months remain missing. PVC routine coverage for 2006 is 62.76%, while overall
2005–2024 routine coverage is 95.84%. These are availability figures, not strict
quality-certified core-element completeness figures.

The other nineteen stations have overall routine-hour availability from 99.75%
to 99.97%. Element counts are separate; PVC has only 18,619 selected hourly
precipitation values over the entire window. Do not interpret the remaining
NULL precipitation values as dry hours or use unqualified PVC rainfall totals.

| Station | Routine hours | Coverage of calendar hours | Hourly precipitation values |
| --- | ---: | ---: | ---: |
| ALB | 175,260 | 99.97% | 174,851 |
| AUG | 175,190 | 99.93% | 174,470 |
| BAF | 175,171 | 99.92% | 174,141 |
| BDL | 175,242 | 99.96% | 174,305 |
| BOS | 175,256 | 99.96% | 174,622 |
| BTV | 175,173 | 99.92% | 174,707 |
| DDH | 174,917 | 99.77% | 173,065 |
| EWB | 175,190 | 99.93% | 174,344 |
| HVN | 175,098 | 99.87% | 173,668 |
| HYA | 175,184 | 99.92% | 173,220 |
| JFK | 175,252 | 99.96% | 173,646 |
| LEB | 175,177 | 99.92% | 174,537 |
| MHT | 175,267 | 99.97% | 172,811 |
| MVY | 175,072 | 99.86% | 171,468 |
| ORH | 175,077 | 99.86% | 173,261 |
| PVC | 168,034 | 95.84% | 18,619 |
| PVD | 175,206 | 99.93% | 174,091 |
| PWM | 175,179 | 99.92% | 173,865 |
| PYM | 174,884 | 99.75% | 173,053 |
| UUU | 175,022 | 99.83% | 173,769 |

The first full validation identified one rejected variable-wind label at PWM,
2007-04-17 04:00 local standard time. The numeric value was already masked, but
the measurement flag had restored `VRB`. The adapter now guards that assignment;
the idempotent migration `sql/migrations/001_ghcnh_variable_wind_qc.sql` cleared
only that one GHCNh compatibility value and retained its raw flags. No legacy
records were changed. The final full verification passed after repair.

Final checks confirm the original field checksum and hourly count are unchanged;
UTC/local time and source-year alignment are consistent; converted temperature,
wind, pressure and precipitation round-trip correctly; provenance is retained;
no known rejected/synthetic numeric values survived; and all scoped files and
station-years are represented. Every integrity mismatch counter is zero.

All 21 unit tests pass. A full repeat command marked all 320 files unchanged.
Full station-year element counts, original checksum, source counts and integrity
results are generated at `outputs/audits/ingestion_2005_2024.json` by the read-only
database validator `analysis/validate_backfill.py`.
