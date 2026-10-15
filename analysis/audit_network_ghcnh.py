"""Read-only all-network GHCNh availability audit, 2005–2024 plus 2025 readiness.

One coherent routine record/hour. Known-bad-QC filtered using the existing
adapter, unknown/calculated QC counted separately. No ingestion or interpolation.
"""
import argparse
import calendar
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ghcnh_backfill import STATIONS, BASE, CORE, NUMERIC, REGULAR, A, B, rejected
from audit_pvc_neighbors import qc_tier
from eda_utils import database_engine

OUT = ROOT / "outputs/audits/network_ghcnh"
FIELDS = {"temperature": "temperature_c", "dew_point_temperature": "dewpoint_c",
          "relative_humidity": "relative_humidity", "station_level_pressure": "station_pressure_hpa",
          "sea_level_pressure": "sea_level_pressure_hpa", "altimeter": "altimeter_hpa",
          "wind_speed": "wind_speed_ms", "wind_direction": "wind_direction_reported",
          "wind_gust": "wind_gust_ms", "precipitation": "hourly_precipitation_mm"}
DB_FIELDS = {"temperature_c": "temperature_c", "dewpoint_c": "dewpoint_c",
             "relative_humidity": "relative_humidity", "station_pressure_hpa": "station_pressure_hpa",
             "wind_speed_ms": "wind_speed_ms", "wind_direction_reported": "wind_direction",
             "wind_gust_ms": "wind_gust_ms", "hourly_precipitation_mm": "precipitation_mm"}
SUFFIXES = ("_Source_Code", "_Quality_Code", "_Measurement_Code", "_Report_Type")


def empty_column(frame, name):
    return frame[name] if name in frame else pd.Series(None, index=frame.index, dtype="object")


def flags(frame, field, suffix):
    return empty_column(frame, field + suffix).fillna("").astype(str)


def screen_field(frame, field):
    """Vectorized equivalent of relevant existing adapter value/flag rules."""
    value = pd.to_numeric(empty_column(frame, field), errors="coerce")
    source = flags(frame, field, "_Source_Code")
    quality = flags(frame, field, "_Quality_Code")
    report = flags(frame, field, "_Report_Type")
    measurement = flags(frame, field, "_Measurement_Code")
    numeric = np.isfinite(value) & value.gt(-999)
    if field == "relative_humidity":
        numeric &= value.between(0, 100)
    if field in {"wind_speed", "wind_gust", "precipitation"}:
        numeric &= value.ge(0)
    if field in {"station_level_pressure", "sea_level_pressure", "altimeter"}:
        numeric &= value.gt(0)
    if field == "wind_direction":
        numeric &= value.between(0, 360)
    point = ~report.isin(["NSRDB", "SOD", "SOM"])
    pairs = list(zip(source, quality))
    unique = set(pairs)
    bad_lookup = {pair: rejected(field, {"s": pair[0], "q": pair[1]}) for pair in unique}
    bad = pd.Series([bad_lookup[pair] for pair in pairs], index=frame.index)
    tier_lookup = {pair: qc_tier(pair[0], pair[1], field) for pair in unique}
    tier = pd.Series([tier_lookup[pair] for pair in pairs], index=frame.index)
    trace = measurement.eq("T") | (measurement.eq("2") & source.isin(A | B))
    variable = (field == "wind_direction") & measurement.eq("V") & point & ~bad
    calm = (field == "wind_direction") & measurement.eq("C") & point & ~bad
    calm &= pd.to_numeric(empty_column(frame, "wind_speed"), errors="coerce").eq(0)
    compatible = numeric & point & ~bad
    if field == "wind_direction":
        compatible |= variable | calm
    if field == "precipitation":
        compatible &= report.isin(["FM15", "FM-15"])
        compatible &= ~measurement.isin(["3", "4", "5", "6", "7", "8", "I", "J", "E"])
    accepted = value.where(compatible)
    if field == "wind_direction":
        # Count reported calm/variable states, never claim these are bearings.
        # This numeric marker exists only in the audit's in-memory count frame.
        accepted = accepted.mask(variable | calm, 0.)
    if field == "precipitation":
        accepted = accepted.mask(compatible & trace, 0.)
    calculated = source.isin(A) & quality.eq("4")
    return accepted, {"raw_numeric": numeric & point, "bad_qc": numeric & point & bad,
                      "mapped_qc": compatible & tier.gt(0), "full_qc": compatible & tier.eq(2),
                      "calculated": compatible & calculated,
                      "unmapped_qc": compatible & tier.eq(0) & ~calculated,
                      "trace": compatible & trace if field == "precipitation" else pd.Series(False, index=frame.index),
                      "variable": variable if field == "wind_direction" else pd.Series(False, index=frame.index),
                      "calm": calm if field == "wind_direction" else pd.Series(False, index=frame.index),
                      "numeric_direction": compatible & ~variable & ~calm if field == "wind_direction" else pd.Series(False, index=frame.index),
                      "source_quality": source + "/" + quality}


