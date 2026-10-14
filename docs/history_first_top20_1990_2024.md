# Provisional history-first hourly shortlist: 1990–2024

Audit date: October 12, 2026.

Superseded by [the full core-hourly screen](quality_history_top20_1990_2024.md):
25 sites were checked year by year, and the final history-first candidate list
replaces Bangor/LaGuardia with Houlton/Glens Falls. Only BOS and BGM meet the
proposed every-year >=95% core-hour threshold. This earlier document preserves
the sample-based findings but is not the current recommendation.

## What this list establishes

This is a 20-candidate priority list for full historical hourly qualification,
not certification that all 20 have good data for every element in every month
of 1990–2024. Nine current stations are retained in this long-record shortlist.
The other current stations remain in the database; no replacements, deletions,
map changes, or historical ingestion were performed.

The search now covers 95 GHCN-Daily identifiers representing 94 distinct
locations, after expanding to qualifying long-record WBAN sites across New
England, New York, and New Jersey. Two checked daily IDs returned 404.
A daily inventory start date was only a discovery filter; actual daily values
were audited separately for 1990–2024 and 2000–2024.

New evidence: NOAA GHCNh v1.1.0 has observations absent from checked older LCDv1
files. Older LCD file absence or summary-only content must not be equated to
absence of historical hourly observations. This affects PVC, EWB, and other
current stations, and PSM's early record in particular.

The audit downloaded GHCNh annual inventory archives for every year 1990–2024,
finding 2,321 station-year inventory entries across the screened IDs. Inventory
field presence confirms archival availability, not expected-hour completeness
or source/QC acceptance. Its published coverage percentages were not treated
as our calendar-hour completeness measures.

Actual GHCNh PSV samples were then downloaded for 1990 and 1995 for 37 current,
backup, and newly discovered hourly candidates (74 station-year checks).
The selected report types were FM15, FM12, SAO, SYSA, SYMT, SYAE, SYAU, SSA,
and SAAU; NSRDB, specials and daily/monthly summaries were excluded.

## Provisional top 20 for hourly qualification

The sample percentage below is the lowest of the temperature, dew-point, and
wind-speed accepted-hour percentages across the two checked early years.
Denominator: every calendar hour in each year (8,760 in 1990 and 1995).
An hour is present if at least one selected routine report supplies the element.

Strict good acceptance is source-specific: source codes 220/221/222/223/347/348
require quality code 1 (good), whereas sources 313/314/315/322/335/343/344/346
require code 1 or 5 (passed all QC checks). Blank/unknown quality codes and
calculated codes are outside this conservative metric. Numeric code 5 must NOT
be accepted for source 223: it means removed there, rather than passed QC.
This metric does not certify physical accuracy or homogeneous observations.
GHCNh dates are used as supplied; the project LCD local-time selector was not used.

| Code | Station | State | Membership | Lowest strict-good core-hour coverage in 1990/1995 samples | Inventory years with temperature/dew point/wind |
| --- | --- | --- | --- | ---: | ---: |
| BOS | Boston/Logan | MA | Existing | 99.99% | 35/35 |
| ORH | Worcester | MA | Existing | 90.92% | 35/35 |
| PVD | Providence/T. F. Green | RI | Existing | 100.00% | 35/35 |
| BDL | Bradley | CT | Existing | 99.99% | 35/35 |
| JFK | New York/JFK | NY | Existing | 99.98% | 35/35 |
| ALB | Albany | NY | Existing | 98.86% | 35/35 |
| BTV | Burlington | VT | Existing | 100.00% | 35/35 |
| PWM | Portland | ME | Existing | 99.91% | 35/35 |
| AUG | Augusta | ME | Existing | 91.45% | 35/35 |
| CON | Concord | NH | New candidate | 99.94% | 35/35 |
| PSM | Portsmouth/Pease | NH | New candidate | 99.89% | 35/35 |
| MPV | Montpelier/Knapp | VT | New candidate | 91.02% | 35/35 |
| BGR | Bangor | ME | New candidate | 92.04% | 35/35 |
| ISP | Islip/MacArthur | NY | New candidate | 99.67% | 35/35 |
| BGM | Binghamton | NY | New candidate | 99.95% | 35/35 |
| SYR | Syracuse | NY | New candidate | 99.95% | 35/35 |
| ROC | Rochester | NY | New candidate | 100.00% | 35/35 |
| BUF | Buffalo | NY | New candidate | 100.00% | 35/35 |
| EWR | Newark | NJ | New candidate | 100.00% | 35/35 |
| LGA | LaGuardia | NY | New candidate | 99.99% | 35/35 |

The order groups retained and new candidates; it is not a fine-grained ranking.
Historical continuity and source-aware early core-hour coverage dominate this
shortlist. It is not yet a geographically optimized final 20-station network.
In particular, JFK/LGA/EWR/ISP provide some redundant regional coverage, while
Buffalo and Rochester are distant upstream sites rather than Cape-local proxies.
Their inclusion reflects strong history; evaluate redundancy and skill before
changing the operational network.

