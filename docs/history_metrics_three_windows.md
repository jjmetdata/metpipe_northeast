# Historical quality metrics in three nested windows

Audit date: October 12, 2026.

Scope expansion: [the all-94 assessment](all94_history_three_windows.md) now
covers every selected location and all original 20 stations in these three
windows. This report preserves the earlier 25-site subset, not the full pool.

## Windows and scope

Use the same source-aware hourly metrics in three nested evaluation windows:

| Window | Calendar years | Expected calendar hours | Sites passing >=95% in all three core fields in every year |
| --- | ---: | ---: | ---: |
| 2005–2024 | 20 | 175,320 | 23/25 |
| 1995–2024 | 30 | 262,992 | 2/25 |
| 1990–2024 | 35 | 306,816 | 2/25 |

The two sites passing every year in the longer windows are BOS and BGM.
In 2005–2024, CON narrowly misses the rule in 2019 (94.418% accepted dew-point
hours), and CNY has substantial wind gaps. All other 23 audited sites pass.

The metrics cover the 25 sites that received full historical core-hour checks,
not all 94 screened locations and not all of the original 20 current stations.
The main history-first shortlist contributes 20 sites; BGR, LGA, BDR, CAR, and
CNY are the five additional comparisons. Nine original sites are in this audit.
Other current coastal/support sites need equivalent full-period calculations
before they can be ranked using these tables.

These comparison windows do not change the proposed 2000–2024 ingestion target,
station membership, map or database. No downloads or ingestion were needed:
the results were recomputed from the previously completed historical audit.

## Metrics

- Per-element accepted-hour coverage: hours containing at least one selected
  routine observation with an explicitly accepted source/QC code, divided by all
  calendar hours in the window. Missing hours and missing files stay in the
  denominator.
- Lowest total core coverage: the lowest whole-window percentage among
  temperature, dew point, and wind speed. It is not the percentage of hours
  where all three are simultaneously available.
- Passing years: years where each of those three fields individually has at
  least 95% accepted hours. The threshold is a project screening rule, not an
  industry-wide station certification standard.
- Weakest year/month: the lowest accepted-hour percentage among the three core
  fields in an individual year/month with an available archive file. Missing
  files are listed separately; a weakest-read-year figure must not conceal them.
- Structured-field presence is retained separately in the companion JSON;
  it is not equivalent to accepted QC coverage.

The strict routine-report/source-QC definitions are unchanged from
quality_history_top20_1990_2024.md. Source-dependent meanings of numeric flags
are preserved. Specials, NSRDB, unknown/blank QC flags and calculated flags are
excluded from the accepted-hour metric. This is a conservative lower bound,
not a homogeneity assessment or proof of physical accuracy.

Whole-period coverage is calculated from hour counts, not by taking an
unweighted mean of rounded annual percentages. Source/QC availability and
report-selection rules must be identical across the three windows.

## Compact comparison

Passing-year ratios are ordered 2005–2024, 1995–2024, 1990–2024.
The first 20 rows are the current history-first shortlist, not the ingested
20-station membership. The final five are additional comparisons.

