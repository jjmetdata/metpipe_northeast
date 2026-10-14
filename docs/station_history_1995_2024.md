# Thirty-year station-history screening: 1995–2024

Audit date: October 12, 2026.

## Outcome and scope

Nine current stations are strong daily-climatology candidates: ALB, AUG, BDL,
BOS, BTV, JFK, ORH, PVD, and PWM. All have daily maximum temperature (TMAX),
minimum temperature (TMIN), and precipitation (PRCP) represented in all 30 years,
with at least 95% quality-accepted daily values for each element in each year.

This is an availability screen, not a homogeneity assessment or certification
for official climate normals. Station moves, instrument changes, observation
times, source changes, and remaining quality issues still need assessment.
The PostgreSQL dataset and station map remain unchanged: 20 stations, 2020–2024.
Historical samples were downloaded only for research; no older data was ingested.

NOAA's current official normals use 1991–2020. The custom 1995–2024 window is
also 30 calendar years, but MetPipe statistics from it should not be called
official NOAA normals. A 1990–2024 window is 35 years.

## Actual daily availability

Source: NOAA GHCN-Daily station files, not simply station metadata start dates.
Denominator: 10,958 calendar days from January 1, 1995 through December 31, 2024.
A value counts as available only when it is not the -9999 missing sentinel and
its GHCN-Daily quality flag is blank. Numeric zeros and trace precipitation
count as present. Percentages are rounded to one decimal: 100.0% need not mean
literally every day. Years with data means at least one accepted value, not a
complete year. These results do not measure hourly wind, humidity, or sky coverage.

| Station | TMAX | TMIN | PRCP | Years with data: TMAX/TMIN/PRCP |
| --- | ---: | ---: | ---: | --- |
| ACK | 88.5% | 88.4% | 87.9% | 27/27/27 |
| ALB | 100.0% | 100.0% | 100.0% | 30/30/30 |
| AUG | 99.9% | 99.9% | 100.0% | 30/30/30 |
| BAF | 87.6% | 87.6% | 87.9% | 27/27/27 |
| BDL | 100.0% | 100.0% | 100.0% | 30/30/30 |
| BDR | 100.0% | 100.0% | 100.0% | 30/30/30 |
| BOS | 100.0% | 100.0% | 100.0% | 30/30/30 |
| BTV | 100.0% | 100.0% | 100.0% | 30/30/30 |
| CON | 100.0% | 100.0% | 100.0% | 30/30/30 |
| GON | 83.1% | 83.0% | 82.8% | 26/26/26 |
| HVN | 77.0% | 77.0% | 76.8% | 24/24/24 |
| JFK | 100.0% | 100.0% | 100.0% | 30/30/30 |
| LEB | 88.5% | 88.5% | 88.6% | 27/27/27 |
| MHT | 89.8% | 89.9% | 88.9% | 28/28/27 |
| MPV | 99.7% | 99.7% | 94.0% | 30/30/29 |
| ORH | 99.9% | 99.9% | 99.5% | 30/30/30 |
| PVD | 100.0% | 100.0% | 100.0% | 30/30/30 |
| PWM | 100.0% | 100.0% | 100.0% | 30/30/30 |
| MQE (Blue Hill) | 100.0% | 99.8% | 100.0% | 30/30/30 |

BAF, HVN, LEB, and MHT have long station metadata histories, but the checked daily
files have substantial gaps in this window. These are archive/element findings,
not a claim that observations were never made at those airports. Historical
LCD or other archives might recover useful measurements; reconciliation is
needed before claiming continuous coverage.

## The other seven current stations

The checked GHCN-Daily inventory does not establish a 1995–2024 daily core for:

- DDH, HYA, and MVY: listed TMAX/TMIN/PRCP records begin in 1998.
- EWB, PYM, and UUU: listed TMAX/TMIN records begin in 1996 and PRCP in 1998.
- PVC: no matching TMAX/TMIN/PRCP inventory entry under USW00064708.

Earlier LCD records and historical IDs were investigated separately. No suitable
1995 LCD file was located for these seven under the checked identifiers.
Absence in these checks is not proof that no other archival source exists.
The older Provincetown cooperative stations (USC00196676 and USC00196681)
are different sites; their listed records end in 1958 and 1992 respectively.
Do not splice those records into airport PVC as if they were one unchanged site.

## Alternatives and network roles

- CON, Concord NH (USW00014745): strong daily core across all 30 years.
- BDR, Bridgeport/Sikorsky CT (USW00094702): strong daily core across all 30 years.
- MQE, Blue Hill Observatory MA (USW00014753): strong daily core; its worst TMIN
  year has 98.36% accepted values. It is an observatory, not an airport, and
  should be labeled as such if added.
- MPV, Montpelier VT: good temperature availability, but precipitation is absent
  for 1997 in the checked file; conditional rather than a full-element core.
- ACK and GON do not qualify for the proposed full-window daily screen in the
  checked archive, despite potentially useful geography and older metadata.

Recommended design: keep a long-record daily-climatology core and a broader
modern hourly network. A shorter-history station can remain valuable for
coastal contrasts, local validation, and later station-to-station lag analysis.
Do not replace every short-history station merely to make a uniform 30-year list.

A proposed MetPipe screening rule is at least 95% accepted daily values per
year per required core element in all 30 years. This is a project proposal,
not NOAA's official normals eligibility or estimation procedure. Seasonal and
monthly completeness should also be checked before producing climatologies.

## Older hourly formats: pipeline implications

Actual 1995 LCD files were checked for ALB, AUG, BAF, BDL, BOS, BTV, HVN, JFK,
LEB, MHT, ORH, PVD, and PWM. They use older SAO, SY-SA, and SAOSP report codes;
none of these samples has FM-15 rows. Some include NSRDB records, which must
not be treated blindly as measured routine observations.

Routine-report unique-hour coverage in the 1995 samples (SAO/SY-SA/FM-15/FM-12;
excluding special reports and NSRDB) is: ALB 99.9%, AUG 91.5%, BAF 60.7%,
BDL 99.9%, BOS 99.9%, BTV 99.9%, HVN 69.0%, JFK 99.9%, LEB 65.6%, MHT 89.7%,
ORH 99.6%, PVD 99.9%, and PWM 99.9%. These are one-year hour-presence checks,
not all-element hourly quality results or full 30-year continuity claims.

The current FM-15-only, fixed-minute hourly view would discard these older
routine observations. Before hourly backfill, support historical report types,
time-dependent schedules, source provenance, quality flags, and historical IDs.
Daily GHCN-Daily ingestion should be a separate path, not mixed into the hourly
observation table as if daily extrema were instantaneous measurements.

## Sources

- [NOAA U.S. Climate Normals](https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals)
- [GHCN-Daily format and quality flags](https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt)
- [GHCN-Daily element inventory](https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt)
- [GHCN-Daily station files](https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/)
- [Archived 1995 LCD files](https://www.ncei.noaa.gov/data/local-climatological-data/access/1995/)
- See station_history_2000_2024.md for checked historical LCD identifiers and
  representative 2000–2005 hourly samples.

