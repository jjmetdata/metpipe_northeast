# Broader airport and non-airport history screen, 1990–2024

Audit date: October 12, 2026.

Follow-up: [the expanded history-first hourly screen](history_first_top20_1990_2024.md)
adds regional WBAN sites (94 distinct locations total), GHCNh inventories for
all 35 years, and actual source/QC-aware 1990 and 1995 hourly samples. It finds
older hourly records absent from checked LCDv1 files; do not infer no hourly
history from the daily-only findings in this report.

## Decision framework

Keep 2000–2024 as the proposed working analysis window, while screening station
choices against a potential 1990–2024 expansion. The desired historical reach is
a preference that helps avoid unnecessary replacements, not a rule that
excludes useful short-record local or real-time stations.

This audit adds observatories and Cooperative Observer stations to the search.
They can be excellent daily climate anchors without supplying an hourly record
suitable for station-to-station lag analysis. Classify each station by role
and actual temporal resolution; do not replace hourly airport observations
with daily extrema merely because a daily station has a longer history.

## Scope and method

Actual NOAA GHCN-Daily files were checked for all 35 years from 1990 through
2024, plus a separate 2000–2024 window, for 32 non-airport-related identifiers
(31 locations, because Blue Hill COOP and LCD refer to the same observatory)
and the 30-airport current/backup pool. Two checked airport IDs returned 404.

This is a deliberately selected regional search across MA, RI, CT, NH, VT, ME,
and eastern NY, not an exhaustive search or a ranking of every Northeast station.
Candidates were initially selected for geography, long element inventories, and
where applicable the NOAA HCN designation; actual values, not that designation,
determine the availability results.

The 1990–2024 denominator is 12,784 calendar days; 2000–2024 is 9,132.
Availability requires a value other than -9999 and a blank GHCN-Daily quality
flag. Numeric zeros and precipitation trace values count as available.
Percentages are rounded. A blank quality flag means not rejected by those
archival tests, not proof of physical accuracy or homogeneous instrumentation.
Counts do not independently establish same-day observation periods or exclude
all accumulation/source conventions; those flags need review before analysis.

Years >=95% reports the number of years with at least 95% accepted daily values
for TMAX/TMIN/PRCP respectively. This is a project screen, not official NOAA
normals methodology. Annual and overall percentages can hide monthly gaps.

## Non-airport availability, full 1990–2024 window

| Site | GHCN-Daily ID | TMAX | TMIN | PRCP | Years >=95%: TMAX/TMIN/PRCP (out of 35) |
| --- | --- | ---: | ---: | ---: | --- |
| BLUE HILL COOP (MA) | USC00190736 | 99.68% | 98.89% | 99.99% | 34/33/35 |
| BLUE HILL LCD (MA) | USW00014753 | 100.00% | 99.87% | 100.00% | 35/35/35 |
| AMHERST (MA) | USC00190120 | 99.18% | 98.19% | 99.61% | 33/33/34 |
| E WAREHAM (MA) | USC00192451 | 87.90% | 87.55% | 98.01% | 28/28/30 |
| HYANNIS (MA) | USC00193821 | 89.79% | 89.40% | 94.63% | 23/22/26 |
| HINGHAM (MA) | USC00193624 | 99.45% | 99.51% | 99.33% | 33/33/32 |
| MIDDLEBORO (MA) | USC00194711 | 41.28% | 41.11% | 87.71% | 9/9/21 |
| LAWRENCE (MA) | USC00194105 | 96.19% | 94.26% | 94.67% | 27/22/23 |
| WALPOLE 2 (MA) | USC00198757 | 99.66% | 99.67% | 99.67% | 34/34/34 |
| BELCHERTOWN (MA) | USC00190562 | 46.85% | 46.82% | 99.09% | 16/16/32 |
| ASHBURNHAM (MA) | USC00190190 | 48.58% | 48.57% | 99.47% | 17/17/34 |
| STORRS (CT) | USC00068138 | 90.02% | 89.49% | 90.38% | 21/21/18 |
| NORFOLK 2 SW (CT) | USC00065445 | 97.69% | 96.91% | 98.01% | 31/30/33 |
| GROTON (CT) | USC00063207 | 80.55% | 80.55% | 81.17% | 15/15/15 |
| NORWICH PUBLIC UTILITY PLT (CT) | USC00065910 | 94.81% | 91.26% | 94.83% | 29/27/29 |
| KINGSTON (RI) | USC00374266 | 99.69% | 99.65% | 99.76% | 34/34/34 |
| N FOSTER 1 E (RI) | USC00375270 | 99.95% | 99.91% | 99.99% | 35/35/35 |
| DURHAM (NH) | USC00272174 | 95.17% | 95.10% | 96.62% | 26/25/30 |
| HANOVER (NH) | USC00273850 | 97.46% | 97.32% | 91.30% | 29/29/20 |
| KEENE (NH) | USC00274399 | 95.99% | 95.85% | 95.67% | 31/31/32 |
| SAINT JOHNSBURY (VT) | USC00437054 | 99.74% | 99.93% | 99.95% | 35/35/35 |
| CORNWALL (VT) | USC00431580 | 88.78% | 88.85% | 86.25% | 25/27/20 |
| S LINCOLN (VT) | USC00437612 | 92.72% | 91.50% | 87.34% | 24/21/14 |
| FARMINGTON (ME) | USC00172765 | 97.90% | 97.76% | 97.97% | 33/33/33 |
| GARDINER (ME) | USC00173046 | 99.35% | 98.91% | 99.78% | 33/33/35 |
| CORINNA (ME) | USC00171628 | 98.16% | 97.22% | 98.72% | 33/32/33 |
| BRIDGEHAMPTON (NY) | USC00300889 | 93.66% | 93.44% | 93.38% | 28/28/30 |
| MOHONK LAKE (NY) | USC00305426 | 91.90% | 91.83% | 91.18% | 32/32/31 |
| SARATOGA SPRINGS 4 SW (NY) | USC00307484 | 96.76% | 97.51% | 96.35% | 30/30/29 |
| MT WASHINGTON (NH) | USW00014755 | 99.83% | 99.68% | 100.00% | 35/35/35 |
| PINKHAM NOTCH (NH) | USC00276818 | 98.03% | 97.45% | 97.85% | 32/30/32 |
| CHATHAM (MA) | USC00191386 | 84.95% | 84.12% | 86.00% | 22/22/24 |