def select_records(raw):
    frame = raw.copy()
    frame["actual_time"] = pd.to_datetime(frame.DATE, utc=True)
    frame["hour_utc"] = frame.actual_time.dt.floor("h")
    screens = {}
    for field, output in FIELDS.items():
        values, diagnostics = screen_field(frame, field)
        frame[output] = values
        screens[field] = diagnostics
    # Mirror the existing adapter's report-type precedence over its main fields.
    report_columns = [flags(frame, field, "_Report_Type") for field in dict.fromkeys(CORE + NUMERIC)]
    kind = pd.Series("", index=frame.index)
    for code in REGULAR:
        present = pd.concat([column.eq(code) for column in report_columns], axis=1).any(axis=1)
        kind = kind.mask(kind.eq("") & present, code)
    frame["kind"] = kind
    frame["priority"] = np.where(kind.eq("FM15"), 0, np.where(kind.eq("FM12"), 2, 1))
    frame["core_count"] = frame[["temperature_c", "dewpoint_c", "wind_speed_ms"]].notna().sum(axis=1)
    chosen = frame[kind.isin(REGULAR)].sort_values(["hour_utc", "priority", "core_count", "actual_time"],
                                                   ascending=[True, True, False, False], kind="stable")
    chosen = chosen.drop_duplicates("hour_utc")
    return chosen, screens


def find_file(station, year, output):
    candidates = [ROOT / "data/raw/ghcnh" / str(year) / (station + ".parquet"),
                  ROOT / "outputs/audits/pvc_neighbors/raw" / f"{station}_{year}.parquet",
                  ROOT / "outputs/reconstruction/pvc_pressure_holdout/test_raw" / f"{station}_{year}.parquet",
                  output / "raw" / str(year) / (station + ".parquet")]
    url = f"{BASE}/{year}/parquet/GHCNh_USW000{STATIONS[station]}_{year}.parquet"
    for path in candidates:
        if path.exists():
            return path, url, "cached"
    path = candidates[-1]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".partial")
    response = subprocess.run(["curl", "-fLsS", "--max-time", "60", "--retry", "1", url,
                               "-o", str(temporary)], capture_output=True, text=True)
    if response.returncode:
        temporary.unlink(missing_ok=True)
        status = "confirmed_no_file" if "404" in response.stderr else "unresolved_download_error"
        raise RuntimeError(status + ": " + response.stderr[:200])
    pq.ParquetFile(temporary)
    temporary.replace(path)
    return path, url, "downloaded"


