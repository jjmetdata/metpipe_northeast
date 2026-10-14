# All 94 locations: three-window historical audit

Audit date: 2026-10-12.

## Scope and outcome

All **94 distinct locations** in the registry were assessed for **2005–2024,
1995–2024 and 1990–2024**, keeping hourly and daily records separate.

- **70 locations** have a matched primary-hourly inventory entry somewhere
  in 1990–2024. Actual available station-year Parquet files were read and screened.
- **24 locations** have no matched primary-hourly inventory in this window;
  this is not evidence of bad measurements or proof that no alternate archive exists.
- **92 locations** have a readable primary GHCN-Daily file. The other
  primary daily identifiers were unavailable in the checked archive.
- **0 unresolved download/parse errors** remain. Confirmed unavailable
  files and no-inventory years are recorded separately and remain in denominators.
- The 20 existing database stations, station map and ingested records are unchanged.

These counts refer to the selected 94-location search pool, not an exhaustive
search of every station in the Northeast. Observatories/COOP sites can be daily
climate support without operating a continuous hourly schedule.

| Window | Locations passing every year: hourly core | Locations passing every year: daily core |
| --- | ---: | ---: |
| 2005–2024 | 41 | 53 |
| 1995–2024 | 2 | 31 |
| 1990–2024 | 2 | 31 |

## Definition and limits

Hourly core = temperature, dew point and wind speed. Daily core = TMAX, TMIN
and PRCP. Passing means each field individually has >=95% accepted values in
every year, using all expected calendar hours/days. This is a conservative
project screen, not a universal quality certification or normals eligibility rule.

Table percentages are the lowest whole-window coverage among the three core
elements, NOT joint simultaneous coverage. Missing hours and missing files remain
in the expected-hour denominator. Expected hours are 175,320, 262,992 and 306,816
for the three windows respectively. A high total can conceal a weak year/month.

The hourly screen selects FM15, FM12, SAO, SYSA, SYMT, SYAE, SYAU, SSA and SAAU.
It excludes specials, NSRDB, unknown/blank QC and calculated flags. Sources
220/221/222/223/347/348 require quality code 1; sources
313/314/315/322/335/343/344/346 require 1 or 5. Codes mean different things across
sources: code 5 is removed for source 223. Unmapped flags do NOT prove bad data.

Daily values count when they are not -9999 and the GHCN-Daily quality flag is blank;
zero and trace values count as present. Observation-day definitions, accumulation
flags, station moves, sensors and homogenization still need separate review.

Wind direction, pressure and precipitation structured presence/QC counts are in
the JSON, but are not hourly pass/fail gates. Blank precipitation is not automatically
zero or missing; gust reporting is conditional. Clouds and radar/live-feed suitability
were not fully audited. This is not an all-variable forecast-readiness certification.

One fixed primary source is used per role/location; sources were not spliced to
maximize coverage. Blue Hill's COOP and LCD IDs are one location with separate
daily series. St. Johnsbury's COOP daily and co-located ASOS hourly IDs are explicitly
separate series; this grouping does not certify a homogeneous station history.
Alternative source/ID investigation remains warranted where primary archives have gaps.

## Original 20: hourly comparison

Each cell = lowest total core coverage; passing-year count.

| Location | 2005–2024 | 1995–2024 | 1990–2024 |
| --- | --- | --- | --- |
| ALB — ALBANY INTL AP (NY) | 99.96%; 20/20 years >=95% | 98.64%; 28/30 years >=95% | 98.71%; 33/35 years >=95% |
| AUG — AUGUSTA STATE AP (ME) | 99.70%; 20/20 years >=95% | 98.28%; 26/30 years >=95% | 98.11%; 31/35 years >=95% |
| BAF — WESTFIELD BARNES MUNI AP (MA) | 99.31%; 19/20 years >=95% | 92.72%; 19/30 years >=95% | 87.29%; 19/35 years >=95% |
| BDL — HARTFORD-BRADLEY INTL AP (CT) | 99.93%; 20/20 years >=95% | 97.39%; 26/30 years >=95% | 97.75%; 31/35 years >=95% |
| BOS — BOSTON (MA) | 99.96%; 20/20 years >=95% | 99.66%; 30/30 years >=95% | 99.71%; 35/35 years >=95% |
| BTV — BURLINGTON INTL AP (VT) | 99.89%; 20/20 years >=95% | 97.28%; 26/30 years >=95% | 97.67%; 31/35 years >=95% |
| DDH — BENNINGTON MORSE STATE AP (VT) | 98.85%; 19/20 years >=95% | 75.61%; 20/30 years >=95% | 64.81%; 20/35 years >=95% |
| EWB — NEW BEDFORD MUNI AP (MA) | 99.05%; 19/20 years >=95% | 94.48%; 22/30 years >=95% | 88.21%; 22/35 years >=95% |
| HVN — NEW HAVEN TWEED AP (CT) | 99.31%; 19/20 years >=95% | 76.05%; 21/30 years >=95% | 65.20%; 21/35 years >=95% |
| HYA — HYANNIS BARNSTABLE MUNI AP (MA) | 99.58%; 20/20 years >=95% | 95.91%; 26/30 years >=95% | 92.17%; 26/35 years >=95% |
| JFK — JFK INTL AP (NY) | 99.88%; 20/20 years >=95% | 97.78%; 26/30 years >=95% | 98.10%; 31/35 years >=95% |
| LEB — LEBANON MUNI AP (NH) | 99.66%; 20/20 years >=95% | 93.52%; 21/30 years >=95% | 92.28%; 21/35 years >=95% |
| MHT — MANCHESTER AP (NH) | 99.62%; 19/20 years >=95% | 96.55%; 22/30 years >=95% | 94.67%; 22/35 years >=95% |
| MVY — VINEYARD HAVEN MARTHAS VINEYAR (MA) | 98.65%; 19/20 years >=95% | 93.25%; 22/30 years >=95% | 84.73%; 22/35 years >=95% |
| ORH — WORCESTER (MA) | 99.47%; 20/20 years >=95% | 97.13%; 21/30 years >=95% | 97.08%; 25/35 years >=95% |
| PVC — PROVINCETOWN MUNI AP (MA) | 94.62%; 15/20 years >=95% | 91.94%; 16/30 years >=95% | 88.39%; 17/35 years >=95% |
| PVD — PROVIDENCE (RI) | 99.86%; 20/20 years >=95% | 97.59%; 26/30 years >=95% | 97.88%; 31/35 years >=95% |
| PWM — PORTLAND JETPORT (ME) | 99.82%; 20/20 years >=95% | 97.44%; 27/30 years >=95% | 97.80%; 32/35 years >=95% |
| PYM — PLYMOUTH MUNI AP (MA) | 99.42%; 20/20 years >=95% | 95.49%; 23/30 years >=95% | 81.85%; 23/35 years >=95% |
| UUU — NEWPORT STATE AP (RI) | 99.63%; 20/20 years >=95% | 83.38%; 22/30 years >=95% | 71.47%; 22/35 years >=95% |

## All 94: hourly comparison

No matched inventory / no selected routine core are archive or reporting-role
statuses, not a label that a station is intrinsically unreliable.