## Strongest non-airport starting points

Four identifiers pass >=95% accepted values in every year for all three
elements: Blue Hill LCD (USW00014753), North Foster 1 E RI (USC00375270),
St. Johnsbury VT (USC00437054), and Mount Washington NH (USW00014755).

Blue Hill COOP and Blue Hill LCD must not be counted as two independent stations
or blindly concatenated. Their observed completeness differs, so compare source
definitions and observation periods before selecting a canonical daily series.

Also promising, with explicit exceptions: Walpole 2 MA, Kingston RI, Hingham MA,
Amherst MA, and Gardiner ME. These have roughly 98–100% total coverage but some
years fall below 95%; they are not as uniformly complete as the four above.

Mount Washington is a summit observatory (~1,912 m in the station metadata).
It adds mountain/high-elevation context, not a direct proxy for coastal surface
conditions. Pinkham Notch is useful mountain-valley context but has monthly
gaps and precipitation coverage of only 66.03% in 2015.

Daily availability does not establish availability of hourly humidity, wind,
pressure, cloud, or near-real-time feeds for these sites. Those are separate
checks before any selection for the hourly forecasting network.

## Annual/monthly cautions and the working window

Lowest annual/monthly figures below are the minimum across the three elements,
including wholly missing periods. They are field-presence diagnostics, not
an automatic replacement rule.