def audit_pair(pair, output):
    station, year = pair
    expected = (366 if calendar.isleap(year) else 365) * 24
    record = {"station": station, "year": year, "expected_hours": expected,
              "station_id": "USW000" + STATIONS[station]}
    try:
        path, url, cache = find_file(station, year, output)
        names = pq.ParquetFile(path).schema.names
        columns = [name for name in names if name in {"DATE", "STATION"} or
                   any(name == field or name in [field + suffix for suffix in SUFFIXES] for field in FIELDS)]
        raw = pq.read_table(path, columns=columns, use_threads=False).to_pandas()
        if "STATION" in raw and set(raw.STATION.dropna().astype(str)) != {record["station_id"]}:
            raise ValueError("Station identity mismatch")
        times = pd.to_datetime(raw.DATE, utc=True)
        if set(times.dt.year) != {year}:
            raise ValueError("Unexpected UTC source year")
        chosen, screens = select_records(raw)
        record.update({"status": "read", "file_url": url, "path": str(path), "cache": cache,
                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "raw_rows": len(raw),
                       "routine_hours": len(chosen), "first_raw_time": times.min().isoformat(),
                       "last_raw_time": times.max().isoformat(), "flags": {}})
        monthly = []
        for field, column in FIELDS.items():
            values = chosen[column]
            record[column + "_hours"] = int(values.notna().sum())
            record[column + "_first"] = chosen.loc[values.notna(), "actual_time"].min().isoformat() if values.notna().any() else None
            record[column + "_last"] = chosen.loc[values.notna(), "actual_time"].max().isoformat() if values.notna().any() else None
            diagnostics = screens[field]
            for name in ["raw_numeric", "bad_qc", "mapped_qc", "full_qc", "calculated", "unmapped_qc", "trace", "variable", "calm", "numeric_direction"]:
                record[column + "_" + name + "_hours"] = int(diagnostics[name].loc[chosen.index].sum())
            record["flags"][field] = diagnostics["source_quality"].loc[chosen.index][diagnostics["raw_numeric"].loc[chosen.index]].value_counts().to_dict()
        for month in range(1, 13):
            subset = chosen[chosen.actual_time.dt.month.eq(month)]
            month_record = {"station": station, "year": year, "month": month,
                            "expected_hours": calendar.monthrange(year, month)[1] * 24,
                            "routine_hours": len(subset)}
            month_record.update({column + "_hours": int(subset[column].notna().sum()) for column in FIELDS.values()})
            monthly.append(month_record)
        return record, monthly
    except Exception as error:
        record.update({"status": "confirmed_no_file" if "confirmed_no_file" in str(error) else "unresolved",
                       "error": str(error)[:400], "routine_hours": 0})
        record.update({column + "_hours": 0 for column in FIELDS.values()})
        return record, []


def current_database_coverage():
    engine = database_engine()
    expressions = [f"COUNT({column}) AS {name}_hours" for name, column in DB_FIELDS.items()]
    query = text("""SELECT station, EXTRACT(YEAR FROM datetime_utc AT TIME ZONE 'UTC')::int AS year,
        COUNT(*) AS routine_hours, """ + ", ".join(expressions) + """ FROM weather_hourly_utc
        WHERE datetime_utc >= TIMESTAMPTZ '2005-01-01 00:00+00'
        AND datetime_utc < TIMESTAMPTZ '2025-01-01 00:00+00'
        GROUP BY station, year ORDER BY station, year""")
    with engine.connect() as connection:
        if connection.execute(text("SHOW transaction_read_only")).scalar() != "on":
            raise ValueError("Use read-only connection")
        before = connection.execute(text("SELECT count(*) FROM weather_observations")).scalar()
        network = list(connection.execute(text("SELECT station FROM station_metadata ORDER BY station")).scalars())
        if network != sorted(STATIONS):
            raise ValueError("Database network differs from the agreed twenty")
        frame = pd.read_sql_query(query, connection)
        after = connection.execute(text("SELECT count(*) FROM weather_observations")).scalar()
        if before != after:
            raise ValueError("Database row count changed during audit")
    engine.dispose()
    return frame, {"observation_rows_before": before, "observation_rows_after": after,
                   "station_codes": network, "database_writes": False}


def summarize(annual, first, last):
    subset = annual[annual.year.between(first, last)]
    columns = ["routine_hours"] + [column + "_hours" for column in FIELDS.values()]
    result = subset.groupby("station")[["expected_hours"] + columns].sum()
    for column in columns:
        result[column.removesuffix("_hours") + "_pct"] = result[column] / result.expected_hours * 100
    result["files_read"] = subset.groupby("station").status.apply(lambda values: int(values.eq("read").sum()))
    result["expected_files"] = last - first + 1
    return result.reset_index()


