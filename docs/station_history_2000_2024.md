# Station-history feasibility: 2000–2024

Audit date: October 12, 2026.

Follow-up: see [the 1995–2024 screen](station_history_1995_2024.md) for actual
30-year daily-element availability and older SAO hourly-report formats.

Observation-history length is a station-selection criterion for MetPipe. The
criterion means usable observation history for the elements and time resolution
required by an analysis, rather than the earliest date attached to a station
name or NOAA identifier.

## Findings

The current PostgreSQL dataset remains the verified 20-station, 2020–2024
dataset. This feasibility check inspected NOAA's ISD station history and monthly
inventory, then downloaded representative archived LCDv1 station-year files.
It did not import historical expansion data.

Within the requested 2000–2024 window:

- ALB, AUG, BDL, BOS, BTV, JFK, ORH, PVD, and PWM have substantial hourly
  observations in checked 2000 files.
- BAF, HVN, LEB, and MHT have substantial hourly reporting in checked 2004 files.
  Earlier inventory entries can contain mainly daily/monthly summaries.
- DDH, EWB, HYA, MVY, PVC, PYM, and UUU have substantial hourly reporting in
  checked 2005 files, often under an older NOAA ID.
- EWB's 2000 file under ID 99999994726 has 304 daily and 10 monthly summaries,
  but zero FM-15 hourly reports. HVN's 2002 file has 365 daily and 12 monthly
  summaries, but zero FM-15 reports. A file's existence therefore does not
  establish usable hourly coverage.
- PVC's checked 2004 file has only four FM-15 hours. Its 2005 file has 7,958
  unique FM-15 hours (90.8% of the year), mainly at :55; the current 2020–2024
  hourly view uses :56.
- AUG's 2000 file has FM-15 reports in 96.7% of calendar hours, but selecting
  only its modal minute (:50) retains 53.2%. A single minute even per calendar
  year may lose valid records when reporting schedules change within the year.

These are representative-year checks, not a full audit of every year from
2000 through 2024. They identify promising expansion windows and limitations;
they do not establish a continuous, uniformly complete 25-year record for all
20 stations. The dates are not airport opening dates or absolute earliest
observation dates. Other archives and older records may add useful information.

## Representative archived files

`Any FM-15` counts unique calendar hours with at least one FM-15 report.
`Modal minute` is the most frequent FM-15 minute in that particular file.
`At modal minute` counts unique hours at that one minute. Every file below
contains FM-15 reports in all 12 months, but individual hours and elements can
still be absent. Field completeness was not audited for these older samples.

| Station | Sample year | NOAA LCDv1 ID | Any FM-15 hours | Modal minute | Hours at modal minute |
| --- | ---: | --- | ---: | --- | ---: |
| ALB | 2000 | 72518014735 | 98.4% | :51 | 97.9% |
| AUG | 2000 | 72618514605 | 96.7% | :50 | 53.2% |
| BAF | 2004 | 74491514775 | 91.4% | :53 | 91.0% |
| BDL | 2000 | 72508014740 | 97.9% | :51 | 97.0% |
| BOS | 2000 | 72509014739 | 97.7% | :54 | 95.1% |
| BTV | 2000 | 72617014742 | 98.7% | :54 | 98.4% |
| DDH | 2005 | 99999954781 | 99.9% | :54 | 99.9% |
| EWB | 2005 | 99999994726 | 99.8% | :53 | 99.8% |
| HVN | 2004 | 72504514758 | 88.9% | :53 | 88.3% |
| HYA | 2005 | 99999994720 | 99.9% | :56 | 99.9% |
| JFK | 2000 | 74486094789 | 98.2% | :51 | 98.0% |
| LEB | 2004 | 72611694765 | 91.9% | :53 | 91.4% |
| MHT | 2004 | 74394514710 | 78.0% | :53 | 77.4% |
| MVY | 2005 | 99999994724 | 99.9% | :53 | 99.9% |
| ORH | 2000 | 72509594746 | 98.2% | :54 | 95.8% |
| PVC | 2005 | 99999964708 | 90.8% | :55 | 90.0% |
| PVD | 2000 | 72507014765 | 98.2% | :51 | 97.7% |
| PWM | 2000 | 72606014764 | 98.5% | :51 | 97.3% |
| PYM | 2005 | 99999954769 | 99.8% | :52 | 99.7% |
| UUU | 2005 | 99999914787 | 99.9% | :53 | 99.9% |

## Selection and expansion approach

Prefer at least 20 years of usable hourly history where feasible, aiming for
25–30 years for historical variability studies. Treat this as a preference
alongside geographic value and variable-specific quality, not an automatic rule
that excludes a useful nearby station.

A practical first expansion target is 2005–2024 for all 20 stations, followed
by 2000–2004 for stations with suitable hourly records. Label analysis periods
explicitly and use a common overlap period for station-to-station comparisons.

Before expansion ingestion:

1. Resolve historical station IDs and document overlap, location changes, and
   source provenance. ORH, for example, has a checked 2000 file under
   72509594746, while the current project uses 72510094746.
2. Replace the station-wide fixed-minute assumption with time-dependent
   reporting metadata or a documented hourly-report selection rule. Audit
   within-year schedule changes, not just modal minute by year.
3. Keep daily/monthly summaries separate from hourly observations, and retain
   report types such as NSRDB rather than treating every row as an independent
   measured hourly observation.
4. Audit every proposed station-year for exact hourly coverage and source-aware
   field semantics before loading it. Preserve missing periods and quality flags.

A 2000–2024 analysis is a 25-year historical summary. Official NOAA climate
normals use standardized 30-year periods; MetPipe summaries should retain their
actual date ranges and should not be labeled official normals.

Sources:
[NOAA LCDv1 archive](https://www.ncei.noaa.gov/data/local-climatological-data/access/),
[NOAA ISD station history](https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv),
[NOAA ISD monthly inventory](https://www.ncei.noaa.gov/pub/data/noaa/isd-inventory.csv),
and [NOAA climate normals](https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals).

