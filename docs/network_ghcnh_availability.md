# All-network GHCNh availability audit

Audit date: October 14, 2026. **Read-only: no database migration, overwrite,
station changes, model retuning, Git commit or push.**

## Decision

**GHCNh is available for all twenty selected stations throughout 2005–2024.**
All **400 station-year files were downloaded/cached, opened and checked** for
station identity and UTC source year. Twenty additional 2025 files were checked
separately: **420 / 420 successful reads**, no unresolved file errors.

Nineteen stations have at least 98.6% aggregate availability for each of
temperature, dew point, relative humidity, station pressure and wind speed.
PVC remains the main historical coverage exception. Some other stations have
weak individual years despite excellent twenty-year averages.

Recommendation: GHCNh is a reasonable **primary historical source for the whole
2005–2024 network**, subject to a staged, source-aware migration and quality
comparison. File/element availability does not certify measurement accuracy.
Do not assume that every element improves, or extend historical completeness
claims into 2025 without its separate element audit.

## Historical availability, 2005–2024

Percent of all 175,320 expected UTC hours per station with a value in the selected
coherent routine report after the existing adapter's known-bad-QC/value screening.
Unknown or calculated QC is retained and counted separately, not certified.

| Station | Routine | Temperature | Dew point | RH | Station pressure | Wind speed | Precipitation* |
|---|---:|---:|---:|---:|---:|---:|---:|
| ALB | 100.00% | 99.99% | 99.99% | 99.99% | 99.87% | 99.99% | 99.75% |
| AUG | 99.96% | 99.81% | 99.79% | 99.79% | 99.82% | 99.70% | 99.55% |
| BAF | 99.93% | 99.34% | 99.31% | 99.31% | 99.51% | 99.65% | 99.34% |
| BDL | 99.98% | 99.96% | 99.95% | 99.95% | 99.64% | 99.96% | 99.41% |
| BOS | 99.99% | 99.98% | 99.98% | 99.98% | 99.79% | 99.98% | 99.60% |
| BTV | 99.98% | 99.95% | 99.90% | 99.90% | 99.59% | 99.89% | 99.68% |
| DDH | 99.80% | 99.22% | 98.85% | 98.85% | 99.59% | 99.07% | 98.74% |
| EWB | 99.95% | 99.25% | 99.05% | 99.04% | 99.52% | 99.67% | 99.46% |
| HVN | 99.90% | 99.34% | 99.34% | 99.33% | 99.44% | 99.71% | 99.06% |
| HYA | 99.95% | 99.72% | 99.69% | 99.69% | 99.35% | 99.58% | 98.81% |
| JFK | 100.00% | 100.00% | 100.00% | 100.00% | 99.33% | 99.99% | 99.03% |
| LEB | 99.95% | 99.76% | 99.75% | 99.75% | 99.72% | 99.67% | 99.57% |
| MHT | 99.98% | 99.64% | 99.63% | 99.63% | 98.99% | 99.93% | 98.89% |
| MVY | 99.90% | 98.76% | 98.70% | 98.69% | 98.82% | 99.40% | 98.15% |
| ORH | 99.91% | 99.69% | 99.61% | 99.60% | 99.42% | 99.61% | 99.17% |
| PVC | 95.90% | 95.17% | 94.62% | 94.61% | 92.79% | 94.86% | 10.61% |
| PVD | 99.97% | 99.94% | 99.90% | 99.90% | 99.56% | 99.91% | 99.62% |
| PWM | 99.98% | 99.94% | 99.88% | 99.88% | 99.78% | 99.80% | 99.55% |
| PYM | 99.83% | 99.56% | 99.48% | 99.48% | 99.36% | 99.42% | 99.07% |
| UUU | 99.88% | 99.78% | 99.73% | 99.73% | 99.63% | 99.63% | 99.48% |

*Precipitation is **selected FM15 compatibility-field presence**, not independently
validated one-hour accumulation coverage. Explicit recorded zero and flagged
trace count as available; missing never becomes zero. NOAA notes that frequent
reports may contain running totals within an hour, so duration-aware last-report
aggregation is still needed before summing rainfall. The coherent core-completeness
selection is not a dedicated precipitation-total selection. PVC's missing amounts
must not automatically be interpreted as dry hours.

Additional audited fields: sea-level pressure, altimeter, wind gust and reported
wind direction/state. Gust presence ranges 9.64–30.33%; this is event-dependent,
not a requirement that every hour contain a gust. PVC sea-level pressure is only
42.65% and altimeter 95.28%. Station pressure, sea-level pressure and altimeter
are distinct fields, not interchangeable observations.

Calm/variable reports are separated from numeric bearings. The source can encode
calm with measurement code C and no valid numeric angle (for example 999 with
zero speed). Counting only angles falsely suggested major direction losses.
The audit counts reported calm/variable states separately and retains numeric-
bearing counts. No calm/variable value is treated as a north-pointing wind vector.
See NOAA documentation Sections IV–VI for definitions and coding.

## Annual/monthly weaknesses

The twenty-year averages do not hide these examples:

- BAF/EWB/HVN: temperature/dew-point/RH availability around 92.7–93.1% in 2006.
- DDH: those elements around 93.2% in 2011.
- MHT: thermodynamic elements around 94.7% in 2006, pressure 91.56% in 2018.
- MVY: temperature/dew point/RH about 90.0–90.2%, pressure 90.86% in 2018.
- JFK: pressure 90.27% in 2024, despite essentially complete temperature history.
- PVC: pressure 61.75% and temperature 62.76% in 2006; no selected routine
  reports at all in October/November 2006. Other years have element-specific
  gaps, including wind speed 82.11% in 2014.

There are 49 core element/station-year cases below the **advisory** 95% threshold.
This is not a new station-replacement rule. All annual/monthly counts and the
full flagged list are exported; retain geographic representation and distinguish
missing observations from inaccurate ones.

## Comparison with current production

The 2020–2024 database primarily preserves LCDv1; older periods already use
GHCNh. We compare the same UTC calendars and existing operational selection,
not identical raw reports or identical source-QC semantics.

For 2020–2024, switching the source/selection gives small coverage increases at
all twenty stations for routine reports, temperature, dew point, RH and wind speed.
Typical thermodynamic/routine gains are about **0.15 percentage points**, not a
dramatic network-wide expansion. Pressure/precipitation can be slightly worse at
some stations, and larger gains occur at several others.

Examples for **2024 station pressure**:

| Station | Current production | GHCNh audit |
|---|---:|---:|
| PVC | 83.66% | 91.78% |
| PYM | 91.40% | 99.45% |
| PWM | 90.98% | 99.23% |
| ORH | 90.80% | 98.84% |
| MHT | 89.56% | 96.89% |
| HYA | 97.17% | 96.93% |
| BOS | 99.52% | 98.91% |
| JFK | 91.18% | 90.27% |

Twelve stations have slightly lower 2024 pressure availability under this GHCNh
selection, while eight gain substantially. More numeric values do not by
themselves mean more accurate measurements. Archive processing, QC, report
selection and the existing CSV cleaning all affect availability.

## Important 2025 readiness limit

All twenty 2025 files exist and were read, but **station pressure is nearly
absent across the network after August**. In September–December, only **32
selected routine station-pressure values** are available across **58,560 expected
station-hours** (about 0.055%). A few late values do not establish continuous
pressure histories. Overall 2025 pressure availability is around 60.7–64.9%.

Temperature and altimeter generally continue, though AUG/MVY have additional
temperature gaps. This pattern does not prove airport pressure sensors stopped;
source feed/processing changes need separate investigation. Do not silently
substitute altimeter for station pressure or assume 2005–2024 completeness
extends into 2025. The prior frozen pressure experiment is unchanged; this is
availability inspection only, not refitting on its test outcomes.

## Quality policy and limits

- Known source-specific suspect/error, failed integrated lowercase flags and
  synthetic/daily/monthly numeric fields are excluded using the existing adapter.
- Unknown flags are **retained but counted separately** to match the current
  ingestion policy. The strict legacy-QC mapping is not complete for every
  element/source. Edited/inserted codes may be legitimate rather than erroneous.
- Most station pressure has source/quality 343/4, gross-limit checks rather than
  independently full-checked sensor accuracy. The known HYA spike shows why
  buddy/temporal QC is still necessary even with high availability.
- RH often has no mapped QC tier and may be calculated from temperature/dew
  point. High availability is not proof of independent humidity measurements.
- One coherent routine row per hour: FM15 priority, then core completeness,
  then latest actual report time. Specials cannot silently fill missing routine
  hours. No per-element best-of-hour cherry-picking or interpolation occurs.
- Historical schedules/site/sensor changes and precision have not been
  homogenized. These are not climate normals, trend validation or forecast skill.
- Cloud decoding and an independently validated precipitation aggregation are
  outside this numerical-element availability audit.

## Reproduce and inspect

```bash
python analysis/audit_network_ghcnh.py
python analysis/report_network_ghcnh.py
python -m unittest discover -s tests -v
```

Defaults audit 2005–2025, separating historical scope from 2025 readiness.
New raw downloads stay in ignored audit outputs, not the production table.
PostgreSQL is accessed through the read-only engine. Raw database row counts
remain **5,381,350 before/after**, and the same twenty station codes are verified.

Generated exports under `outputs/audits/network_ghcnh/`:

- `source_manifest.json`: file URLs, cached/downloaded origin, SHA256, identity,
  raw/routine counts, per-element source/quality distributions.
- `annual_availability.csv`, `monthly_availability.csv`: expected-hour counts,
  element presence, QC categories, trace/calm/variable counts and first/last dates.
- `station_summary_2005_2024.csv`, `station_summary_2020_2024.csv`,
  `station_summary_2025.csv`: per-station period summaries.
- `production_annual_availability.csv`, `source_coverage_comparison.csv`:
  existing-database coverage and comparable calendar-period deltas.
- `core_station_years_below_95.csv`: advisory weak-year/element list.
- `network_ghcnh_availability.html`: self-contained tables and three heatmaps.

Recommended next step: stage GHCNh for the whole historical network, reconcile
values/units/timing/QC against current data, preserve the old source, and only
then select the production source. Availability alone does not authorize a
destructive migration or modeled gap filling.

Primary references: [NOAA GHCNh product information](https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly)
and [NOAA coding documentation](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh_DOCUMENTATION.pdf),
especially Sections IV–VI and IX. Raw-file URLs are in the manifest.