| Location | 2005–2024 | 1995–2024 | 1990–2024 |
| --- | --- | --- | --- |
| GROTON (CT) | No matched inventory | No matched inventory | No matched inventory |
| GON — GROTON NEW LONDON AP (CT) | 99.54%; 20/20 years >=95% | 91.92%; 23/30 years >=95% | 82.74%; 23/35 years >=95% |
| HARTFORD BRAINARD FLD (CT) | 99.65%; 20/20 years >=95% | 94.86%; 21/30 years >=95% | 89.48%; 21/35 years >=95% |
| BDL — HARTFORD-BRADLEY INTL AP (CT) | 99.93%; 20/20 years >=95% | 97.39%; 26/30 years >=95% | 97.75%; 31/35 years >=95% |
| BDR — IGOR I SIKORSKY MEM AP (CT) | 99.49%; 20/20 years >=95% | 96.43%; 24/30 years >=95% | 92.83%; 24/35 years >=95% |
| HVN — NEW HAVEN TWEED AP (CT) | 99.31%; 19/20 years >=95% | 76.05%; 21/30 years >=95% | 65.20%; 21/35 years >=95% |
| NORFOLK 2 SW (CT) | No selected routine core | No selected routine core | No selected routine core |
| NORWICH PUBLIC UTILITY PLT (CT) | No matched inventory | No matched inventory | No matched inventory |
| STORRS (CT) | No matched inventory | No matched inventory | No matched inventory |
| AMHERST (MA) | No matched inventory | No matched inventory | No matched inventory |
| ASHBURNHAM (MA) | No matched inventory | No matched inventory | No matched inventory |
| BEDFORD HANSCOM FLD (MA) | 99.50%; 20/20 years >=95% | 89.05%; 21/30 years >=95% | 85.61%; 21/35 years >=95% |
| BELCHERTOWN (MA) | No matched inventory | No matched inventory | No matched inventory |
| BLUE HILL LCD (MA) | 42.29%; 4/20 years >=95% | 48.37%; 8/30 years >=95% | 41.46%; 8/35 years >=95% |
| BOS — BOSTON (MA) | 99.96%; 20/20 years >=95% | 99.66%; 30/30 years >=95% | 99.71%; 35/35 years >=95% |
| CHATHAM (MA) | No matched inventory | No matched inventory | No matched inventory |
| E WAREHAM (MA) | No matched inventory | No matched inventory | No matched inventory |
| HINGHAM (MA) | No matched inventory | No matched inventory | No matched inventory |
| HYANNIS (MA) | No matched inventory | No matched inventory | No matched inventory |
| HYA — HYANNIS BARNSTABLE MUNI AP (MA) | 99.58%; 20/20 years >=95% | 95.91%; 26/30 years >=95% | 92.17%; 26/35 years >=95% |
| LAWRENCE (MA) | No matched inventory | No matched inventory | No matched inventory |
| MIDDLEBORO (MA) | No matched inventory | No matched inventory | No matched inventory |
| AQW — N ADAMS HARRIMAN AP (MA) | 98.74%; 19/20 years >=95% | 89.16%; 20/30 years >=95% | 76.43%; 20/35 years >=95% |
| ACK — NANTUCKET MEM AP (MA) | 98.85%; 18/20 years >=95% | 94.58%; 22/30 years >=95% | 90.12%; 22/35 years >=95% |
| EWB — NEW BEDFORD MUNI AP (MA) | 99.05%; 19/20 years >=95% | 94.48%; 22/30 years >=95% | 88.21%; 22/35 years >=95% |
| PSF — PITTSFIELD MUNI AP (MA) | 99.36%; 20/20 years >=95% | 75.12%; 20/30 years >=95% | 64.39%; 20/35 years >=95% |
| PYM — PLYMOUTH MUNI AP (MA) | 99.42%; 20/20 years >=95% | 95.49%; 23/30 years >=95% | 81.85%; 23/35 years >=95% |
| PVC — PROVINCETOWN MUNI AP (MA) | 94.62%; 15/20 years >=95% | 91.94%; 16/30 years >=95% | 88.39%; 17/35 years >=95% |
| MVY — VINEYARD HAVEN MARTHAS VINEYAR (MA) | 98.65%; 19/20 years >=95% | 93.25%; 22/30 years >=95% | 84.73%; 22/35 years >=95% |
| WALPOLE 2 (MA) | No matched inventory | No matched inventory | No matched inventory |
| BAF — WESTFIELD BARNES MUNI AP (MA) | 99.31%; 19/20 years >=95% | 92.72%; 19/30 years >=95% | 87.29%; 19/35 years >=95% |
| ORH — WORCESTER (MA) | 99.47%; 20/20 years >=95% | 97.13%; 21/30 years >=95% | 97.08%; 25/35 years >=95% |
| AUG — AUGUSTA STATE AP (ME) | 99.70%; 20/20 years >=95% | 98.28%; 26/30 years >=95% | 98.11%; 31/35 years >=95% |
| BANGOR INTL AP (ME) | 99.93%; 20/20 years >=95% | 96.63%; 26/30 years >=95% | 97.11%; 31/35 years >=95% |
| CARIBOU WFO (ME) | 99.79%; 20/20 years >=95% | 95.25%; 24/30 years >=95% | 91.58%; 24/35 years >=95% |
| CORINNA (ME) | No matched inventory | No matched inventory | No matched inventory |
| FARMINGTON (ME) | No matched inventory | No matched inventory | No matched inventory |
| GARDINER (ME) | No matched inventory | No matched inventory | No matched inventory |
| HOULTON AP (ME) | 99.48%; 20/20 years >=95% | 97.75%; 24/30 years >=95% | 97.39%; 28/35 years >=95% |
| MILLINOCKET MUNI AP (ME) | 88.08%; 16/20 years >=95% | 87.19%; 18/30 years >=95% | 75.29%; 18/35 years >=95% |
| PWM — PORTLAND JETPORT (ME) | 99.82%; 20/20 years >=95% | 97.44%; 27/30 years >=95% | 97.80%; 32/35 years >=95% |
| PRESQUE ISLE MUNI AP (ME) | 97.69%; 16/20 years >=95% | 94.68%; 20/30 years >=95% | 89.98%; 22/35 years >=95% |
| CON — CONCORD ASOS (NH) | 99.08%; 19/20 years >=95% | 97.70%; 24/30 years >=95% | 98.03%; 29/35 years >=95% |
| DURHAM (NH) | No selected routine core | No selected routine core | No selected routine core |
| HANOVER (NH) | No selected routine core | No selected routine core | No selected routine core |
| KEENE (NH) | No matched inventory | No matched inventory | No matched inventory |
| EEN — KEENE DILLNT-HOPKNS AP (NH) | 94.75%; 13/20 years >=95% | 92.84%; 14/30 years >=95% | 88.56%; 16/35 years >=95% |
| LEB — LEBANON MUNI AP (NH) | 99.66%; 20/20 years >=95% | 93.52%; 21/30 years >=95% | 92.28%; 21/35 years >=95% |
| MHT — MANCHESTER AP (NH) | 99.62%; 19/20 years >=95% | 96.55%; 22/30 years >=95% | 94.67%; 22/35 years >=95% |
| MT WASHINGTON (NH) | 70.01%; 0/20 years >=95% | 72.10%; 0/30 years >=95% | 69.34%; 0/35 years >=95% |
| PINKHAM NOTCH (NH) | No selected routine core | No selected routine core | No selected routine core |
| PSM — PORTSMOUTH PEASE AFB (NH) | 99.62%; 20/20 years >=95% | 98.31%; 28/30 years >=95% | 98.48%; 33/35 years >=95% |
| ATLANTIC CITY INTL AP (NJ) | 99.04%; 20/20 years >=95% | 96.70%; 25/30 years >=95% | 97.17%; 30/35 years >=95% |
| ATLANTIC CITY MARINA (NJ) | 25.38%; 0/20 years >=95% | 16.92%; 0/30 years >=95% | 14.50%; 0/35 years >=95% |
| MILLVILLE MUNI AP (NJ) | 98.90%; 20/20 years >=95% | 97.83%; 26/30 years >=95% | 97.70%; 31/35 years >=95% |
| NEWARK LIBERTY INTL AP (NJ) | 99.92%; 20/20 years >=95% | 98.36%; 27/30 years >=95% | 98.59%; 32/35 years >=95% |
| TETERBORO AP (NJ) | 99.38%; 19/20 years >=95% | 97.55%; 21/30 years >=95% | 97.19%; 23/35 years >=95% |
| TRENTON-MERCER AP (NJ) | 99.06%; 19/20 years >=95% | 92.11%; 22/30 years >=95% | 88.84%; 22/35 years >=95% |
| ALB — ALBANY INTL AP (NY) | 99.96%; 20/20 years >=95% | 98.64%; 28/30 years >=95% | 98.71%; 33/35 years >=95% |
| BINGHAMTON (NY) | 99.42%; 20/20 years >=95% | 99.39%; 30/30 years >=95% | 99.48%; 35/35 years >=95% |
| BRIDGEHAMPTON (NY) | No matched inventory | No matched inventory | No matched inventory |
| BUFFALO (NY) | 99.69%; 20/20 years >=95% | 97.20%; 26/30 years >=95% | 97.60%; 31/35 years >=95% |
| CANTON 4 SE (NY) | No selected routine core | No selected routine core | No selected routine core |
| DANSVILLE MUNI AP (NY) | 99.01%; 20/20 years >=95% | 75.79%; 21/30 years >=95% | 64.97%; 21/35 years >=95% |
| DUNKIRK CHAUTAUQUA CO AP (NY) | 99.24%; 20/20 years >=95% | 83.99%; 23/30 years >=95% | 71.99%; 23/35 years >=95% |
| ELMIRA CORNING RGNL AP (NY) | 99.34%; 20/20 years >=95% | 96.89%; 24/30 years >=95% | 96.76%; 28/35 years >=95% |
| GLENS FALLS AP (NY) | 99.20%; 20/20 years >=95% | 97.33%; 23/30 years >=95% | 96.98%; 26/35 years >=95% |
| ISLIP-LI MACARTHUR AP (NY) | 99.92%; 20/20 years >=95% | 99.23%; 29/30 years >=95% | 99.33%; 34/35 years >=95% |
| JFK — JFK INTL AP (NY) | 99.88%; 20/20 years >=95% | 97.78%; 26/30 years >=95% | 98.10%; 31/35 years >=95% |
| LAGUARDIA AP (NY) | 99.94%; 20/20 years >=95% | 97.89%; 26/30 years >=95% | 98.19%; 31/35 years >=95% |
| MASSENA INTL AP (NY) | 99.14%; 19/20 years >=95% | 98.34%; 26/30 years >=95% | 98.58%; 31/35 years >=95% |
| MOHONK LAKE (NY) | No selected routine core | No selected routine core | No selected routine core |
| NIAGARA FALLS INTL AP (NY) | 96.98%; 17/20 years >=95% | 94.24%; 20/30 years >=95% | 94.86%; 24/35 years >=95% |
| NY CITY CNTRL PARK (NY) | 92.35%; 7/20 years >=95% | 77.72%; 11/30 years >=95% | 66.62%; 11/35 years >=95% |
| PLATTSBURGH INTL AP (NY) | No matched inventory | No matched inventory | No matched inventory |
| POUGHKEEPSIE AP (NY) | 99.48%; 20/20 years >=95% | 96.04%; 21/30 years >=95% | 96.05%; 24/35 years >=95% |
| ROCHESTER GTR INTL (NY) | 99.95%; 20/20 years >=95% | 98.37%; 27/30 years >=95% | 98.60%; 32/35 years >=95% |
| SARATOGA SPRINGS 4 SW (NY) | No matched inventory | No matched inventory | No matched inventory |
| SYRACUSE HANCOCK INTL AP (NY) | 99.92%; 20/20 years >=95% | 97.35%; 26/30 years >=95% | 97.72%; 31/35 years >=95% |
| WATERTOWN AP (NY) | 99.61%; 20/20 years >=95% | 98.25%; 24/30 years >=95% | 97.94%; 29/35 years >=95% |
| WESTCHESTER CO AP (NY) | 99.50%; 20/20 years >=95% | 97.64%; 23/30 years >=95% | 97.22%; 26/35 years >=95% |
| WESTHAMPTON GABRESKI AP (NY) | 98.78%; 20/20 years >=95% | 88.61%; 21/30 years >=95% | 84.30%; 21/35 years >=95% |
| BLOCK ISLAND STATE AP (RI) | 90.01%; 8/20 years >=95% | 89.55%; 9/30 years >=95% | 87.91%; 9/35 years >=95% |
| KINGSTON (RI) | No matched inventory | No matched inventory | No matched inventory |
| N FOSTER 1 E (RI) | No matched inventory | No matched inventory | No matched inventory |
| UUU — NEWPORT STATE AP (RI) | 99.63%; 20/20 years >=95% | 83.38%; 22/30 years >=95% | 71.47%; 22/35 years >=95% |
| PVD — PROVIDENCE (RI) | 99.86%; 20/20 years >=95% | 97.59%; 26/30 years >=95% | 97.88%; 31/35 years >=95% |
| DDH — BENNINGTON MORSE STATE AP (VT) | 98.85%; 19/20 years >=95% | 75.61%; 20/30 years >=95% | 64.81%; 20/35 years >=95% |
| BTV — BURLINGTON INTL AP (VT) | 99.89%; 20/20 years >=95% | 97.28%; 26/30 years >=95% | 97.67%; 31/35 years >=95% |
| CORNWALL (VT) | No matched inventory | No matched inventory | No matched inventory |
| MPV — MONTPELIER AP (VT) | 99.42%; 20/20 years >=95% | 98.30%; 27/30 years >=95% | 98.00%; 31/35 years >=95% |
| S LINCOLN (VT) | No matched inventory | No matched inventory | No matched inventory |
| SAINT JOHNSBURY (VT) | 4.38%; 0/20 years >=95% | 11.86%; 0/30 years >=95% | 14.74%; 0/35 years >=95% |
| VSF — SPRINGFIELD HARTNESS STATE AP (VT) | 99.40%; 20/20 years >=95% | 92.52%; 21/30 years >=95% | 79.31%; 21/35 years >=95% |