All entries have positive inventory presence for the three core fields in all
35 years. That statement does not imply every hour is observed or good. The
18 sites other than PSM and MPV also pass the previous >=95%-per-year daily
TMAX/TMIN/PRCP screen across all 35 years. PSM's checked daily core is absent;
MPV's daily precipitation has a 1997 gap. Those daily limitations do not negate
their observed hourly archive, but required precipitation must be independently
qualified.

## Important cautions

- ORH, AUG, MPV, and BGR have early sample accepted-hour minima around 91–92%,
  not near-perfect coverage. Their weaker periods need monthly review.
- PSM's newer hourly archive supports reconsidering it despite older LCD
  retrieval failures. Its modern structured pressure/sky gaps still require
  attention; the low precipitation-cell fraction cannot simply be called missing
  rainfall because explicit-zero conventions differ.
- BDR has an excellent daily core, but strict early hourly sample coverage is
  only about 71% for the weakest of temperature/dew point/wind. It is not an
  established 1990s hourly quality upgrade over every current coastal station.
- No sky, visibility, pressure, precipitation accumulation, or direction field
  has been fully QC-audited for all 35 years. Gust completeness is conditional.
- A complete monthly, report-frequency, element/QC, and station-history audit
  of all 700 proposed station-years remains necessary before calling this a
  qualified full-period hourly network.

## Current stations outside the long-record shortlist

The early samples support investigating replacement for historical analysis,
rather than assuming the stations are currently unreliable:

- BAF: weakest core accepted-hour coverage about 54% in the early samples.
- EWB: about 47%; HVN: dew point about 0.08–0.09%; HYA: about 61%; MVY: about
  0.39% in 1990 dew point and about 45% in 1995 dew point.
- LEB: about 62% in 1995; MHT: about 73% in 1990 dew point.
- PYM: no checked 1990 file, and about 56% in 1995.
- DDH and UUU: no checked 1990 or 1995 files under the canonical IDs.
- PVC: strict accepted core-hour coverage about 30% in 1990, improving to
  roughly 94–96% in 1995. NOAA GHCNh does have 1990 observations, contradicting
  any broader inference of no historical airport observations from LCD/GHCNd
  retrieval failures.

EWB's actual GHCNh 2000 file contains substantial FM15 observations, even
though the checked LCDv1 2000 file only had summaries. This is direct evidence
that alternate-source reconciliation can recover usable backfill.

PVC should remain a separate local-target station if Provincetown remains
important; it cannot honestly be described as uniformly good throughout the
full 1990–2024 window on this evidence. Nor should inland stations be considered
physical substitutes for Cape/coastal observations. Keep HYA/MVY/EWB/PYM and
other useful recent stations as a modern coastal support layer where warranted.

Retaining most of the original 20 and demanding uniformly strong 1990s hourly
coverage are competing preferences on current evidence. Do not force a count
by silently accepting sparse years.

## Non-airport long-record complements

These should be included in the wider dataset search and registry, even where
they cannot fill a continuous hourly-network slot:

- Blue Hill Observatory MA (USW00014753): excellent daily history; only 27
  GHCNh inventory year files and 24 with the three core fields in this window;
  no checked canonical 1990 or 1995 PSV file. Its COOP daily ID is the same site,
  not an independent station. Other observatory archives merit investigation.
- North Foster RI (USC00375270): excellent 35-year daily core; no matched
  canonical-ID GHCNh inventory entries in this audit.
- St. Johnsbury VT (USC00437054): excellent 35-year daily core; no matched
  canonical-ID GHCNh inventory entries in this audit. Alternate hourly IDs may
  exist and require explicit crosswalks.
- Mount Washington NH (USW00014755): excellent daily core, but only about
  50% routine-hour coverage in the 1990 sample, reflecting a different reporting
  pattern. Do not assume daily completeness equals an hourly schedule.
- Caribou WFO ME (USW00014607): excellent daily record and non-airport identity,
  but early strictly accepted dew-point/wind hours are around 69–70%. Good as a
  climate/temperature candidate, not yet an all-element hourly core substitute.

## Recommended decision

Use this list to prioritize source-aware full-period validation, not to delete
the existing network. Keep 2000–2024 as the ingestion target, screen 1990–2024
for future readiness, and keep distinct long-record core, modern regional
support, and daily climate-support roles. This resolves the history/geography
tradeoff without pretending every station must serve all roles.

Compare possible regional substitutions such as CON for MHT and MPV for LEB/DDH,
but assess loss of geography and observational independence. PSM is worth
testing as a historical seacoast option. BDR remains valuable for daily context
and newer coastal hourly data, not an automatic full-period hourly upgrade.

## Sources

- [NOAA GHCNh product, source harmonization and QC](https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly)
- [GHCNh v1.1.0 documentation and source-dependent quality codes](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh_DOCUMENTATION.pdf)
- [Hourly inventory archives](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/index.html#hourly/inventory/)
- [Hourly station-year files](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/index.html#hourly/access/by-year/)
- [NOAA daily files](https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/)

Detailed scratch results reside in /tmp/metpipe_broad_daily_results.json,
/tmp/metpipe_hourly_inventory_results.json, and /tmp/metpipe_early_hourly_results.json.
The retained conclusions and audit methods are documented here.