| Site | Lowest annual availability, 1990–2024 | 2000–2024 total TMAX/TMIN/PRCP | Lowest monthly availability, 1990–2024 |
| --- | ---: | --- | ---: |
| BLUE HILL COOP | 81.10% | 99.55% / 98.47% / 99.99% | 63.33% |
| BLUE HILL LCD | 98.36% | 100.00% / 99.81% / 100.00% | 78.57% |
| AMHERST | 90.14% | 99.55% / 98.81% / 99.89% | 0.00% |
| E WAREHAM | 0.00% | 84.35% / 83.92% / 97.94% | 0.00% |
| HYANNIS | 44.93% | 90.07% / 90.04% / 96.48% | 0.00% |
| HINGHAM | 91.23% | 99.62% / 99.66% / 99.40% | 0.00% |
| MIDDLEBORO | 0.00% | 57.79% / 57.56% / 82.86% | 0.00% |
| LAWRENCE | 69.86% | 97.00% / 95.52% / 95.05% | 0.00% |
| WALPOLE 2 | 91.78% | 99.53% / 99.54% / 99.54% | 0.00% |
| BELCHERTOWN | 0.00% | 65.58% / 65.55% / 99.07% | 0.00% |
| ASHBURNHAM | 0.00% | 68.00% / 67.99% / 99.27% | 0.00% |
| STORRS | 30.33% | 93.67% / 93.27% / 93.77% | 0.00% |
| NORFOLK 2 SW | 47.95% | 96.87% / 96.52% / 97.22% | 0.00% |
| GROTON | 0.00% | 73.61% / 73.70% / 74.35% | 0.00% |
| NORWICH PUBLIC UTILITY PLT | 11.75% | 92.93% / 92.82% / 92.83% | 0.00% |
| KINGSTON | 91.80% | 99.59% / 99.62% / 99.66% | 0.00% |
| N FOSTER 1 E | 98.90% | 99.98% / 99.92% / 99.99% | 90.32% |
| DURHAM | 47.95% | 93.51% / 93.39% / 95.42% | 0.00% |
| HANOVER | 72.05% | 97.93% / 97.79% / 87.92% | 0.00% |
| KEENE | 32.51% | 94.92% / 94.79% / 93.96% | 0.00% |
| SAINT JOHNSBURY | 98.63% | 99.79% / 99.95% / 99.93% | 92.86% |
| CORNWALL | 0.00% | 99.27% / 99.08% / 95.63% | 0.00% |
| S LINCOLN | 20.49% | 94.00% / 93.34% / 86.14% | 0.00% |
| FARMINGTON | 49.86% | 97.09% / 97.00% / 97.16% | 0.00% |
| GARDINER | 91.51% | 99.23% / 98.86% / 99.88% | 0.00% |
| CORINNA | 80.27% | 97.59% / 97.19% / 98.24% | 0.00% |
| BRIDGEHAMPTON | 6.01% | 92.00% / 91.70% / 91.02% | 0.00% |
| MOHONK LAKE | 0.55% | 88.69% / 88.61% / 87.65% | 0.00% |
| SARATOGA SPRINGS 4 SW | 50.96% | 96.22% / 96.82% / 95.02% | 0.00% |
| MT WASHINGTON | 95.89% | 99.77% / 99.63% / 100.00% | 70.97% |
| PINKHAM NOTCH | 66.03% | 98.01% / 97.77% / 97.34% | 0.00% |
| CHATHAM | 0.00% | 82.00% / 81.56% / 83.10% | 0.00% |

Examples of why metadata alone is insufficient:

- East Wareham: no accepted TMAX/TMIN values for 2017–2018 in the checked file.
- Belchertown and Ashburnham: extensive early temperature gaps despite long
  inventory start/end dates; precipitation coverage is much stronger.
- Middleboro: temperature is absent for 1990–2006 in the checked file.
- Groton COOP: empty years 2006 and 2022; this is distinct from GON airport.
- Cornwall: empty 1997–1998 daily core.
- Mohonk Lake and Bridgehampton: very poor coverage in particular recent
  years; the stations' actual observations may exist elsewhere, so investigate
  alternate archives before calling the sites intrinsically unreliable.
- Chatham COOP's checked inventory ends in 2021. Do not silently stitch it
  to Chatham airport or the older lighthouse series.

## Existing and backup airport pool: daily screen back to 1990

These are daily-core checks only. Refer to backup_candidates_hourly_coverage.md
for representative hourly samples; the airport hourly archive has not been
fully audited for every year from 1990 through 2024.

