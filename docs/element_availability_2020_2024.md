# MetPipe element availability, 2020–2024

Audit date: October 11, 2026.

PostgreSQL now contains **1,297,439 observations from all 20 stations**, covering
100 station-year combinations. All 100 database counts match the prepared source
records. A database backup was created before the 10 additions were ingested.
The hourly view contains **874,057 scheduled reports**, covering all **1,200
station-month combinations** (20 stations × 60 months). Every station has all
five years represented. The import added 637,041 observations to the original
660,398; original station-year counts were retained.

## Measurement

The table gives the percentage of **existing scheduled hourly reports** with a
stored or parseable value for each element. It excludes entirely missing hours
from the element denominator. There are 43,848 expected hours in 2020–2024.
`Report` measures existing scheduled reports against those expected hours.

Values were queried from `weather_hourly` for all 20 ingested stations. The
additions were first audited in memory from their source CSVs; those percentages
were then verified against the database. The audit selects FM-15 reports at the
checked minute and keeps the earliest record per hour. A trailing `s`
was stripped for numeric parsing, `T` counted as a present precipitation value,
and `*`, blanks, and other nonnumeric values counted as absent. This matches
current storage behavior, but does **not** certify suspect values as reliable.
All percentages are rounded to one decimal place; 100.0% may include a small
number of absent values.

`DB` means ingested in PostgreSQL; every station in this table is now ingested.
`Temp` is dry-bulb temperature, `Dew` dew point, `RH` relative humidity,
`Press` station pressure, and `Dir` wind direction. All entries are percentages.

| Station | Status | Report | Temp | Dew | RH | Press | Wind speed | Dir | Precipitation | Sky | Gust |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ALB | DB | 99.9 | 100.0 | 100.0 | 100.0 | 99.9 | 100.0 | 100.0 | 99.7 | 99.9 | 14.9 |
| AUG | DB | 99.8 | 99.6 | 99.6 | 99.6 | 99.8 | 99.6 | 99.5 | 99.5 | 99.7 | 15.8 |
| BAF | DB | 99.8 | 99.6 | 99.6 | 99.6 | 99.3 | 99.7 | 99.7 | 99.3 | 99.4 | 12.3 |
| BDL | DB | 99.9 | 100.0 | 100.0 | 100.0 | 99.5 | 100.0 | 100.0 | 99.4 | 99.6 | 11.4 |
| BOS | DB | 99.9 | 100.0 | 100.0 | 100.0 | 99.8 | 100.0 | 100.0 | 99.6 | 99.8 | 17.0 |
| BTV | DB | 99.7 | 100.0 | 99.9 | 99.9 | 99.7 | 99.8 | 99.8 | 99.7 | 99.7 | 15.0 |
| DDH | DB | 99.6 | 99.8 | 98.5 | 98.5 | 99.5 | 98.9 | 98.9 | 97.6 | 99.0 | 13.9 |
| EWB | DB | 99.8 | 99.7 | 99.4 | 99.4 | 99.5 | 99.6 | 99.6 | 99.3 | 99.4 | 18.0 |
| HVN | DB | 99.8 | 99.6 | 99.6 | 99.6 | 99.5 | 99.7 | 99.7 | 98.7 | 99.5 | 17.1 |
| HYA | DB | 99.8 | 99.5 | 99.5 | 99.5 | 99.1 | 99.3 | 99.3 | 97.0 | 98.9 | 24.8 |
| JFK | DB | 99.9 | 100.0 | 100.0 | 100.0 | 98.1 | 100.0 | 100.0 | 97.8 | 98.2 | 15.0 |
| LEB | DB | 99.9 | 99.6 | 99.6 | 99.6 | 99.7 | 99.4 | 99.4 | 99.5 | 99.5 | 9.7 |
| MHT | DB | 99.9 | 100.0 | 99.9 | 99.9 | 97.7 | 99.9 | 99.9 | 97.5 | 97.8 | 14.3 |
| MVY | DB | 99.8 | 99.6 | 99.5 | 99.5 | 97.1 | 99.2 | 99.2 | 98.4 | 98.1 | 24.5 |
| ORH | DB | 99.8 | 100.0 | 99.9 | 99.9 | 98.0 | 99.8 | 99.8 | 97.5 | 98.3 | 21.3 |
| PVC | DB | 97.3 | 98.3 | 98.3 | 98.3 | 94.5 | 99.6 | 99.6 | 12.8 | 94.5 | 26.6 |
| PVD | DB | 99.8 | 99.9 | 99.8 | 99.8 | 97.7 | 99.9 | 99.9 | 98.5 | 97.9 | 15.1 |
| PWM | DB | 99.7 | 100.0 | 99.9 | 99.9 | 98.1 | 99.9 | 99.9 | 98.3 | 98.2 | 13.2 |
| PYM | DB | 99.5 | 99.8 | 99.8 | 99.8 | 97.4 | 99.3 | 99.3 | 97.6 | 97.3 | 19.4 |
| UUU | DB | 99.8 | 99.8 | 99.8 | 99.8 | 98.0 | 99.5 | 99.5 | 98.2 | 97.9 | 22.0 |