## All 94: daily comparison

Each cell = lowest total accepted-day coverage; years where all three daily
elements meet 95%. Do not substitute these values for hourly qualifications.

| Location | 2005–2024 | 1995–2024 | 1990–2024 |
| --- | --- | --- | --- |
| GROTON (CT) | 67.83%; 3/20 years >=95% | 77.66%; 11/30 years >=95% | 80.55%; 15/35 years >=95% |
| GON — GROTON NEW LONDON AP (CT) | 99.03%; 20/20 years >=95% | 82.76%; 25/30 years >=95% | 70.94%; 25/35 years >=95% |
| HARTFORD BRAINARD FLD (CT) | 99.58%; 20/20 years >=95% | 95.87%; 25/30 years >=95% | 96.05%; 29/35 years >=95% |
| BDL — HARTFORD-BRADLEY INTL AP (CT) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| BDR — IGOR I SIKORSKY MEM AP (CT) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| HVN — NEW HAVEN TWEED AP (CT) | 99.47%; 20/20 years >=95% | 76.85%; 23/30 years >=95% | 65.87%; 23/35 years >=95% |
| NORFOLK 2 SW (CT) | 99.92%; 20/20 years >=95% | 96.63%; 25/30 years >=95% | 96.91%; 30/35 years >=95% |
| NORWICH PUBLIC UTILITY PLT (CT) | 91.05%; 14/20 years >=95% | 93.77%; 24/30 years >=95% | 91.26%; 27/35 years >=95% |
| STORRS (CT) | 98.52%; 17/20 years >=95% | 89.20%; 17/30 years >=95% | 89.49%; 18/35 years >=95% |
| AMHERST (MA) | 99.00%; 19/20 years >=95% | 98.48%; 29/30 years >=95% | 98.19%; 33/35 years >=95% |
| ASHBURNHAM (MA) | 85.00%; 17/20 years >=95% | 56.66%; 17/30 years >=95% | 48.57%; 17/35 years >=95% |
| BEDFORD HANSCOM FLD (MA) | 98.82%; 19/20 years >=95% | 86.99%; 25/30 years >=95% | 74.56%; 25/35 years >=95% |
| BELCHERTOWN (MA) | 81.94%; 16/20 years >=95% | 54.63%; 16/30 years >=95% | 46.82%; 16/35 years >=95% |
| BLUE HILL LCD (MA) | 99.97%; 20/20 years >=95% | 99.84%; 30/30 years >=95% | 99.87%; 35/35 years >=95% |
| BOS — BOSTON (MA) | 100.00%; 20/20 years >=95% | 99.98%; 30/30 years >=95% | 99.98%; 35/35 years >=95% |
| CHATHAM (MA) | 80.00%; 15/20 years >=95% | 82.70%; 19/30 years >=95% | 84.12%; 22/35 years >=95% |
| E WAREHAM (MA) | 81.33%; 16/20 years >=95% | 85.83%; 23/30 years >=95% | 87.55%; 27/35 years >=95% |
| HINGHAM (MA) | 99.25%; 18/20 years >=95% | 99.50%; 28/30 years >=95% | 99.33%; 32/35 years >=95% |
| HYANNIS (MA) | 91.36%; 16/20 years >=95% | 88.72%; 19/30 years >=95% | 89.40%; 22/35 years >=95% |
| HYA — HYANNIS BARNSTABLE MUNI AP (MA) | 99.19%; 19/20 years >=95% | 88.60%; 25/30 years >=95% | 75.95%; 25/35 years >=95% |
| LAWRENCE (MA) | 95.47%; 13/20 years >=95% | 94.56%; 15/30 years >=95% | 94.26%; 17/35 years >=95% |
| MIDDLEBORO (MA) | 71.95%; 8/20 years >=95% | 47.97%; 8/30 years >=95% | 41.11%; 8/35 years >=95% |
| AQW — N ADAMS HARRIMAN AP (MA) | 98.85%; 20/20 years >=95% | 88.89%; 26/30 years >=95% | 76.19%; 26/35 years >=95% |
| ACK — NANTUCKET MEM AP (MA) | 98.11%; 17/20 years >=95% | 87.88%; 22/30 years >=95% | 75.33%; 22/35 years >=95% |
| EWB — NEW BEDFORD MUNI AP (MA) | 99.42%; 20/20 years >=95% | 88.99%; 25/30 years >=95% | 76.28%; 25/35 years >=95% |
| PSF — PITTSFIELD MUNI AP (MA) | 99.60%; 20/20 years >=95% | 86.09%; 25/30 years >=95% | 73.80%; 25/35 years >=95% |
| PYM — PLYMOUTH MUNI AP (MA) | 99.44%; 20/20 years >=95% | 88.89%; 26/30 years >=95% | 76.19%; 26/35 years >=95% |
| PVC — PROVINCETOWN MUNI AP (MA) | No readable daily file | No readable daily file | No readable daily file |
| MVY — VINEYARD HAVEN MARTHAS VINEYAR (MA) | 97.70%; 15/20 years >=95% | 87.56%; 21/30 years >=95% | 75.06%; 21/35 years >=95% |
| WALPOLE 2 (MA) | 99.84%; 20/20 years >=95% | 99.61%; 29/30 years >=95% | 99.66%; 34/35 years >=95% |
| BAF — WESTFIELD BARNES MUNI AP (MA) | 99.62%; 20/20 years >=95% | 87.64%; 26/30 years >=95% | 75.12%; 26/35 years >=95% |
| ORH — WORCESTER (MA) | 99.94%; 20/20 years >=95% | 99.47%; 30/30 years >=95% | 99.55%; 35/35 years >=95% |
| AUG — AUGUSTA STATE AP (ME) | 99.89%; 20/20 years >=95% | 99.92%; 30/30 years >=95% | 99.93%; 35/35 years >=95% |
| BANGOR INTL AP (ME) | 99.99%; 20/20 years >=95% | 99.81%; 30/30 years >=95% | 99.84%; 35/35 years >=95% |
| CARIBOU WFO (ME) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| CORINNA (ME) | 97.14%; 17/20 years >=95% | 97.21%; 27/30 years >=95% | 97.22%; 32/35 years >=95% |
| FARMINGTON (ME) | 96.34%; 18/20 years >=95% | 97.47%; 28/30 years >=95% | 97.75%; 33/35 years >=95% |
| GARDINER (ME) | 98.95%; 18/20 years >=95% | 98.89%; 28/30 years >=95% | 98.91%; 33/35 years >=95% |
| HOULTON AP (ME) | 99.90%; 20/20 years >=95% | 99.92%; 30/30 years >=95% | 99.93%; 35/35 years >=95% |
| MILLINOCKET MUNI AP (ME) | 98.88%; 19/20 years >=95% | 88.25%; 25/30 years >=95% | 75.65%; 25/35 years >=95% |
| PWM — PORTLAND JETPORT (ME) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| PRESQUE ISLE MUNI AP (ME) | 1.79%; 0/20 years >=95% | 1.20%; 0/30 years >=95% | 1.02%; 0/35 years >=95% |
| CON — CONCORD ASOS (NH) | 99.97%; 20/20 years >=95% | 99.97%; 30/30 years >=95% | 99.98%; 35/35 years >=95% |
| DURHAM (NH) | 93.33%; 12/20 years >=95% | 94.32%; 19/30 years >=95% | 95.09%; 24/35 years >=95% |
| HANOVER (NH) | 85.22%; 5/20 years >=95% | 89.93%; 10/30 years >=95% | 91.30%; 15/35 years >=95% |
| KEENE (NH) | 98.73%; 20/20 years >=95% | 94.96%; 27/30 years >=95% | 95.67%; 31/35 years >=95% |
| EEN — KEENE DILLNT-HOPKNS AP (NH) | No readable daily file | No readable daily file | No readable daily file |
| LEB — LEBANON MUNI AP (NH) | 99.62%; 20/20 years >=95% | 88.47%; 26/30 years >=95% | 75.84%; 26/35 years >=95% |
| MHT — MANCHESTER AP (NH) | 99.63%; 20/20 years >=95% | 88.93%; 26/30 years >=95% | 76.23%; 26/35 years >=95% |
| MT WASHINGTON (NH) | 99.55%; 20/20 years >=95% | 99.64%; 30/30 years >=95% | 99.68%; 35/35 years >=95% |
| PINKHAM NOTCH (NH) | 97.51%; 17/20 years >=95% | 97.61%; 25/30 years >=95% | 97.45%; 29/35 years >=95% |
| PSM — PORTSMOUTH PEASE AFB (NH) | 0.00%; 0/20 years >=95% | 0.00%; 0/30 years >=95% | 0.00%; 0/35 years >=95% |
| ATLANTIC CITY INTL AP (NJ) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| ATLANTIC CITY MARINA (NJ) | 99.21%; 20/20 years >=95% | 99.39%; 30/30 years >=95% | 99.38%; 35/35 years >=95% |
| MILLVILLE MUNI AP (NJ) | 98.91%; 18/20 years >=95% | 99.26%; 28/30 years >=95% | 99.37%; 33/35 years >=95% |
| NEWARK LIBERTY INTL AP (NJ) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| TETERBORO AP (NJ) | 99.56%; 20/20 years >=95% | 99.37%; 30/30 years >=95% | 99.46%; 35/35 years >=95% |
| TRENTON-MERCER AP (NJ) | 100.00%; 20/20 years >=95% | 89.37%; 26/30 years >=95% | 76.60%; 26/35 years >=95% |
| ALB — ALBANY INTL AP (NY) | 99.99%; 20/20 years >=95% | 99.99%; 30/30 years >=95% | 99.99%; 35/35 years >=95% |
| BINGHAMTON (NY) | 99.97%; 20/20 years >=95% | 99.98%; 30/30 years >=95% | 99.98%; 35/35 years >=95% |
| BRIDGEHAMPTON (NY) | 88.82%; 13/20 years >=95% | 92.51%; 23/30 years >=95% | 93.38%; 26/35 years >=95% |
| BUFFALO (NY) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| CANTON 4 SE (NY) | 67.46%; 4/20 years >=95% | 78.00%; 13/30 years >=95% | 81.12%; 18/35 years >=95% |
| DANSVILLE MUNI AP (NY) | 99.14%; 20/20 years >=95% | 82.04%; 24/30 years >=95% | 70.32%; 24/35 years >=95% |
| DUNKIRK CHAUTAUQUA CO AP (NY) | 97.82%; 18/20 years >=95% | 87.71%; 24/30 years >=95% | 75.18%; 24/35 years >=95% |
| ELMIRA CORNING RGNL AP (NY) | 99.81%; 20/20 years >=95% | 88.98%; 26/30 years >=95% | 76.27%; 26/35 years >=95% |
| GLENS FALLS AP (NY) | 99.77%; 20/20 years >=95% | 99.82%; 30/30 years >=95% | 99.83%; 35/35 years >=95% |
| ISLIP-LI MACARTHUR AP (NY) | 99.99%; 20/20 years >=95% | 99.98%; 30/30 years >=95% | 99.98%; 35/35 years >=95% |
| JFK — JFK INTL AP (NY) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| LAGUARDIA AP (NY) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| MASSENA INTL AP (NY) | 99.33%; 19/20 years >=95% | 99.29%; 29/30 years >=95% | 99.39%; 34/35 years >=95% |
| MOHONK LAKE (NY) | 84.56%; 16/20 years >=95% | 89.71%; 26/30 years >=95% | 91.18%; 31/35 years >=95% |
| NIAGARA FALLS INTL AP (NY) | 99.23%; 19/20 years >=95% | 77.24%; 22/30 years >=95% | 66.21%; 22/35 years >=95% |
| NY CITY CNTRL PARK (NY) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| PLATTSBURGH INTL AP (NY) | 5.42%; 1/20 years >=95% | 3.61%; 1/30 years >=95% | 3.10%; 1/35 years >=95% |
| POUGHKEEPSIE AP (NY) | 99.75%; 20/20 years >=95% | 80.87%; 24/30 years >=95% | 79.51%; 27/35 years >=95% |
| ROCHESTER GTR INTL (NY) | 100.00%; 20/20 years >=95% | 100.00%; 30/30 years >=95% | 100.00%; 35/35 years >=95% |
| SARATOGA SPRINGS 4 SW (NY) | 94.29%; 15/20 years >=95% | 95.81%; 24/30 years >=95% | 96.36%; 29/35 years >=95% |
| SYRACUSE HANCOCK INTL AP (NY) | 99.89%; 20/20 years >=95% | 99.93%; 30/30 years >=95% | 99.92%; 35/35 years >=95% |
| WATERTOWN AP (NY) | 99.81%; 20/20 years >=95% | 99.87%; 30/30 years >=95% | 99.87%; 35/35 years >=95% |
| WESTCHESTER CO AP (NY) | 99.10%; 20/20 years >=95% | 95.35%; 23/30 years >=95% | 95.49%; 27/35 years >=95% |
| WESTHAMPTON GABRESKI AP (NY) | 96.36%; 14/20 years >=95% | 85.12%; 19/30 years >=95% | 72.97%; 19/35 years >=95% |
| BLOCK ISLAND STATE AP (RI) | 0.57%; 0/20 years >=95% | 2.57%; 0/30 years >=95% | 15.89%; 4/35 years >=95% |
| KINGSTON (RI) | 99.92%; 20/20 years >=95% | 99.62%; 29/30 years >=95% | 99.65%; 34/35 years >=95% |
| N FOSTER 1 E (RI) | 99.93%; 20/20 years >=95% | 99.92%; 30/30 years >=95% | 99.91%; 35/35 years >=95% |
| UUU — NEWPORT STATE AP (RI) | 99.73%; 20/20 years >=95% | 88.90%; 26/30 years >=95% | 76.20%; 26/35 years >=95% |
| PVD — PROVIDENCE (RI) | 100.00%; 20/20 years >=95% | 99.97%; 30/30 years >=95% | 99.98%; 35/35 years >=95% |
| DDH — BENNINGTON MORSE STATE AP (VT) | 99.21%; 18/20 years >=95% | 86.19%; 24/30 years >=95% | 73.88%; 24/35 years >=95% |
| BTV — BURLINGTON INTL AP (VT) | 99.99%; 20/20 years >=95% | 99.99%; 30/30 years >=95% | 99.99%; 35/35 years >=95% |
| CORNWALL (VT) | 94.73%; 12/20 years >=95% | 85.19%; 17/30 years >=95% | 86.25%; 18/35 years >=95% |
| MPV — MONTPELIER AP (VT) | 99.85%; 20/20 years >=95% | 93.96%; 27/30 years >=95% | 94.82%; 32/35 years >=95% |
| S LINCOLN (VT) | 83.92%; 3/20 years >=95% | 85.22%; 4/30 years >=95% | 87.34%; 8/35 years >=95% |
| SAINT JOHNSBURY (VT) | 99.88%; 20/20 years >=95% | 99.77%; 30/30 years >=95% | 99.74%; 35/35 years >=95% |
| VSF — SPRINGFIELD HARTNESS STATE AP (VT) | 99.55%; 20/20 years >=95% | 88.96%; 26/30 years >=95% | 76.25%; 26/35 years >=95% |

