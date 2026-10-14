# Ten backup-airport candidates and expansion-window recommendation

Audit date: October 12, 2026.

## Scope

These are ten additional backups, not replacements approved for the current
20-station network. No candidate observations were ingested and the map is
unchanged. The audit checked NOAA LCDv1 files for 1995, 2000, 2005, 2010, 2015,
and every year from 2020 through 2024 for each candidate (100 station-year
checks). Older identifiers were tried where applicable. A five-year aggregate
is fully checked; the older years are representative samples, not proof of
continuous coverage for every intervening year.

Routine-hour availability counts distinct local-standard-time calendar hours
containing FM-15, FM-12, SAO, or SY-SA reports. Special reports, summaries, and
NSRDB rows are excluded. This is deliberately independent of a fixed reporting
minute, and is not identical to the current database's scheduled FM-15 view.
It measures the presence of routine reports, not quality-approved measurements.

## Routine-hour coverage

The 2020–2024 denominator is 43,848 expected calendar hours. Individual leap
years have 8,784 hours and other years have 8,760. Not established means no
routine observations found in the identifiers/files checked; it does not prove
no observations exist elsewhere.

| Code | Airport/location | 1995 sample | 2000 sample | 2005 sample | 2010 sample | 2015 sample | 2020–2024 | Worst recent year |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| CON | Concord, NH | 99.91% | 98.27% | 99.77% | 99.82% | 99.93% | 99.85% | 99.60% (2023) |
| BDR | Bridgeport/Sikorsky, CT | 70.86% | 97.70% | 99.92% | 99.79% | 99.92% | 99.76% | 99.25% (2020) |
| MPV | Montpelier/Knapp, VT | 91.38% | 98.19% | 99.93% | 99.76% | 99.92% | 99.81% | 99.46% (2024) |
| ACK | Nantucket, MA | 64.39% | Not established | 99.99% | 99.98% | 99.78% | 99.74% | 99.44% (2021) |
| PSF | Pittsfield, MA | Not established | Not established | 99.92% | 99.90% | 100.00% | 99.82% | 99.64% (2024) |
| AQW | North Adams, MA | Not established | Not established | 99.89% | 99.95% | 99.98% | 99.74% | 99.32% (2024) |
| VSF | Springfield/Hartness, VT | Not established | Not established | 99.70% | 99.79% | 100.00% | 99.72% | 99.19% (2022) |
| EEN | Keene, NH | Not established | Not established | 96.63% | 99.18% | 99.60% | 99.52% | 97.92% (2024) |
| PSM | Portsmouth/Pease, NH | Not established | Not established | 67.16% | 99.50% | 99.83% | 99.66% | 99.58% (2024) |
| GON | Groton/New London, CT | 62.10% | Not established | 100.00% | 99.90% | 100.00% | 99.92% | 99.82% (2024) |

The monthly ISD inventory shows at least one record of some type in every
month of 2005–2024 for nine candidates. PSM is missing January–March 2005.
Inventory counts include summaries and other report types, so they cannot
certify hourly coverage; the LCD samples above are the stronger evidence.

## Recent element presence

Each percentage below counts expected hours with at least one routine report
containing a nonblank cell for that element. Missing whole hours are included
in the denominator. This is only a structured-field presence check: numeric
parseability, suspect flags, physical plausibility, and homogeneity were not
certified. A present text token is not necessarily an accepted measurement.

| Code | Temperature | Dew point | Wind speed | Wind direction | Station pressure | Precip cell | Sky |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CON | 99.66% | 99.64% | 98.13% | 98.10% | 99.85% | 99.21% | 99.35% |
| BDR | 99.75% | 99.74% | 99.23% | 99.23% | 99.61% | 99.37% | 99.56% |
| MPV | 99.74% | 99.74% | 99.22% | 99.12% | 97.91% | 97.87% | 97.81% |
| ACK | 97.63% | 97.56% | 96.06% | 96.07% | 96.16% | 94.68% | 97.52% |
| PSF | 99.26% | 98.71% | 98.75% | 98.75% | 97.95% | 97.67% | 97.44% |
| AQW | 98.58% | 98.04% | 97.27% | 97.27% | 99.23% | 98.97% | 98.93% |
| VSF | 99.54% | 99.52% | 98.94% | 98.94% | 97.79% | 97.85% | 97.51% |
| EEN | 98.26% | 98.25% | 97.91% | 97.91% | 83.36% | 19.78% | 95.19% |
| PSM | 99.66% | 99.65% | 99.66% | 99.66% | 94.26% | 14.22% | 94.35% |
| GON | 99.65% | 99.48% | 99.54% | 99.55% | 98.99% | 97.73% | 99.08% |

Precipitation cell presence must not be interpreted as precipitation-observation
completeness: stations differ in explicit-zero and trace reporting. Low values
at EEN and PSM require inspection of raw METAR precipitation and sensor-status
groups before any decision about rain usability. Do not replace blank amounts
with zero. Gusts were not used as a completeness requirement because their
reporting is conditional.

EEN station pressure (83.36%) and PSM pressure/sky (~94%) are genuine structured
field availability cautions, even though hourly report coverage is high.
ACK has ~96% wind and pressure presence and ~97.6% temperature/dew-point
presence; it is geographically valuable but not the cleanest all-element backup.

