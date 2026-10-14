"""Render the all-location audit without conflating hourly and daily roles."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STARTS = [2005, 1995, 1990]
CURRENT = {"BOS", "PVD", "ALB", "JFK", "ORH", "PVC", "EWB", "HYA", "MVY", "PYM",
           "BAF", "BDL", "HVN", "UUU", "BTV", "DDH", "MHT", "LEB", "PWM", "AUG"}


def hourly(location, start):
    return next(r for r in location["hourly"][location["primary_hourly_id"]] if r["start_year"] == start)


def daily(location, start):
    source = location["daily"][location["primary_daily_id"]]
    return next((r for r in source["windows"] if r["start_year"] == start), None)


def label(location):
    code = location.get("code")
    return (code + " — " if code else "") + location["name"].replace("|", "\\|") + " (" + location["state"] + ")"


def hour_cell(location, start):
    r = hourly(location, start)
    if r["inventory_years"] == 0:
        return "No matched inventory"
    if r["years_read"] == 0:
        return "No readable file"
    if max(r["elements"][e]["present_hours"] for e in ["temperature", "dew_point_temperature", "wind_speed"]) == 0:
        return "No selected routine core"
    return "%.2f%%; %s/%s years >=95%%" % (r["lowest_core_pct"], r["years_all_core95"], r["years_expected"])


def daily_cell(location, start):
    r = daily(location, start)
    if r is None:
        return "No readable daily file"
    low = min(v["accepted_day_pct"] for v in r["elements"].values())
    return "%.2f%%; %s/%s years >=95%%" % (low, r["years_all_daily95"], r["years_expected"])


def render(audit):
    locations = sorted(audit["locations"], key=lambda r: (r["state"], r["name"]))
    current = sorted((r for r in locations if r.get("code") in CURRENT), key=lambda r: r["code"])
    matched = [r for r in locations if hourly(r, 1990)["inventory_years"] > 0]
    daily_read = [r for r in locations if daily(r, 1990) is not None]
    table = []
    for start in STARTS:
        hp = sum(hourly(r, start)["years_all_core95"] == hourly(r, start)["years_expected"] for r in locations)
        dp = sum(daily(r, start) is not None and daily(r, start)["years_all_daily95"] == daily(r, start)["years_expected"] for r in locations)
        table.append("| %s–2024 | %s | %s |" % (start, hp, dp))
    overview = "\n".join("| %s | %s |" % (label(r), " | ".join(hour_cell(r, start) for start in STARTS)) for r in locations)
    daily_table = "\n".join("| %s | %s |" % (label(r), " | ".join(daily_cell(r, start) for start in STARTS)) for r in locations)
    current_table = "\n".join("| %s | %s |" % (label(r), " | ".join(hour_cell(r, start) for start in STARTS)) for r in current)
    details = []
    for start in STARTS:
        rows = []
        for location in locations:
            r = hourly(location, start)
            fields = r["elements"]
            if r["years_read"]:
                values = " | ".join("%.2f%%" % fields[e]["accepted_hour_pct"] for e in ["temperature", "dew_point_temperature", "wind_speed"])
            else:
                values = "N/A | N/A | N/A"
            worst = r["weakest_read_year"]
            weak = "%.2f%% (%s)" % (worst["pct"], worst["year"]) if worst else "N/A"
            rows.append("| %s | %s | %s/%s | %s |" % (label(location), values, r["years_read"], r["years_expected"], weak))
        details.append("## Hourly elements, %s–2024\n\n| Location | Temperature | Dew point | Wind speed | Files read | Weakest core year in read files |\n| --- | ---: | ---: | ---: | ---: | --- |\n%s" % (start, "\n".join(rows)))
    return """# All 94 locations: three-window historical audit

Audit date: %(date)s.

## Scope and outcome

All **%(count)s distinct locations** in the registry were assessed for **2005–2024,
1995–2024 and 1990–2024**, keeping hourly and daily records separate.

- **%(matched)s locations** have a matched primary-hourly inventory entry somewhere
  in 1990–2024. Actual available station-year Parquet files were read and screened.
- **%(no_match)s locations** have no matched primary-hourly inventory in this window;
  this is not evidence of bad measurements or proof that no alternate archive exists.
- **%(daily_read)s locations** have a readable primary GHCN-Daily file. The other
  primary daily identifiers were unavailable in the checked archive.
- **%(unresolved)s unresolved download/parse errors** remain. Confirmed unavailable
  files and no-inventory years are recorded separately and remain in denominators.
- The 20 existing database stations, station map and ingested records are unchanged.

These counts refer to the selected 94-location search pool, not an exhaustive
search of every station in the Northeast. Observatories/COOP sites can be daily
climate support without operating a continuous hourly schedule.

| Window | Locations passing every year: hourly core | Locations passing every year: daily core |
| --- | ---: | ---: |
%(summary)s

## Definition and limits

Hourly core = temperature, dew point and wind speed. Daily core = TMAX, TMIN
and PRCP. Passing means each field individually has >=95%% accepted values in
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
%(current)s

## All 94: hourly comparison

No matched inventory / no selected routine core are archive or reporting-role
statuses, not a label that a station is intrinsically unreliable.

| Location | 2005–2024 | 1995–2024 | 1990–2024 |
| --- | --- | --- | --- |
%(overview)s

## All 94: daily comparison

Each cell = lowest total accepted-day coverage; years where all three daily
elements meet 95%%. Do not substitute these values for hourly qualifications.

| Location | 2005–2024 | 1995–2024 | 1990–2024 |
| --- | --- | --- | --- |
%(daily)s

%(details)s

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
""" % {"date": audit["audit_date"], "count": len(locations), "matched": len(matched),
       "no_match": len(locations) - len(matched), "daily_read": len(daily_read),
       "unresolved": len(audit["unresolved"]), "summary": "\n".join(table),
       "current": current_table, "overview": overview, "daily": daily_table,
       "details": "\n\n".join(details)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "outputs/audits/all94/period_metrics.json")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/all94_history_three_windows.md")
    args = parser.parse_args()
    audit = json.loads(args.input.read_text())
    args.output.write_text(render(audit))
    print("Report:", args.output)


if __name__ == "__main__":
    main()