## Hourly elements, 2005–2024

| Location | Temperature | Dew point | Wind speed | Files read | Weakest core year in read files |
| --- | ---: | ---: | ---: | ---: | --- |
| GROTON (CT) | N/A | N/A | N/A | 0/20 | N/A |
| GON — GROTON NEW LONDON AP (CT) | 99.77% | 99.54% | 99.77% | 20/20 | 98.83% (2024) |
| HARTFORD BRAINARD FLD (CT) | 99.74% | 99.67% | 99.65% | 20/20 | 97.55% (2015) |
| BDL — HARTFORD-BRADLEY INTL AP (CT) | 99.94% | 99.93% | 99.96% | 20/20 | 99.76% (2011) |
| BDR — IGOR I SIKORSKY MEM AP (CT) | 99.56% | 99.52% | 99.49% | 20/20 | 97.76% (2021) |
| HVN — NEW HAVEN TWEED AP (CT) | 99.32% | 99.31% | 99.71% | 20/20 | 92.97% (2006) |
| NORFOLK 2 SW (CT) | 0.00% | 0.00% | 0.00% | 20/20 | 0.00% (2005) |
| NORWICH PUBLIC UTILITY PLT (CT) | N/A | N/A | N/A | 0/20 | N/A |
| STORRS (CT) | N/A | N/A | N/A | 0/20 | N/A |
| AMHERST (MA) | N/A | N/A | N/A | 0/20 | N/A |
| ASHBURNHAM (MA) | N/A | N/A | N/A | 0/20 | N/A |
| BEDFORD HANSCOM FLD (MA) | 99.75% | 99.55% | 99.50% | 20/20 | 97.62% (2016) |
| BELCHERTOWN (MA) | N/A | N/A | N/A | 0/20 | N/A |
| BLUE HILL LCD (MA) | 42.34% | 42.29% | 42.66% | 20/20 | 0.00% (2007) |
| BOS — BOSTON (MA) | 99.96% | 99.96% | 99.98% | 20/20 | 99.86% (2005) |
| CHATHAM (MA) | N/A | N/A | N/A | 0/20 | N/A |
| E WAREHAM (MA) | N/A | N/A | N/A | 0/20 | N/A |
| HINGHAM (MA) | N/A | N/A | N/A | 0/20 | N/A |
| HYANNIS (MA) | N/A | N/A | N/A | 0/20 | N/A |
| HYA — HYANNIS BARNSTABLE MUNI AP (MA) | 99.71% | 99.69% | 99.58% | 20/20 | 97.90% (2021) |
| LAWRENCE (MA) | N/A | N/A | N/A | 0/20 | N/A |
| MIDDLEBORO (MA) | N/A | N/A | N/A | 0/20 | N/A |
| AQW — N ADAMS HARRIMAN AP (MA) | 99.36% | 99.19% | 98.74% | 20/20 | 91.91% (2023) |
| ACK — NANTUCKET MEM AP (MA) | 99.12% | 99.08% | 98.85% | 20/20 | 86.00% (2024) |
| EWB — NEW BEDFORD MUNI AP (MA) | 99.25% | 99.05% | 99.67% | 20/20 | 92.63% (2006) |
| PSF — PITTSFIELD MUNI AP (MA) | 99.61% | 99.44% | 99.36% | 20/20 | 96.58% (2020) |
| PYM — PLYMOUTH MUNI AP (MA) | 99.55% | 99.47% | 99.42% | 20/20 | 98.04% (2019) |
| PVC — PROVINCETOWN MUNI AP (MA) | 95.17% | 94.62% | 94.86% | 20/20 | 59.82% (2006) |
| MVY — VINEYARD HAVEN MARTHAS VINEYAR (MA) | 98.71% | 98.65% | 99.40% | 20/20 | 90.02% (2018) |
| WALPOLE 2 (MA) | N/A | N/A | N/A | 0/20 | N/A |
| BAF — WESTFIELD BARNES MUNI AP (MA) | 99.33% | 99.31% | 99.65% | 20/20 | 92.70% (2006) |
| ORH — WORCESTER (MA) | 99.55% | 99.47% | 99.59% | 20/20 | 97.25% (2018) |
| AUG — AUGUSTA STATE AP (ME) | 99.77% | 99.75% | 99.70% | 20/20 | 98.76% (2024) |
| BANGOR INTL AP (ME) | 99.93% | 99.93% | 99.93% | 20/20 | 99.73% (2008) |
| CARIBOU WFO (ME) | 99.89% | 99.86% | 99.79% | 20/20 | 99.17% (2024) |
| CORINNA (ME) | N/A | N/A | N/A | 0/20 | N/A |
| FARMINGTON (ME) | N/A | N/A | N/A | 0/20 | N/A |
| GARDINER (ME) | N/A | N/A | N/A | 0/20 | N/A |
| HOULTON AP (ME) | 99.79% | 99.69% | 99.48% | 20/20 | 98.61% (2024) |
| MILLINOCKET MUNI AP (ME) | 88.59% | 88.50% | 88.08% | 20/20 | 0.93% (2009) |
| PWM — PORTLAND JETPORT (ME) | 99.90% | 99.85% | 99.82% | 20/20 | 99.32% (2024) |
| PRESQUE ISLE MUNI AP (ME) | 97.95% | 97.79% | 97.69% | 20/20 | 87.78% (2013) |
| CON — CONCORD ASOS (NH) | 99.46% | 99.44% | 99.08% | 20/20 | 94.42% (2019) |
| DURHAM (NH) | 0.00% | 0.00% | 0.00% | 20/20 | 0.00% (2005) |
| HANOVER (NH) | 0.00% | 0.00% | 0.00% | 20/20 | 0.00% (2005) |
| KEENE (NH) | N/A | N/A | N/A | 0/20 | N/A |
| EEN — KEENE DILLNT-HOPKNS AP (NH) | 94.89% | 94.75% | 97.26% | 20/20 | 81.06% (2011) |
| LEB — LEBANON MUNI AP (NH) | 99.76% | 99.75% | 99.66% | 20/20 | 98.82% (2021) |
| MHT — MANCHESTER AP (NH) | 99.63% | 99.62% | 99.93% | 20/20 | 94.61% (2006) |
| MT WASHINGTON (NH) | 71.06% | 70.01% | 90.03% | 20/20 | 51.02% (2018) |
| PINKHAM NOTCH (NH) | 0.00% | 0.00% | 0.00% | 20/20 | 0.00% (2005) |
| PSM — PORTSMOUTH PEASE AFB (NH) | 99.62% | 99.63% | 99.64% | 20/20 | 98.56% (2018) |
| ATLANTIC CITY INTL AP (NJ) | 99.21% | 99.09% | 99.04% | 20/20 | 96.35% (2023) |
| ATLANTIC CITY MARINA (NJ) | 25.38% | 25.38% | 29.37% | 8/20 | 21.18% (2024) |
| MILLVILLE MUNI AP (NJ) | 98.93% | 98.90% | 99.48% | 20/20 | 96.84% (2013) |
| NEWARK LIBERTY INTL AP (NJ) | 99.92% | 99.93% | 99.95% | 20/20 | 99.64% (2008) |
| TETERBORO AP (NJ) | 99.39% | 99.38% | 99.84% | 20/20 | 93.66% (2006) |
| TRENTON-MERCER AP (NJ) | 99.15% | 99.09% | 99.06% | 20/20 | 89.77% (2005) |
| ALB — ALBANY INTL AP (NY) | 99.96% | 99.96% | 99.97% | 20/20 | 99.90% (2005) |
| BINGHAMTON (NY) | 99.42% | 99.42% | 99.66% | 20/20 | 97.35% (2008) |
| BRIDGEHAMPTON (NY) | N/A | N/A | N/A | 0/20 | N/A |
| BUFFALO (NY) | 99.69% | 99.69% | 99.93% | 20/20 | 95.73% (2021) |
| CANTON 4 SE (NY) | 0.00% | 0.00% | 0.00% | 17/20 | 0.00% (2005) |
| DANSVILLE MUNI AP (NY) | 99.38% | 99.30% | 99.01% | 20/20 | 96.37% (2014) |
| DUNKIRK CHAUTAUQUA CO AP (NY) | 99.43% | 99.32% | 99.24% | 20/20 | 96.60% (2009) |
| ELMIRA CORNING RGNL AP (NY) | 99.40% | 99.34% | 99.60% | 20/20 | 97.67% (2011) |
| GLENS FALLS AP (NY) | 99.24% | 99.20% | 99.26% | 20/20 | 96.95% (2016) |
| ISLIP-LI MACARTHUR AP (NY) | 99.92% | 99.92% | 99.93% | 20/20 | 99.57% (2018) |
| JFK — JFK INTL AP (NY) | 99.88% | 99.88% | 99.98% | 20/20 | 98.61% (2020) |
| LAGUARDIA AP (NY) | 99.95% | 99.94% | 99.99% | 20/20 | 99.72% (2008) |
| MASSENA INTL AP (NY) | 99.24% | 99.14% | 99.23% | 20/20 | 92.37% (2008) |
| MOHONK LAKE (NY) | 0.00% | 0.00% | 0.00% | 13/20 | 0.00% (2012) |
| NIAGARA FALLS INTL AP (NY) | 97.11% | 96.98% | 97.41% | 20/20 | 67.83% (2011) |
| NY CITY CNTRL PARK (NY) | 99.39% | 99.33% | 92.35% | 20/20 | 71.95% (2018) |
| PLATTSBURGH INTL AP (NY) | N/A | N/A | N/A | 0/20 | N/A |
| POUGHKEEPSIE AP (NY) | 99.66% | 99.65% | 99.48% | 20/20 | 98.61% (2010) |
| ROCHESTER GTR INTL (NY) | 99.95% | 99.95% | 99.95% | 20/20 | 99.73% (2021) |
| SARATOGA SPRINGS 4 SW (NY) | N/A | N/A | N/A | 0/20 | N/A |
| SYRACUSE HANCOCK INTL AP (NY) | 99.97% | 99.96% | 99.92% | 20/20 | 99.72% (2009) |
| WATERTOWN AP (NY) | 99.75% | 99.74% | 99.61% | 20/20 | 98.77% (2021) |
| WESTCHESTER CO AP (NY) | 99.53% | 99.50% | 99.86% | 20/20 | 97.91% (2019) |
| WESTHAMPTON GABRESKI AP (NY) | 98.80% | 98.78% | 99.14% | 20/20 | 96.36% (2011) |
| BLOCK ISLAND STATE AP (RI) | 90.60% | 90.01% | 92.17% | 20/20 | 39.52% (2009) |
| KINGSTON (RI) | N/A | N/A | N/A | 0/20 | N/A |
| N FOSTER 1 E (RI) | N/A | N/A | N/A | 0/20 | N/A |
| UUU — NEWPORT STATE AP (RI) | 99.78% | 99.73% | 99.63% | 20/20 | 98.94% (2009) |
| PVD — PROVIDENCE (RI) | 99.90% | 99.86% | 99.90% | 20/20 | 99.43% (2017) |
| DDH — BENNINGTON MORSE STATE AP (VT) | 99.22% | 98.85% | 99.07% | 20/20 | 93.21% (2011) |
| BTV — BURLINGTON INTL AP (VT) | 99.94% | 99.90% | 99.89% | 20/20 | 99.20% (2021) |
| CORNWALL (VT) | N/A | N/A | N/A | 0/20 | N/A |
| MPV — MONTPELIER AP (VT) | 99.73% | 99.55% | 99.42% | 20/20 | 97.56% (2008) |
| S LINCOLN (VT) | N/A | N/A | N/A | 0/20 | N/A |
| SAINT JOHNSBURY (VT) | 97.97% | 97.60% | 4.38% | 20/20 | 0.00% (2006) |
| VSF — SPRINGFIELD HARTNESS STATE AP (VT) | 99.64% | 99.53% | 99.40% | 20/20 | 98.34% (2007) |

