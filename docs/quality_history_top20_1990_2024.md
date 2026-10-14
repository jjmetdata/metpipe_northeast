# History-first top 20: full core-hourly screen, 1990–2024

Audit date: October 12, 2026.

Scope expansion: [all 94 selected locations](all94_history_three_windows.md)
have now received a three-window assessment, including all original 20 stations.
This history-first shortlist should not be treated as the final network or as
a reason to discard stations with strong recent/coastal observational value.

Period comparison: [the three-window metrics](history_metrics_three_windows.md)
recalculate the same screen for 2005–2024, 1995–2024 and 1990–2024. The shorter
modern window performs much better and should inform station-specific roles.

## Result

The following 20 are a recommended history-first candidate pool for MetPipe's
hourly backbone, balancing historical availability, geography, and retention
of current stations. They are NOT 20 uniformly complete or fully certified
stations. Under a conservative >=95% annual threshold for accepted temperature,
dew point, and wind-speed hours, only BOS and BGM pass every one of the 35 years
among the 25 sites fully checked.

This follows the daily screen of 95 identifiers / 94 distinct regional locations,
GHCNh inventory checks for every year 1990–2024, and actual early PSV samples.
It adds full station-year Parquet checks for 25 sites: 875 attempted years,
870 read successfully, and 5 missing Central Park files (1990–1994).
All 700 station-years for the selected 20 were read successfully.

The map, database, and current 20 memberships are unchanged. This document
supersedes the sample-only recommendation in history_first_top20_1990_2024.md.
Bangor and LaGuardia are no longer in the primary shortlist: Bangor has a severe
1996 temperature/dew-point gap, while LaGuardia is redundant with JFK/EWR for
this regional selection. Houlton and Glens Falls are included instead.

## Top 20

Total core coverage is the lowest of three whole-period accepted-hour percentages:
temperature, dew point, and wind speed. Worst year is the lowest of those fields
in any year. Years >=95% means ALL THREE pass the threshold in that year.

| Code | Station | Status | Lowest total core coverage, 1990–2024 | Weakest core year | Years all three >=95% |
| --- | --- | --- | ---: | ---: | ---: |
| BOS | Boston/Logan, MA | Existing | 99.71% | 97.77% (2003) | 35/35 |
| ORH | Worcester, MA | Existing | 97.08% | 84.98% (2004) | 25/35 |
| PVD | Providence, RI | Existing | 97.88% | 82.72% (1998) | 31/35 |
| BDL | Bradley, CT | Existing | 97.75% | 81.37% (1999) | 31/35 |
| JFK | New York/JFK, NY | Existing | 98.10% | 82.77% (1998) | 31/35 |
| ALB | Albany, NY | Existing | 98.71% | 82.77% (1999) | 33/35 |
| BTV | Burlington, VT | Existing | 97.67% | 77.97% (1999) | 31/35 |
| PWM | Portland, ME | Existing | 97.80% | 78.68% (1999) | 32/35 |
| AUG | Augusta, ME | Existing | 98.11% | 91.45% (1995) | 31/35 |
| CON | Concord, NH | Candidate | 98.03% | 86.36% (1999) | 29/35 |
| PSM | Portsmouth/Pease, NH | Candidate | 98.48% | 80.54% (1999) | 33/35 |
| MPV | Montpelier, VT | Candidate | 98.00% | 91.02% (1995) | 31/35 |
| ISP | Islip/MacArthur, NY | Candidate | 99.33% | 93.85% (1997) | 34/35 |
| BGM | Binghamton, NY | Candidate | 99.48% | 97.35% (2008) | 35/35 |
| SYR | Syracuse, NY | Candidate | 97.72% | 78.06% (1999) | 31/35 |
| ROC | Rochester, NY | Candidate | 98.60% | 83.15% (1998) | 32/35 |
| BUF | Buffalo, NY | Candidate | 97.60% | 78.21% (1999) | 31/35 |
| EWR | Newark, NJ | Candidate | 98.59% | 83.12% (1999) | 32/35 |
| HUL | Houlton, ME | Candidate | 97.39% | 88.34% (1990) | 28/35 |
| GFL | Glens Falls, NY | Candidate | 96.98% | 88.78% (1995) | 26/35 |

The list retains nine original sites, not most of the 20. Keeping most of the
old sites and demanding uniformly good 1990s hourly coverage conflict on the
checked evidence. The other original sites can stay as a useful modern/coastal
support layer; a historical core need not replace all local observations.

The table order groups retained and additional sites; it is not a precise
skill ranking. Buffalo/Rochester are distant upstream context, not substitutes
for coastal Massachusetts. JFK/EWR/ISP overlap geographically but sample
different environments; test incremental value before optimizing a final count.

## Method and limits

NOAA GHCNh station/year Parquet files were checked for every calendar year
1990–2024. Expected-hour denominators are 8,760 or 8,784 per year, and 306,816
over the whole period. Each element/hour counts once when at least one
selected routine report contains a value with an explicitly accepted QC flag.

Report types: FM15, FM12, SAO, SYSA, SYMT, SYAE, SYAU, SSA, SAAU.
Special reports and NSRDB are excluded. Thus this measures scheduled/routine
core-hour availability, not the maximum information recoverable from all
valid special observations. Missing routine reports can coexist with useful
special observations; they must not be labeled erroneous measurements.