## Geographic value and priority

- CON: strong central NH backup to MHT; excellent sampled hourly history and
  previously checked 30-year daily core.
- BDR: strong southwestern coastal backup to HVN/BDL/PVD; excellent modern
  hourly coverage and previously checked 30-year daily core.
- PSF: western Massachusetts/Berkshires; strong modern hourly coverage and
  adds elevated inland context.
- GON: eastern Connecticut coast; strong recent report and field availability.
- MPV: northern Vermont interior; strong hourly backup to BTV. Its daily
  precipitation archive has a 1997 gap, which is a separate issue from recent
  hourly availability.
- VSF: southern Vermont/Connecticut River valley; strong modern hourly option.
- AQW: northwestern Massachusetts; useful geography, but wind/dew-point fields
  are slightly less complete than PSF.
- ACK: offshore maritime contrast southeast of Cape Cod; useful but with larger
  element gaps than its report coverage alone suggests.
- EEN: southwestern NH; conditional backup because of station-pressure gaps
  and 2024 routine-hour coverage of 97.92%.
- PSM: NH seacoast; conditional backup because of pressure/sky gaps and partial
  2005 coverage. Start later or preserve the missing months explicitly.

This ranking is an availability/geography screen, not a statement that the
stations have equal predictive value. Station-to-station skill must be tested.

## Source IDs and reporting minutes

Modal routine minute is descriptive, not a validated permanent selection rule.

| Code | LCDv1 IDs with routine samples | Modal minute 2005 | Modal minute 2024 |
| --- | --- | --- | --- |
| CON | 72605014745 | 51 | 51 |
| BDR | 72504094702 | 54 | 52 |
| MPV | 72614594705 | 51 | 51 |
| ACK | 72506014756, 72506314756 | 53 | 53 |
| PSF | 74410414763, 99999914763 | 54 | 54 |
| AQW | 72507554768, 99999954768 | 52 | 52 |
| VSF | 72611554740, 99999954740 | 54 | 54 |
| EEN | 72616594721, 99999994721 | 55 | 56 |
| PSM | 72605504743, 99999904743 | 55 | 55 |
| GON | 72504614707 | 56 | 56 |

BDR changed from mainly :54 to :52; EEN from mainly :55 to :56. Additional
FM-12 reports often appear at :00. The pipeline must define a consistent
routine-report priority and within-hour selection policy rather than combine
different report types indiscriminately or apply the current minute to all years.

Checked ACK, PSF, AQW, VSF, and GON 2000 files contain 304 SOD and 10 SOM
summaries but no routine hourly rows. Their existence is not an hourly backfill
qualification. Older 1995 observations use SAO-family codes.

## Recommended data length and next steps

Target 2005–2024 as the first network-wide hourly expansion window, subject to
a full station-year and monthly/element audit. It offers 20 years of events
without immediately introducing the pre-METAR report transition and numerous
early summary-only files. PVC's 2005 sample is only 90.8% complete; a common
window is an analysis target, not permission to pretend every station is complete.

1. First make the hourly selector time-dependent/source-aware, preserve
   suspect/trace/missing semantics and provenance, and establish UTC conversion
   from LCDv1 local standard time.
2. Audit all intended 2005–2019 station-years before ingestion. Begin a smaller
   2015–2019 backfill to validate the updated workflow, then expand to 2005.
   Download/ingest independently by station-year; do not invent missing hours.
3. Use a chronologically held-out recent block (for example 2020–2024) for
   lag/sequence and forecasting evaluation. Avoid random-row splits that leak
   adjacent hours or parts of the same weather event across train/test sets.
4. Backfill 2000–2004 selectively after checking whether those extra years
   materially improve event coverage or out-of-sample performance.
5. Treat 1995–2024 and 1990–2024 as later, purpose-driven research extensions,
   not prerequisites for nowcasting. More history cannot substitute for
   good timing, quality control, live data, radar, and model alignment.

Historical observations alone cannot evaluate corrections to historical HRRR,
GFS, or ECMWF forecasts without corresponding archived forecasts, issue times,
valid times, and model-version metadata. Availability of those archives should
help determine the eventual model-training window.

For climatological context, use official NOAA 1991–2020 normals where available
(the standard period is 1991–2020, not 1990–2020). Do not assume every airport
has official hourly normals for every variable.

NOAA now describes LCDv1 as deprecated, with data through August 29, 2025 and
no future updates. LCDv2 uses metric units and GHCNh/GHCNd sources. Build an
explicit format/unit adapter before using newer annual files; do not route
LCDv2 blindly through the current LCDv1 cleaner.

## Sources and reproducibility

- [NOAA LCD product, version change and variable coverage](https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- [LCDv1 annual archive](https://www.ncei.noaa.gov/data/local-climatological-data/access/)
- [ISD station history](https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv)
- [ISD monthly inventory](https://www.ncei.noaa.gov/pub/data/noaa/isd-inventory.csv)
- [NOAA official climate normals](https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals)

For a sample, append YEAR/ID.csv to the LCDv1 annual archive URL using the ID
table above. Audit scratch files and full station-year results are currently in
/tmp/metpipe_backup_*.csv and /tmp/metpipe_backup_results.json; these are
temporary downloads, not part of the ingested database. The methodology and
aggregate results are retained in this report.