| Code | Lowest core coverage 2005–2024 | Lowest core coverage 1995–2024 | Lowest core coverage 1990–2024 | Passing years in the three windows |
| --- | ---: | ---: | ---: | --- |
| BOS | 99.96% | 99.66% | 99.71% | 20/20 · 30/30 · 35/35 |
| ORH | 99.47% | 97.13% | 97.08% | 20/20 · 21/30 · 25/35 |
| PVD | 99.86% | 97.59% | 97.88% | 20/20 · 26/30 · 31/35 |
| BDL | 99.93% | 97.39% | 97.75% | 20/20 · 26/30 · 31/35 |
| JFK | 99.88% | 97.78% | 98.10% | 20/20 · 26/30 · 31/35 |
| ALB | 99.96% | 98.64% | 98.71% | 20/20 · 28/30 · 33/35 |
| BTV | 99.89% | 97.28% | 97.67% | 20/20 · 26/30 · 31/35 |
| PWM | 99.82% | 97.44% | 97.80% | 20/20 · 27/30 · 32/35 |
| AUG | 99.70% | 98.28% | 98.11% | 20/20 · 26/30 · 31/35 |
| CON | 99.08% | 97.70% | 98.03% | 19/20 · 24/30 · 29/35 |
| PSM | 99.62% | 98.31% | 98.48% | 20/20 · 28/30 · 33/35 |
| MPV | 99.42% | 98.30% | 98.00% | 20/20 · 27/30 · 31/35 |
| ISP | 99.92% | 99.23% | 99.33% | 20/20 · 29/30 · 34/35 |
| BGM | 99.42% | 99.39% | 99.48% | 20/20 · 30/30 · 35/35 |
| SYR | 99.92% | 97.35% | 97.72% | 20/20 · 26/30 · 31/35 |
| ROC | 99.95% | 98.37% | 98.60% | 20/20 · 27/30 · 32/35 |
| BUF | 99.69% | 97.20% | 97.60% | 20/20 · 26/30 · 31/35 |
| EWR | 99.92% | 98.36% | 98.59% | 20/20 · 27/30 · 32/35 |
| HUL | 99.48% | 97.75% | 97.39% | 20/20 · 24/30 · 28/35 |
| GFL | 99.20% | 97.33% | 96.98% | 20/20 · 23/30 · 26/35 |
| BGR | 99.93% | 96.63% | 97.11% | 20/20 · 26/30 · 31/35 |
| LGA | 99.94% | 97.89% | 98.19% | 20/20 · 26/30 · 31/35 |
| BDR | 99.49% | 96.43% | 92.83% | 20/20 · 24/30 · 24/35 |
| CAR | 99.79% | 95.25% | 91.58% | 20/20 · 24/30 · 24/35 |
| CNY | 92.35% | 77.72% | 66.62% | 7/20 · 11/30 · 11/35 |

## 2005–2024: element-specific results