Source-aware strict QC acceptance:
- Sources 220/221/222/223/347/348: code 1 = good.
- Sources 313/314/315/322/335/343/344/346: codes 1/5 = passed all QC.
- Blank/unknown QC flags, calculated flags and other flags do not count toward
  this conservative lower bound. Code 5 means removed for source 223, not good.

The Parquet/PSV files have different publication dates and can reflect different
archive revisions. Current PSV spot-checks confirmed the highlighted PVD 1998
and BGR 1996 deficiencies found in Parquet; they are not merely assumptions
from metadata. Preserve an archive snapshot/version in future reproducible runs.

This is not a homogeneity or physical-accuracy certification. It does not check
station moves, sensor siting/calibration, representativeness, or whether all
valid source records were successfully harmonized. Those remain separate
station-history/source-reconciliation tasks.

Wind direction, station-level pressure, sea-level pressure and precipitation
were also measured as structured routine-field presence and strict-flag hours
in the raw results, but they are NOT qualification gates in this shortlist.
Pressure is often calculated or lacks an explicitly accepted legacy flag, so
low strict-good station-pressure counts must not be equated to absent pressure;
sea-level pressure has different coverage. Precipitation traces, zero/blank
conventions, accumulation windows and sensor-status semantics need separate
source-aware qualification. Sky/cloud fields were not fully audited.

Annual values hide monthly holes. Boston's weakest core month is 94.624%;
Worcester has a month with only 32.917% routine accepted wind hours (June 1996).
Use month/element masks, not a station-wide good/bad label.

## What this changes from the earlier discussion

- Strong daily climate coverage did not establish complete hourly coverage.
  Even original major airports have weaker historical years.
- BDR is NOT an automatic full-period hourly improvement over HVN: full-period
  core totals are about 92.8–92.9%, with a ~70.9% weakest year.
- Bangor's daily record is excellent, but 1996 accepted routine temperature and
  dew-point hours are only ~44.9%. It is a reserve pending source recovery,
  not a top choice for uninterrupted all-element hourly history.
- Houlton/Glens Falls have lower totals than some metropolitan sites, but
  less extreme weakest-year core gaps than Bangor and add geographic coverage.
- PSM and MPV are promising hourly archives despite limitations in the checked
  GHCN-Daily series; qualifying their precipitation is a separate step.
- The original nine retained sites are reasonable long-record candidates,
  but only Boston meets the proposed every-year >=95% core-hour rule.

Do not replace a station merely because a single archive has a gap. Look for
alternate IDs/sources and distinguish station reporting gaps, QC rejection,
archive harmonization gaps, and missing rows in the project pipeline.

## Non-airport climate-support candidates

Keep these in the broader candidate registry, but not as interchangeable
continuous-hourly replacements:

- Blue Hill Observatory MA: excellent 1990–2024 daily core; no canonical
  GHCNh 1990/1995 files in the checked archive. Investigate observatory archives.
- North Foster RI: excellent daily core; continuous historical hourly coverage
  not established.
- St. Johnsbury VT: excellent daily core. A separate nearby ASOS identifier
  USW00054742 was checked: no 1990 inventory file, and sparse core inventory
  in 1995. Do not silently splice it into the COOP daily series.
- Mount Washington NH: excellent daily core, but different reporting frequency;
  1990 routine-hour coverage is about 50%, not a coastal surface proxy.
- Caribou WFO ME: excellent daily series; the full hourly screen finds early
  core dew-point/wind gaps, with the weakest year around 69.2%. Climate or
  temperature support remains useful, but not an all-element hourly substitute.
- Central Park NY: excellent daily core, but wind is missing/limited in the
  historical hourly archive and 1990–1994 Parquet files were unavailable.

Non-airport status does not guarantee, or disqualify, reliability; resolution,
element availability and source/QC evidence determine the role.

## PVC and modern coastal support

PVC remains a local-target exception, not a fully qualified uninterrupted
1990–2024 core site. Actual 1990 GHCNh observations exist, but its early core
accepted hours are only roughly 30–32%, improving greatly by 1995.
Keep its observations if Provincetown matters; an inland airport cannot replace
them physically. HYA, MVY, EWB, PYM and other recent coastal stations can remain
as modern support with explicitly shorter usable periods.

## Recommended next action

1. Retain the present data and classify stations into long-record core,
   modern/coastal support, and daily climate support.
2. Investigate the worst-year/month gaps and source crosswalks for the retained
   stations before replacing them. Do not infer bad measurements from absence.
3. Preserve source/QC and timestamps, replace fixed historical-minute assumptions,
   then ingest 2000–2024 station-years with explicit coverage masks.
4. Expand to 1990 later with documented usable windows and no artificial filling
   of unavailable observations.
5. Audit precipitation/pressure/cloud requirements before finalizing a network
   for forecast correction. Test station utility on chronological held-out events.

## Sources and retained evidence

- [NOAA GHCNh product and QC](https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly)
- [Source-dependent QC and report types](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh_DOCUMENTATION.pdf)
- [Hourly station-year data](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/index.html#hourly/access/by-year/)
- [GHCN-Daily data](https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/)

Full-period annual core-hour summaries for all 25 tested sites are retained in
hourly_core_history_summary_1990_2024.json. Detailed monthly and additional
element scratch results are in /tmp/metpipe_full_hourly_results.json and
/tmp/metpipe_extra_full_hourly_results.json. Neither dataset was ingested.