## Findings that annual coverage hides

- **Precipitation cell presence is not a comparable completeness metric across
  stations.** PVC has no explicit numeric `0.00` precipitation values in its
  scheduled 2020–2024 reports, while BOS has 37,263 explicit zero values. METAR
  hourly precipitation groups can be omitted when no precipitation occurred.
  Thus PVC's 12.8% non-null rate partly reflects a reporting convention and must
  not be described as 87.2% missing precipitation observations.
- The 42,672 scheduled PVC reports contain 2,385 positive precipitation amounts,
  3,067 traces, and 37,220 blank precipitation cells. The current cleaner reads
  source blanks as NaN and ingestion stores them as SQL NULL.
- Some blanks genuinely remain unknown: 5,575 blank PVC reports contain `PNO`
  (rain gauge not operating), and 513 blank reports contain precipitation tokens
  such as `-RA` or `-SN` in the METAR body. These sets may overlap. Another 2,074
  blank reports contain an unavailable 3/6-hour precipitation group (`6////`).
  Current weather without a precipitation token also does not prove that no
  precipitation fell earlier in the preceding hour. Blanket NULL-to-zero
  replacement is therefore inappropriate. Future classification should retain
  measured amount, trace, inferred dry, and unknown states with provenance.
- PVC December 2024 has 716 scheduled reports, but 0% have structured station
  pressure or sky-condition values. Some raw METAR remarks still include sky
  conditions and an altimeter setting. For example, the December 1 16:56 LCD
  record contains `CLR` and `A3000` in the original METAR while the structured
  sky and station-pressure columns are blank. This suggests a structured-field
  extraction or encoding problem for at least some records; it is not evidence
  that every corresponding sensor observation was absent.
- Similar concentrated December 2024 gaps occur at MHT, ORH, PYM, MVY, and UUU.
  JFK has a comparable concentration in April 2024. These periods deserve
  source-level investigation before replacing stations on field availability
  alone. Altimeter setting, sea-level pressure, and station pressure are
  different quantities and must not be substituted for one another.
- Annual minima can be appreciably lower than five-year averages. For example,
  MHT 2024 has 89.8% station-pressure and 90.3% sky availability; HYA 2021 has
  90.4% precipitation availability; DDH 2022 has 96.6% dew-point availability.
- Gusts occur in only 9.7–26.6% of existing hourly reports across the network.
  Gust reporting is conditional, so low gust presence alone does not indicate
  missing routine observations. Blank gusts remain distinct from numeric zero.
- The current cleaner discards suspect-value suffixes and replaces trace rain
  with an artificial numeric amount. The table therefore describes current
  stored/parseable values, not quality-approved measurements. Preserving source
  flags is a separate pipeline improvement.

## Reproduce the database checks

Open `sql/element_availability.sql` in DataGrip. It returns ingestion status for
all 20 stations, per-element overall and annual availability for loaded
stations, and monthly PVC diagnostics. Both the existing-report denominator and
the expected-hour denominator are shown. The queries are read-only.

Sources: [NOAA LCDv1 archive](https://www.ncei.noaa.gov/data/local-climatological-data/access/),
[NOAA LCD documentation](https://www.ncei.noaa.gov/pub/data/cdo/documentation/LCD_documentation.pdf),
[NWS ASOS wind reporting](https://www.weather.gov/asos/WindSensor.html),
and [AWC METAR precipitation and sensor-status definitions](https://aviationweather.gov/help/data/).