## Hourly elements, 1995–2024

| Location | Temperature | Dew point | Wind speed | Files read | Weakest core year in read files |
| --- | ---: | ---: | ---: | ---: | --- |
| GROTON (CT) | N/A | N/A | N/A | 0/30 | N/A |
| GON — GROTON NEW LONDON AP (CT) | 92.46% | 91.92% | 92.35% | 30/30 | 53.81% (1998) |
| HARTFORD BRAINARD FLD (CT) | 95.58% | 95.30% | 94.86% | 30/30 | 65.97% (1996) |
| BDL — HARTFORD-BRADLEY INTL AP (CT) | 97.43% | 97.39% | 97.56% | 30/30 | 81.37% (1999) |
| BDR — IGOR I SIKORSKY MEM AP (CT) | 96.48% | 96.43% | 96.50% | 30/30 | 70.89% (1995) |
| HVN — NEW HAVEN TWEED AP (CT) | 90.37% | 76.05% | 90.39% | 30/30 | 0.05% (1997) |
| NORFOLK 2 SW (CT) | 0.00% | 0.00% | 0.00% | 29/30 | 0.00% (1995) |
| NORWICH PUBLIC UTILITY PLT (CT) | N/A | N/A | N/A | 0/30 | N/A |
| STORRS (CT) | N/A | N/A | N/A | 0/30 | N/A |
| AMHERST (MA) | N/A | N/A | N/A | 0/30 | N/A |
| ASHBURNHAM (MA) | N/A | N/A | N/A | 0/30 | N/A |
| BEDFORD HANSCOM FLD (MA) | 89.72% | 89.46% | 89.05% | 29/30 | 22.66% (1997) |
| BELCHERTOWN (MA) | N/A | N/A | N/A | 0/30 | N/A |
| BLUE HILL LCD (MA) | 48.46% | 48.37% | 48.72% | 27/30 | 0.00% (2007) |
| BOS — BOSTON (MA) | 99.69% | 99.66% | 99.68% | 30/30 | 97.77% (2003) |
| CHATHAM (MA) | N/A | N/A | N/A | 0/30 | N/A |
| E WAREHAM (MA) | N/A | N/A | N/A | 0/30 | N/A |
| HINGHAM (MA) | N/A | N/A | N/A | 0/30 | N/A |
| HYANNIS (MA) | N/A | N/A | N/A | 0/30 | N/A |
| HYA — HYANNIS BARNSTABLE MUNI AP (MA) | 96.33% | 96.23% | 95.91% | 30/30 | 61.35% (1995) |
| LAWRENCE (MA) | N/A | N/A | N/A | 0/30 | N/A |
| MIDDLEBORO (MA) | N/A | N/A | N/A | 0/30 | N/A |
| AQW — N ADAMS HARRIMAN AP (MA) | 90.33% | 90.21% | 89.16% | 30/30 | 0.03% (1995) |
| ACK — NANTUCKET MEM AP (MA) | 94.78% | 94.58% | 94.61% | 30/30 | 56.77% (1995) |
| EWB — NEW BEDFORD MUNI AP (MA) | 94.69% | 94.48% | 94.78% | 30/30 | 47.20% (1995) |
| PSF — PITTSFIELD MUNI AP (MA) | 75.75% | 75.63% | 75.12% | 24/30 | 23.34% (2001) |
| PYM — PLYMOUTH MUNI AP (MA) | 96.03% | 95.98% | 95.49% | 30/30 | 56.12% (1995) |
| PVC — PROVINCETOWN MUNI AP (MA) | 92.75% | 91.94% | 92.18% | 30/30 | 59.82% (2006) |
| MVY — VINEYARD HAVEN MARTHAS VINEYAR (MA) | 93.73% | 93.25% | 94.10% | 30/30 | 45.24% (1995) |
| WALPOLE 2 (MA) | N/A | N/A | N/A | 0/30 | N/A |
| BAF — WESTFIELD BARNES MUNI AP (MA) | 93.60% | 93.42% | 92.72% | 30/30 | 57.66% (1997) |
| ORH — WORCESTER (MA) | 97.20% | 97.14% | 97.13% | 30/30 | 84.98% (2004) |
| AUG — AUGUSTA STATE AP (ME) | 98.47% | 98.41% | 98.28% | 30/30 | 91.45% (1995) |
| BANGOR INTL AP (ME) | 96.65% | 96.63% | 98.25% | 30/30 | 44.84% (1996) |
| CARIBOU WFO (ME) | 96.95% | 95.43% | 95.25% | 30/30 | 70.44% (1995) |
| CORINNA (ME) | N/A | N/A | N/A | 0/30 | N/A |
| FARMINGTON (ME) | N/A | N/A | N/A | 0/30 | N/A |
| GARDINER (ME) | N/A | N/A | N/A | 0/30 | N/A |
| HOULTON AP (ME) | 98.01% | 97.93% | 97.75% | 30/30 | 89.73% (1995) |
| MILLINOCKET MUNI AP (ME) | 88.08% | 87.98% | 87.19% | 30/30 | 0.93% (2009) |
| PWM — PORTLAND JETPORT (ME) | 97.55% | 97.46% | 97.44% | 30/30 | 78.68% (1999) |
| PRESQUE ISLE MUNI AP (ME) | 95.41% | 95.18% | 94.68% | 30/30 | 72.82% (1998) |
| CON — CONCORD ASOS (NH) | 98.08% | 98.01% | 97.70% | 30/30 | 86.36% (1999) |
| DURHAM (NH) | 0.00% | 0.00% | 0.00% | 30/30 | 0.00% (1995) |
| HANOVER (NH) | 0.00% | 0.00% | 0.00% | 30/30 | 0.00% (1995) |
| KEENE (NH) | N/A | N/A | N/A | 0/30 | N/A |
| EEN — KEENE DILLNT-HOPKNS AP (NH) | 93.00% | 92.84% | 93.63% | 30/30 | 63.28% (2001) |
| LEB — LEBANON MUNI AP (NH) | 94.77% | 94.56% | 93.52% | 30/30 | 60.15% (1997) |
| MHT — MANCHESTER AP (NH) | 97.03% | 96.88% | 96.55% | 30/30 | 78.12% (2004) |
| MT WASHINGTON (NH) | 72.94% | 72.10% | 85.60% | 30/30 | 51.02% (2018) |
| PINKHAM NOTCH (NH) | 0.00% | 0.00% | 0.00% | 30/30 | 0.00% (1995) |
| PSM — PORTSMOUTH PEASE AFB (NH) | 98.54% | 98.54% | 98.31% | 30/30 | 80.54% (1999) |
| ATLANTIC CITY INTL AP (NJ) | 96.81% | 96.70% | 96.72% | 30/30 | 81.43% (1998) |
| ATLANTIC CITY MARINA (NJ) | 16.92% | 16.92% | 19.58% | 8/30 | 21.18% (2024) |
| MILLVILLE MUNI AP (NJ) | 97.88% | 97.83% | 98.23% | 30/30 | 90.31% (1998) |
| NEWARK LIBERTY INTL AP (NJ) | 98.36% | 98.36% | 98.48% | 30/30 | 83.12% (1999) |
| TETERBORO AP (NJ) | 97.97% | 97.89% | 97.55% | 30/30 | 86.03% (2001) |
| TRENTON-MERCER AP (NJ) | 93.27% | 92.11% | 92.93% | 30/30 | 21.85% (1996) |
| ALB — ALBANY INTL AP (NY) | 98.65% | 98.64% | 98.69% | 30/30 | 82.77% (1999) |
| BINGHAMTON (NY) | 99.41% | 99.39% | 99.54% | 30/30 | 97.35% (2008) |
| BRIDGEHAMPTON (NY) | N/A | N/A | N/A | 0/30 | N/A |
| BUFFALO (NY) | 97.20% | 97.20% | 97.33% | 30/30 | 78.21% (1999) |
| CANTON 4 SE (NY) | 0.00% | 0.00% | 0.00% | 27/30 | 0.00% (1995) |
| DANSVILLE MUNI AP (NY) | 76.24% | 76.19% | 75.79% | 24/30 | 31.45% (2001) |
| DUNKIRK CHAUTAUQUA CO AP (NY) | 84.30% | 84.22% | 83.99% | 26/30 | 71.04% (2004) |
| ELMIRA CORNING RGNL AP (NY) | 97.77% | 97.72% | 96.89% | 30/30 | 77.73% (2001) |
| GLENS FALLS AP (NY) | 97.55% | 97.54% | 97.33% | 30/30 | 88.78% (1995) |
| ISLIP-LI MACARTHUR AP (NY) | 99.32% | 99.23% | 99.37% | 30/30 | 93.85% (1997) |
| JFK — JFK INTL AP (NY) | 97.78% | 97.78% | 97.83% | 30/30 | 82.77% (1998) |
| LAGUARDIA AP (NY) | 97.89% | 97.89% | 97.89% | 30/30 | 82.89% (1998) |
| MASSENA INTL AP (NY) | 98.45% | 98.34% | 98.45% | 30/30 | 92.37% (2008) |
| MOHONK LAKE (NY) | 0.00% | 0.00% | 0.00% | 13/30 | 0.00% (2012) |
| NIAGARA FALLS INTL AP (NY) | 94.33% | 94.24% | 96.11% | 30/30 | 49.13% (1996) |
| NY CITY CNTRL PARK (NY) | 96.03% | 95.93% | 77.72% | 30/30 | 0.00% (1995) |
| PLATTSBURGH INTL AP (NY) | N/A | N/A | N/A | 0/30 | N/A |
| POUGHKEEPSIE AP (NY) | 97.36% | 97.22% | 96.04% | 30/30 | 72.97% (2001) |
| ROCHESTER GTR INTL (NY) | 98.41% | 98.41% | 98.37% | 30/30 | 83.15% (1998) |
| SARATOGA SPRINGS 4 SW (NY) | N/A | N/A | N/A | 0/30 | N/A |
| SYRACUSE HANCOCK INTL AP (NY) | 97.44% | 97.44% | 97.35% | 30/30 | 78.06% (1999) |
| WATERTOWN AP (NY) | 98.45% | 98.42% | 98.25% | 30/30 | 91.78% (1995) |
| WESTCHESTER CO AP (NY) | 97.87% | 97.72% | 97.64% | 30/30 | 88.15% (2001) |
| WESTHAMPTON GABRESKI AP (NY) | 92.45% | 88.61% | 92.82% | 30/30 | 14.26% (1997) |
| BLOCK ISLAND STATE AP (RI) | 89.97% | 89.55% | 90.74% | 30/30 | 39.52% (2009) |
| KINGSTON (RI) | N/A | N/A | N/A | 0/30 | N/A |
| N FOSTER 1 E (RI) | N/A | N/A | N/A | 0/30 | N/A |
| UUU — NEWPORT STATE AP (RI) | 83.84% | 83.81% | 83.38% | 26/30 | 61.42% (1999) |
| PVD — PROVIDENCE (RI) | 97.62% | 97.59% | 97.60% | 30/30 | 82.72% (1998) |
| DDH — BENNINGTON MORSE STATE AP (VT) | 76.22% | 75.98% | 75.61% | 25/30 | 0.00% (1999) |
| BTV — BURLINGTON INTL AP (VT) | 97.40% | 97.37% | 97.28% | 30/30 | 77.97% (1999) |
| CORNWALL (VT) | N/A | N/A | N/A | 0/30 | N/A |
| MPV — MONTPELIER AP (VT) | 98.51% | 98.39% | 98.30% | 30/30 | 91.02% (1995) |
| S LINCOLN (VT) | N/A | N/A | N/A | 0/30 | N/A |
| SAINT JOHNSBURY (VT) | 75.06% | 74.68% | 11.86% | 30/30 | 0.00% (1998) |
| VSF — SPRINGFIELD HARTNESS STATE AP (VT) | 93.78% | 93.68% | 92.52% | 30/30 | 5.92% (1995) |