| Airport code | GHCN-Daily ID | TMAX | TMIN | PRCP | Years >=95%: TMAX/TMIN/PRCP (out of 35) |
| --- | --- | ---: | ---: | ---: | --- |
| ALB | USW00014735 | 100.00% | 100.00% | 99.99% | 35/35/35 |
| AUG | USW00014605 | 99.93% | 99.95% | 99.98% | 35/35/35 |
| BAF | USW00014775 | 75.12% | 75.12% | 75.31% | 26/26/26 |
| BDL | USW00014740 | 100.00% | 100.00% | 100.00% | 35/35/35 |
| BOS | USW00014739 | 100.00% | 100.00% | 99.98% | 35/35/35 |
| BTV | USW00014742 | 99.99% | 100.00% | 100.00% | 35/35/35 |
| DDH | USW00054781 | 73.89% | 73.88% | 74.08% | 25/25/25 |
| EWB | USW00094726 | 80.64% | 80.62% | 76.28% | 27/27/26 |
| HVN | USW00014758 | 65.99% | 65.97% | 65.87% | 23/23/23 |
| HYA | USW00094720 | 76.71% | 76.64% | 75.95% | 27/27/25 |
| JFK | USW00094789 | 100.00% | 100.00% | 100.00% | 35/35/35 |
| LEB | USW00094765 | 75.84% | 75.84% | 75.92% | 26/26/26 |
| MHT | USW00014710 | 76.96% | 77.03% | 76.23% | 27/27/26 |
| MVY | USW00094724 | 75.57% | 75.56% | 75.05% | 24/24/23 |
| ORH | USW00094746 | 99.90% | 99.91% | 99.55% | 35/35/35 |
| PVC | USW00064708 | Not available under checked ID | — | — | — |
| PVD | USW00014765 | 99.98% | 99.98% | 99.98% | 35/35/35 |
| PWM | USW00014764 | 100.00% | 100.00% | 100.00% | 35/35/35 |
| PYM | USW00054769 | 80.66% | 80.66% | 76.19% | 28/28/26 |
| UUU | USW00014787 | 81.02% | 81.00% | 76.20% | 28/28/26 |
| CON | USW00014745 | 99.98% | 99.98% | 100.00% | 35/35/35 |
| BDR | USW00094702 | 100.00% | 100.00% | 100.00% | 35/35/35 |
| MPV | USW00094705 | 99.69% | 99.73% | 94.82% | 35/35/32 |
| ACK | USW00014756 | 75.85% | 75.81% | 75.33% | 24/24/23 |
| PSF | USW00014763 | 73.80% | 73.80% | 73.83% | 25/25/25 |
| AQW | USW00054768 | 80.59% | 80.63% | 76.19% | 28/28/26 |
| VSF | USW00054740 | 80.87% | 80.87% | 76.25% | 28/28/26 |
| EEN | USW00094721 | Not available under checked ID | — | — | — |
| PSM | USW00004743 | 0.00% | 0.00% | 0.00% | 0/0/0 |
| GON | USW00014707 | 71.20% | 71.18% | 70.94% | 25/25/25 |

ALB, AUG, BDL, BOS, BTV, JFK, ORH, PVD, PWM, CON, and BDR pass the proposed
annual daily screen for all 35 years and all three core elements.
PVC and EEN had no downloadable file under the checked IDs; this is not proof
that other observations or identifiers do not exist. PSM's checked GHCN-Daily
file has no TMAX/TMIN/PRCP values in the audit window, despite strong modern
LCD hourly records. Archive and resolution must remain explicit.

## Recommended next steps

1. Maintain a station registry with source IDs, station role (hourly/daily),
   coordinates/elevation and their effective dates, element-specific history,
   monthly completeness, and known gaps. Treat 1990 history as future readiness,
   not as a universal eligibility condition.
2. Adopt 2000–2024 as the working target, but preserve station-specific starts
   and missing intervals. Some airport 2000 LCD files contain only daily
   summaries; a uniform complete hourly 25-year network is not yet established.
   Investigate alternate archives/historical IDs before promising those years.
3. Before broad backfill, fix the fixed-minute hourly selector and preserve
   source/QC/trace metadata and time semantics. Validate a smaller 2015–2019
   expansion, then work backward station-year by station-year.
4. Add daily climate data through a distinct daily-observation schema/path, not
   the existing instantaneous weather_observations table. Keep measurement and
   observation-period definitions when comparing daily data across sites.
5. For the strongest candidate non-airports, separately investigate subdaily
   archives and live-feed availability. Do not promote a daily-only site into
   a lead/lag nowcasting analysis.
6. Review station relocation, instrumentation, observation-time changes and
   homogenization needs before using long records for trends. Availability is
   a necessary screen, not a complete reliability assessment.

Published NOAA normals remain useful for baseline context. A 1990–2024 custom
record spans 35 years, whereas current official normals use 1991–2020. There
is no need to recompute official normals merely to build a forecasting pipeline.

The station map, current 20-station membership, and PostgreSQL observations
were not changed by this research.

## Sources

- [NOAA GHCN-Daily product and source integration](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily)
- [Daily station files](https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/)
- [Element inventory](https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt)
- [Station metadata](https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt)
- [Format, quality, measurement and source flags](https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt)
- [Blue Hill Observatory](https://bluehill.org/)
- [NOAA climate normals](https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals)

Each audited daily file is available as ID.dly under the station-files URL.
Temporary raw downloads and detailed JSON results currently reside in /tmp;
the screening method and results are retained in this report.