| Code | Temperature | Dew point | Wind speed | Weakest available-file core year | Weakest available-file core month | Years all three >=95% |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| BOS | 99.96% | 99.96% | 99.98% | 99.86% (2005, dew point temperature) | 98.66% (2005-12) | 20/20 |
| ORH | 99.55% | 99.47% | 99.59% | 97.25% (2018, dew point temperature) | 85.35% (2018-03) | 20/20 |
| PVD | 99.90% | 99.86% | 99.90% | 99.43% (2017, dew point temperature) | 97.31% (2022-01) | 20/20 |
| BDL | 99.94% | 99.93% | 99.96% | 99.76% (2011, dew point temperature) | 97.58% (2011-10) | 20/20 |
| JFK | 99.88% | 99.88% | 99.98% | 98.61% (2020, dew point temperature) | 84.03% (2020-09) | 20/20 |
| ALB | 99.96% | 99.96% | 99.97% | 99.90% (2005, dew point temperature) | 99.44% (2005-11) | 20/20 |
| BTV | 99.94% | 99.90% | 99.89% | 99.20% (2021, wind speed) | 94.76% (2021-12) | 20/20 |
| PWM | 99.90% | 99.85% | 99.82% | 99.32% (2024, dew point temperature) | 94.44% (2024-04) | 20/20 |
| AUG | 99.77% | 99.75% | 99.70% | 98.76% (2024, wind speed) | 90.46% (2022-01) | 20/20 |
| CON | 99.46% | 99.44% | 99.08% | 94.42% (2019, dew point temperature) | 39.65% (2019-07) | 19/20 |
| PSM | 99.62% | 99.63% | 99.64% | 98.56% (2018, dew point temperature) | 93.06% (2018-09) | 20/20 |
| MPV | 99.73% | 99.55% | 99.42% | 97.56% (2008, dew point temperature) | 76.44% (2008-02) | 20/20 |
| ISP | 99.92% | 99.92% | 99.93% | 99.57% (2018, wind speed) | 95.16% (2018-01) | 20/20 |
| BGM | 99.42% | 99.42% | 99.66% | 97.35% (2008, dew point temperature) | 82.50% (2008-09) | 20/20 |
| SYR | 99.97% | 99.96% | 99.92% | 99.72% (2009, wind speed) | 97.85% (2009-07) | 20/20 |
| ROC | 99.95% | 99.95% | 99.95% | 99.73% (2021, dew point temperature) | 97.45% (2007-10) | 20/20 |
| BUF | 99.69% | 99.69% | 99.93% | 95.73% (2021, dew point temperature) | 55.91% (2021-03) | 20/20 |
| EWR | 99.92% | 99.93% | 99.95% | 99.64% (2008, temperature) | 98.66% (2008-10) | 20/20 |
| HUL | 99.79% | 99.69% | 99.48% | 98.61% (2024, wind speed) | 95.43% (2017-03) | 20/20 |
| GFL | 99.24% | 99.20% | 99.26% | 96.95% (2016, dew point temperature) | 81.10% (2007-02) | 20/20 |
| BGR | 99.93% | 99.93% | 99.93% | 99.73% (2008, dew point temperature) | 98.66% (2010-05) | 20/20 |
| LGA | 99.95% | 99.94% | 99.99% | 99.72% (2008, dew point temperature) | 97.92% (2019-09) | 20/20 |
| BDR | 99.56% | 99.52% | 99.49% | 97.76% (2021, wind speed) | 74.86% (2021-11) | 20/20 |
| CAR | 99.89% | 99.86% | 99.79% | 99.17% (2024, wind speed) | 94.25% (2016-02) | 20/20 |
| CNY | 99.39% | 99.33% | 92.35% | 71.95% (2018, wind speed) | 0.00% (2018-11) | 7/20 |

## 1995–2024: element-specific results