## Hourly elements, 1990–2024

| Location | Temperature | Dew point | Wind speed | Files read | Weakest core year in read files |
| --- | ---: | ---: | ---: | ---: | --- |
| GROTON (CT) | N/A | N/A | N/A | 0/35 | N/A |
| GON — GROTON NEW LONDON AP (CT) | 87.82% | 82.74% | 88.88% | 35/35 | 0.03% (1990) |
| HARTFORD BRAINARD FLD (CT) | 91.18% | 89.48% | 91.72% | 35/35 | 39.78% (1991) |
| BDL — HARTFORD-BRADLEY INTL AP (CT) | 97.79% | 97.75% | 97.90% | 35/35 | 81.37% (1999) |
| BDR — IGOR I SIKORSKY MEM AP (CT) | 92.90% | 92.83% | 92.92% | 35/35 | 70.89% (1995) |
| HVN — NEW HAVEN TWEED AP (CT) | 87.60% | 65.20% | 87.62% | 35/35 | 0.05% (1997) |
| NORFOLK 2 SW (CT) | 0.00% | 0.00% | 0.00% | 34/35 | 0.00% (1990) |
| NORWICH PUBLIC UTILITY PLT (CT) | N/A | N/A | N/A | 0/35 | N/A |
| STORRS (CT) | N/A | N/A | N/A | 0/35 | N/A |
| AMHERST (MA) | N/A | N/A | N/A | 0/35 | N/A |
| ASHBURNHAM (MA) | N/A | N/A | N/A | 0/35 | N/A |
| BEDFORD HANSCOM FLD (MA) | 86.31% | 85.61% | 86.00% | 34/35 | 22.66% (1997) |
| BELCHERTOWN (MA) | N/A | N/A | N/A | 0/35 | N/A |
| BLUE HILL LCD (MA) | 41.53% | 41.46% | 41.76% | 27/35 | 0.00% (2007) |
| BOS — BOSTON (MA) | 99.74% | 99.71% | 99.73% | 35/35 | 97.77% (2003) |
| CHATHAM (MA) | N/A | N/A | N/A | 0/35 | N/A |
| E WAREHAM (MA) | N/A | N/A | N/A | 0/35 | N/A |
| HINGHAM (MA) | N/A | N/A | N/A | 0/35 | N/A |
| HYANNIS (MA) | N/A | N/A | N/A | 0/35 | N/A |
| HYA — HYANNIS BARNSTABLE MUNI AP (MA) | 92.44% | 92.19% | 92.17% | 35/35 | 61.35% (1995) |
| LAWRENCE (MA) | N/A | N/A | N/A | 0/35 | N/A |
| MIDDLEBORO (MA) | N/A | N/A | N/A | 0/35 | N/A |
| AQW — N ADAMS HARRIMAN AP (MA) | 77.43% | 77.33% | 76.43% | 30/35 | 0.03% (1995) |
| ACK — NANTUCKET MEM AP (MA) | 90.56% | 90.12% | 90.56% | 35/35 | 56.77% (1995) |
| EWB — NEW BEDFORD MUNI AP (MA) | 89.19% | 88.21% | 90.36% | 35/35 | 26.62% (1994) |
| PSF — PITTSFIELD MUNI AP (MA) | 64.93% | 64.83% | 64.39% | 24/35 | 23.34% (2001) |
| PYM — PLYMOUTH MUNI AP (MA) | 82.31% | 82.27% | 81.85% | 32/35 | 0.00% (1993) |
| PVC — PROVINCETOWN MUNI AP (MA) | 89.10% | 88.39% | 88.61% | 35/35 | 29.92% (1990) |
| MVY — VINEYARD HAVEN MARTHAS VINEYAR (MA) | 88.74% | 84.73% | 89.08% | 35/35 | 0.39% (1990) |
| WALPOLE 2 (MA) | N/A | N/A | N/A | 0/35 | N/A |
| BAF — WESTFIELD BARNES MUNI AP (MA) | 88.65% | 87.29% | 88.50% | 35/35 | 12.43% (1991) |
| ORH — WORCESTER (MA) | 97.23% | 97.08% | 97.22% | 35/35 | 84.98% (2004) |
| AUG — AUGUSTA STATE AP (ME) | 98.28% | 98.22% | 98.11% | 35/35 | 91.45% (1995) |
| BANGOR INTL AP (ME) | 97.13% | 97.11% | 98.50% | 35/35 | 44.84% (1996) |
| CARIBOU WFO (ME) | 97.38% | 91.74% | 91.58% | 35/35 | 69.22% (1990) |
| CORINNA (ME) | N/A | N/A | N/A | 0/35 | N/A |
| FARMINGTON (ME) | N/A | N/A | N/A | 0/35 | N/A |
| GARDINER (ME) | N/A | N/A | N/A | 0/35 | N/A |
| HOULTON AP (ME) | 97.60% | 97.50% | 97.39% | 35/35 | 88.34% (1990) |
| MILLINOCKET MUNI AP (ME) | 76.04% | 75.41% | 75.29% | 35/35 | 0.00% (1990) |
| PWM — PORTLAND JETPORT (ME) | 97.89% | 97.82% | 97.80% | 35/35 | 78.68% (1999) |
| PRESQUE ISLE MUNI AP (ME) | 91.72% | 89.98% | 91.11% | 35/35 | 0.07% (1990) |
| CON — CONCORD ASOS (NH) | 98.35% | 98.30% | 98.03% | 35/35 | 86.36% (1999) |
| DURHAM (NH) | 0.00% | 0.00% | 0.00% | 35/35 | 0.00% (1990) |
| HANOVER (NH) | 0.00% | 0.00% | 0.00% | 35/35 | 0.00% (1990) |
| KEENE (NH) | N/A | N/A | N/A | 0/35 | N/A |
| EEN — KEENE DILLNT-HOPKNS AP (NH) | 88.73% | 88.56% | 89.23% | 35/35 | 0.00% (1990) |
| LEB — LEBANON MUNI AP (NH) | 92.76% | 92.28% | 93.17% | 35/35 | 51.84% (1991) |
| MHT — MANCHESTER AP (NH) | 95.61% | 94.67% | 95.23% | 35/35 | 72.78% (1990) |
| MT WASHINGTON (NH) | 70.12% | 69.34% | 80.99% | 35/35 | 49.58% (1990) |
| PINKHAM NOTCH (NH) | 0.00% | 0.00% | 0.00% | 35/35 | 0.00% (1990) |
| PSM — PORTSMOUTH PEASE AFB (NH) | 98.68% | 98.68% | 98.48% | 35/35 | 80.54% (1999) |
| ATLANTIC CITY INTL AP (NJ) | 97.27% | 97.17% | 97.19% | 35/35 | 81.43% (1998) |
| ATLANTIC CITY MARINA (NJ) | 14.50% | 14.50% | 16.78% | 10/35 | 0.00% (1990) |
| MILLVILLE MUNI AP (NJ) | 97.78% | 97.70% | 98.08% | 35/35 | 90.31% (1998) |
| NEWARK LIBERTY INTL AP (NJ) | 98.59% | 98.59% | 98.70% | 35/35 | 83.12% (1999) |
| TETERBORO AP (NJ) | 97.55% | 97.42% | 97.19% | 35/35 | 86.03% (2001) |
| TRENTON-MERCER AP (NJ) | 89.85% | 88.84% | 89.58% | 35/35 | 21.85% (1996) |
| ALB — ALBANY INTL AP (NY) | 98.72% | 98.71% | 98.75% | 35/35 | 82.77% (1999) |
| BINGHAMTON (NY) | 99.49% | 99.48% | 99.61% | 35/35 | 97.35% (2008) |
| BRIDGEHAMPTON (NY) | N/A | N/A | N/A | 0/35 | N/A |
| BUFFALO (NY) | 97.60% | 97.60% | 97.71% | 35/35 | 78.21% (1999) |
| CANTON 4 SE (NY) | 0.00% | 0.00% | 0.00% | 32/35 | 0.00% (1990) |
| DANSVILLE MUNI AP (NY) | 65.35% | 65.31% | 64.97% | 24/35 | 31.45% (2001) |
| DUNKIRK CHAUTAUQUA CO AP (NY) | 72.26% | 72.19% | 71.99% | 26/35 | 71.04% (2004) |
| ELMIRA CORNING RGNL AP (NY) | 97.51% | 97.39% | 96.76% | 35/35 | 77.73% (2001) |
| GLENS FALLS AP (NY) | 97.19% | 97.15% | 96.98% | 35/35 | 88.78% (1995) |
| ISLIP-LI MACARTHUR AP (NY) | 99.42% | 99.33% | 99.45% | 35/35 | 93.85% (1997) |
| JFK — JFK INTL AP (NY) | 98.10% | 98.10% | 98.14% | 35/35 | 82.77% (1998) |
| LAGUARDIA AP (NY) | 98.19% | 98.19% | 98.19% | 35/35 | 82.89% (1998) |
| MASSENA INTL AP (NY) | 98.67% | 98.58% | 98.67% | 35/35 | 92.37% (2008) |
| MOHONK LAKE (NY) | 0.00% | 0.00% | 0.00% | 13/35 | 0.00% (2012) |
| NIAGARA FALLS INTL AP (NY) | 94.94% | 94.86% | 96.46% | 35/35 | 49.13% (1996) |
| NY CITY CNTRL PARK (NY) | 82.32% | 82.23% | 66.62% | 30/35 | 0.00% (1995) |
| PLATTSBURGH INTL AP (NY) | N/A | N/A | N/A | 0/35 | N/A |
| POUGHKEEPSIE AP (NY) | 97.08% | 96.85% | 96.05% | 35/35 | 72.97% (2001) |
| ROCHESTER GTR INTL (NY) | 98.64% | 98.63% | 98.60% | 35/35 | 83.15% (1998) |
| SARATOGA SPRINGS 4 SW (NY) | N/A | N/A | N/A | 0/35 | N/A |
| SYRACUSE HANCOCK INTL AP (NY) | 97.81% | 97.80% | 97.72% | 35/35 | 78.06% (1999) |
| WATERTOWN AP (NY) | 98.12% | 98.08% | 97.94% | 35/35 | 91.78% (1995) |
| WESTCHESTER CO AP (NY) | 97.55% | 97.22% | 97.35% | 35/35 | 88.15% (2001) |
| WESTHAMPTON GABRESKI AP (NY) | 87.92% | 84.30% | 89.08% | 35/35 | 14.26% (1997) |
| BLOCK ISLAND STATE AP (RI) | 88.38% | 87.91% | 89.33% | 35/35 | 39.52% (2009) |
| KINGSTON (RI) | N/A | N/A | N/A | 0/35 | N/A |
| N FOSTER 1 E (RI) | N/A | N/A | N/A | 0/35 | N/A |
| UUU — NEWPORT STATE AP (RI) | 71.87% | 71.84% | 71.47% | 26/35 | 61.42% (1999) |
| PVD — PROVIDENCE (RI) | 97.91% | 97.88% | 97.89% | 35/35 | 82.72% (1998) |
| DDH — BENNINGTON MORSE STATE AP (VT) | 65.33% | 65.12% | 64.81% | 25/35 | 0.00% (1999) |
| BTV — BURLINGTON INTL AP (VT) | 97.77% | 97.74% | 97.67% | 35/35 | 77.97% (1999) |
| CORNWALL (VT) | N/A | N/A | N/A | 0/35 | N/A |
| MPV — MONTPELIER AP (VT) | 98.19% | 98.06% | 98.00% | 35/35 | 91.02% (1995) |
| S LINCOLN (VT) | N/A | N/A | N/A | 0/35 | N/A |
| SAINT JOHNSBURY (VT) | 70.00% | 69.68% | 14.74% | 33/35 | 0.00% (1998) |
| VSF — SPRINGFIELD HARTNESS STATE AP (VT) | 80.38% | 80.30% | 79.31% | 30/35 | 5.92% (1995) |

## Evidence and reproduction

Registry: docs/history_audit_registry.json. Audit code:
analysis/audit_station_history.py. Generated machine-readable evidence and
monthly/source/QC detail: outputs/audits/all94/period_metrics.json and
outputs/audits/all94/hourly_annual.json. Outputs are ignored by Git; registry,
methodology and this report are retained.

Use an environment with pandas and pyarrow, then run:

```bash
python analysis/audit_station_history.py
python analysis/report_station_history.py
```

The audit reuses cached public archive files and checkpoints. It does not write
to PostgreSQL, clean production data, update the map or replace stations.

Sources: [NOAA GHCNh](https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly),
[source-dependent QC documentation](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh_DOCUMENTATION.pdf),
[GHCN-Daily](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily).