def run(output, start=2005, end=2025, workers=4):
    output.mkdir(parents=True, exist_ok=True)
    results, monthly = [], []
    jobs = [(station, year) for year in range(start, end + 1) for station in sorted(STATIONS)]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(audit_pair, pair, output) for pair in jobs]
        for number, future in enumerate(as_completed(futures), 1):
            record, months = future.result()
            results.append(record)
            monthly.extend(months)
            if number % 20 == 0 or record["status"] != "read":
                print(f"Checked {number}/{len(jobs)}: {record['station']} {record['year']} {record['status']}", flush=True)
    results.sort(key=lambda row: (row["station"], row["year"]))
    (output / "source_manifest.json").write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
    annual = pd.DataFrame([{key: value for key, value in row.items() if key != "flags"} for row in results])
    annual.to_csv(output / "annual_availability.csv", index=False)
    pd.DataFrame(monthly).sort_values(["station", "year", "month"]).to_csv(output / "monthly_availability.csv", index=False)
    summary = summarize(annual, 2005, 2024)
    summary.to_csv(output / "station_summary_2005_2024.csv", index=False)
    modern = summarize(annual, 2020, 2024)
    modern.to_csv(output / "station_summary_2020_2024.csv", index=False)
    if end >= 2025:
        summarize(annual, 2025, 2025).to_csv(output / "station_summary_2025.csv", index=False)
    database, snapshot = current_database_coverage()
    database.to_csv(output / "production_annual_availability.csv", index=False)
    compare = annual[annual.year.between(2005, 2024)].merge(database, on=["station", "year"], suffixes=("_ghcnh", "_production"), validate="one_to_one")
    comparison = []
    for first, last in [(2005, 2024), (2020, 2024), (2024, 2024)]:
        period = compare[compare.year.between(first, last)]
        for station, group in period.groupby("station"):
            denominator = int(group.expected_hours.sum())
            for field in ["routine"] + list(DB_FIELDS):
                column = "routine_hours" if field == "routine" else field + "_hours"
                new, old = int(group[column + "_ghcnh"].sum()), int(group[column + "_production"].sum())
                comparison.append({"station": station, "period": f"{first}–{last}", "element": field,
                                   "expected_hours": denominator, "ghcnh_hours": new, "production_hours": old,
                                   "ghcnh_pct": new / denominator * 100, "production_pct": old / denominator * 100,
                                   "change_percentage_points": (new - old) / denominator * 100})
    pd.DataFrame(comparison).to_csv(output / "source_coverage_comparison.csv", index=False)
    audit = {"scope": "20 stations, UTC 2005–2024 plus separate 2025 readiness",
             "checked_station_years": len(results), "successful_files": int(annual.status.eq("read").sum()),
             "historical_successful_files": int(annual[annual.year.le(2024)].status.eq("read").sum()),
             "unresolved": [row for row in results if row["status"] != "read"],
             "database_snapshot": snapshot,
             "qc_policy": "Existing adapter known-bad flags filtered, calculated/unmapped QC retained and counted separately",
             "selection": "One coherent routine record/hour; FM15 priority, core completeness, latest actual report",
             "precipitation_policy": "FM15 compatibility, accumulation codes excluded, trace separately counted, missing never zero",
             "wind_direction_policy": "Reported numeric direction or calm/variable state, with calm/variable and numeric-bearing counts retained separately",
             "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (output / "audit_summary.json").write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n")
    print(json.dumps({key: value for key, value in audit.items() if key not in {"unresolved", "database_snapshot"}}, indent=2), flush=True)
    if audit["unresolved"]:
        raise RuntimeError("Unresolved files remain; do not call this audit complete")
    return audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--start", type=int, default=2005)
    parser.add_argument("--end", type=int, default=2025)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.start != 2005 or args.end not in {2024, 2025}:
        raise ValueError("This network decision audit covers 2005–2024, optionally 2025")
    run(args.output, args.start, args.end, args.workers)