| Code | Temperature | Dew point | Wind speed | Weakest available-file core year | Weakest available-file core month | Years all three >=95% |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| BOS | 99.69% | 99.66% | 99.68% | 97.77% (2003, dew point temperature) | 94.62% (1996-05) | 30/30 |
| ORH | 97.20% | 97.14% | 97.13% | 84.98% (2004, temperature) | 32.92% (1996-06) | 21/30 |
| PVD | 97.62% | 97.59% | 97.60% | 82.72% (1998, dew point temperature) | 77.42% (1996-07) | 26/30 |
| BDL | 97.43% | 97.39% | 97.56% | 81.37% (1999, dew point temperature) | 78.06% (1999-09) | 26/30 |
| JFK | 97.78% | 97.78% | 97.83% | 82.77% (1998, dew point temperature) | 79.57% (1998-01) | 26/30 |
| ALB | 98.65% | 98.64% | 98.69% | 82.77% (1999, dew point temperature) | 80.69% (1999-09) | 28/30 |
| BTV | 97.40% | 97.37% | 97.28% | 77.97% (1999, wind speed) | 68.30% (1999-02) | 26/30 |
| PWM | 97.55% | 97.46% | 97.44% | 78.68% (1999, dew point temperature) | 68.75% (1999-02) | 27/30 |
| AUG | 98.47% | 98.41% | 98.28% | 91.45% (1995, dew point temperature) | 81.72% (1995-08) | 26/30 |
| CON | 98.08% | 98.01% | 97.70% | 86.36% (1999, wind speed) | 39.65% (2019-07) | 24/30 |
| PSM | 98.54% | 98.54% | 98.31% | 80.54% (1999, wind speed) | 70.56% (1999-04) | 28/30 |
| MPV | 98.51% | 98.39% | 98.30% | 91.02% (1995, wind speed) | 73.92% (1995-08) | 27/30 |
| ISP | 99.32% | 99.23% | 99.37% | 93.85% (1997, dew point temperature) | 88.98% (1997-01) | 29/30 |
| BGM | 99.41% | 99.39% | 99.54% | 97.35% (2008, dew point temperature) | 82.50% (2008-09) | 30/30 |
| SYR | 97.44% | 97.44% | 97.35% | 78.06% (1999, wind speed) | 68.60% (1999-02) | 26/30 |
| ROC | 98.41% | 98.41% | 98.37% | 83.15% (1998, dew point temperature) | 80.24% (1998-01) | 27/30 |
| BUF | 97.20% | 97.20% | 97.33% | 78.21% (1999, wind speed) | 55.91% (2021-03) | 26/30 |
| EWR | 98.36% | 98.36% | 98.48% | 83.12% (1999, dew point temperature) | 80.64% (1998-01) | 27/30 |
| HUL | 98.01% | 97.93% | 97.75% | 89.73% (1995, dew point temperature) | 71.37% (1995-08) | 24/30 |
| GFL | 97.55% | 97.54% | 97.33% | 88.78% (1995, wind speed) | 58.89% (2001-06) | 23/30 |
| BGR | 96.65% | 96.63% | 98.25% | 44.84% (1996, dew point temperature) | 0.00% (1996-01) | 26/30 |
| LGA | 97.89% | 97.89% | 97.89% | 82.89% (1998, dew point temperature) | 80.24% (1998-01) | 26/30 |
| BDR | 96.48% | 96.43% | 96.50% | 70.89% (1995, dew point temperature) | 70.42% (1995-09) | 24/30 |
| CAR | 96.95% | 95.43% | 95.25% | 70.44% (1995, dew point temperature) | 58.47% (1996-07) | 24/30 |
| CNY | 96.03% | 95.93% | 77.72% | 0.00% (1995, wind speed) | 0.00% (1995-01) | 11/30 |

## 1990–2024: element-specific results

| Code | Temperature | Dew point | Wind speed | Weakest available-file core year | Weakest available-file core month | Years all three >=95% |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| BOS | 99.74% | 99.71% | 99.73% | 97.77% (2003, dew point temperature) | 94.62% (1996-05) | 35/35 |
| ORH | 97.23% | 97.08% | 97.22% | 84.98% (2004, temperature) | 32.92% (1996-06) | 25/35 |
| PVD | 97.91% | 97.88% | 97.89% | 82.72% (1998, dew point temperature) | 77.42% (1996-07) | 31/35 |
| BDL | 97.79% | 97.75% | 97.90% | 81.37% (1999, dew point temperature) | 78.06% (1999-09) | 31/35 |
| JFK | 98.10% | 98.10% | 98.14% | 82.77% (1998, dew point temperature) | 79.57% (1998-01) | 31/35 |
| ALB | 98.72% | 98.71% | 98.75% | 82.77% (1999, dew point temperature) | 80.69% (1999-09) | 33/35 |
| BTV | 97.77% | 97.74% | 97.67% | 77.97% (1999, wind speed) | 68.30% (1999-02) | 31/35 |
| PWM | 97.89% | 97.82% | 97.80% | 78.68% (1999, dew point temperature) | 68.75% (1999-02) | 32/35 |
| AUG | 98.28% | 98.22% | 98.11% | 91.45% (1995, dew point temperature) | 81.72% (1995-08) | 31/35 |
| CON | 98.35% | 98.30% | 98.03% | 86.36% (1999, wind speed) | 39.65% (2019-07) | 29/35 |
| PSM | 98.68% | 98.68% | 98.48% | 80.54% (1999, wind speed) | 70.56% (1999-04) | 33/35 |
| MPV | 98.19% | 98.06% | 98.00% | 91.02% (1995, wind speed) | 73.92% (1995-08) | 31/35 |
| ISP | 99.42% | 99.33% | 99.45% | 93.85% (1997, dew point temperature) | 88.98% (1997-01) | 34/35 |
| BGM | 99.49% | 99.48% | 99.61% | 97.35% (2008, dew point temperature) | 82.50% (2008-09) | 35/35 |
| SYR | 97.81% | 97.80% | 97.72% | 78.06% (1999, wind speed) | 68.60% (1999-02) | 31/35 |
| ROC | 98.64% | 98.63% | 98.60% | 83.15% (1998, dew point temperature) | 80.24% (1998-01) | 32/35 |
| BUF | 97.60% | 97.60% | 97.71% | 78.21% (1999, wind speed) | 55.91% (2021-03) | 31/35 |
| EWR | 98.59% | 98.59% | 98.70% | 83.12% (1999, dew point temperature) | 80.64% (1998-01) | 32/35 |
| HUL | 97.60% | 97.50% | 97.39% | 88.34% (1990, dew point temperature) | 30.51% (1990-03) | 28/35 |
| GFL | 97.19% | 97.15% | 96.98% | 88.78% (1995, wind speed) | 58.89% (2001-06) | 26/35 |
| BGR | 97.13% | 97.11% | 98.50% | 44.84% (1996, dew point temperature) | 0.00% (1996-01) | 31/35 |
| LGA | 98.19% | 98.19% | 98.19% | 82.89% (1998, dew point temperature) | 80.24% (1998-01) | 31/35 |
| BDR | 92.90% | 92.83% | 92.92% | 70.89% (1995, dew point temperature) | 65.73% (1994-07) | 24/35 |
| CAR | 97.38% | 91.74% | 91.58% | 69.22% (1990, dew point temperature) | 58.47% (1996-07) | 24/35 |
| CNY | 82.32% | 82.23% | 66.62% | 0.00% (1995, wind speed) | 0.00% (1995-01) | 11/35 |

## Interpretation

- Many otherwise useful stations are excellent from 2005 onward. ORH and PVD
  pass all 20 recent years despite significant earlier weaknesses.
- BGR's weakest 1995–2024 year is 1996 (~44.84% accepted routine dew-point
  hours), but it passes all 20 years in 2005–2024 and has 99.93% lowest total
  core coverage there. Do not dismiss it as a currently unreliable station.
- BDR similarly improves sharply in the modern window; its strong recent
  performance should not be conflated with complete early-1990s hourly history.
- Adding years can increase an overall percentage when the added years are
  more complete than the existing window. Therefore the 1990–2024 total may
  exceed the 1995–2024 total even though the longer window retains the same
  weak year. This is why the weakest-year and passing-year metrics accompany
  whole-window averages.
- These are nested windows, not three disjoint periods. To isolate the
  incremental cost of backfill, later compare 1990–1994 and 1995–2004 as separate
  blocks against the recent baseline.
- Precipitation cell blanks, trace values, gust reporting and pressure derived
  flags require their own semantics. Do not use the core-hour threshold as
  automatic certification of precipitation, cloud or pressure quality.

## Missing-file treatment and companion data

CNY has no successfully read Parquet file in 1990–1994. Its 1990–2024
whole-window percentages include those unavailable years in the expected-hour
denominator; only 30/35 files were read. All other 24 sites have all 35 yearly
files. None of the unavailable years was silently excluded.

The companion JSON contains 75 station/window records, exact expected-hour
denominators, accepted/present hour counts for seven checked elements, missing
file years, weakest year/month and passing-year counts.
It corrects a denominator limitation in the earlier Central Park-only summary,
which had described its 30 read years rather than a full 35-year denominator.

## Sources

Derived from the existing NOAA GHCNh audit files; see
[NOAA GHCNh](https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly)
and [source-dependent QC documentation](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh_DOCUMENTATION.pdf).
See quality_history_top20_1990_2024.md for the complete selection method and
limitations. Raw monthly audit results remain in the research scratch files.

