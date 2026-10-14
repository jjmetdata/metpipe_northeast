"""Read-only NOAA history audit; does not clean, ingest, or replace stations.

Requires pandas and pyarrow. Generated research results go under outputs/audits.
Uses a fixed source/QC screen, preserving daily and hourly roles separately.
"""
import argparse
import calendar
import csv
import glob
import json
import os
from pathlib import Path
import subprocess
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.ncei.noaa.gov/oa/global-historical-climatology-network"
WINDOWS = [2005, 1995, 1990]
CORE = ["temperature", "dew_point_temperature", "wind_speed"]
FIELDS = CORE + ["wind_direction", "station_level_pressure", "sea_level_pressure", "precipitation"]
ROUTINE = ["FM15", "FM12", "SAO", "SYSA", "SYMT", "SYAE", "SYAU", "SSA", "SAAU"]
SOURCE_A = ["220", "221", "222", "223", "347", "348"]
SOURCE_B = ["313", "314", "315", "322", "335", "343", "344", "346"]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(json.dumps(value))
    temporary.replace(path)


def download(url, path):
    result = subprocess.run(
        ["curl", "-fLsS", "--max-time", "90", "--retry", "2", url, "-o", str(path)],
        capture_output=True,
    )
    if result.returncode:
        if path.exists():
            path.unlink()
        message = result.stderr.decode()[:300]
        return "archive_file_unavailable" if "404" in message else "download_error", message
    return None, None


def inventories(ids, cache, output):
    target = output / "hourly_inventory.json"
    if target.exists():
        return json.loads(target.read_text())
    prior = cache / "metpipe_hourly_inventory_results.json"
    rows = json.loads(prior.read_text()) if prior.exists() else []
    covered_ids = {r["id"] for r in rows}
    extra = ids - covered_ids
    # Previously scanned IDs with zero entries need not be repeatedly fetched.
    old_registry = cache / "metpipe_broad_daily_results.json"
    if old_registry.exists():
        extra -= {r["id"] for r in json.loads(old_registry.read_text())}
    if not prior.exists():
        extra = ids
    if extra:
        for year in range(1990, 2025):
            path = cache / ("metpipe_ghcnh_%s_inventory.tar.gz" % year)
            if not path.exists():
                status, message = download(
                    BASE + "/hourly/inventory/ghcn-hourly_v1.1.0_d%s-inv.tar.gz" % year, path
                )
                if status:
                    raise RuntimeError("Inventory %s unresolved: %s" % (year, message))
            with tarfile.open(str(path), "r|gz") as archive:
                for member in archive:
                    parts = member.name.split("_")
                    if len(parts) < 3 or parts[1] not in extra:
                        continue
                    data = json.load(archive.extractfile(member))
                    fields = {r["id"]: {k: r.get(k) for k in ["coverage", "startDate", "endDate"]}
                              for r in data["stations"][0]["dataTypes"]}
                    rows.append({"year": year, "id": parts[1], "fields": fields})
    rows = [r for r in rows if r["id"] in ids]
    save(target, rows)
    return rows


def audit_hourly(pair, cache):
    import pandas as pd
    import pyarrow.parquet as pq

    sid, year = pair
    path = cache / ("metpipe_all94_%s_%s.parquet" % (sid, year))
    status, message = download(
        BASE + "/hourly/access/by-year/%s/parquet/GHCNh_%s_%s.parquet" % (year, sid, year), path
    )
    if status:
        return {"id": sid, "year": year, "status": status, "error": message}
    try:
        names = pq.ParquetFile(str(path)).schema.names
        columns = ["DATE"] + [e + suffix for e in FIELDS
                              for suffix in ["", "_Quality_Code", "_Source_Code", "_Report_Type"]
                              if e + suffix in names]
        frame = pq.read_table(str(path), columns=columns, use_threads=False).to_pandas()
        frame = frame[frame.DATE.str.startswith(str(year))].copy()
        hours = frame.DATE.str.slice(0, 13)
        expected = (366 if calendar.isleap(year) else 365) * 24
        results = {}
        for element in FIELDS:
            if element not in frame:
                continue
            reports = frame.get(element + "_Report_Type", pd.Series("", index=frame.index)).fillna("")
            sources = frame.get(element + "_Source_Code", pd.Series("", index=frame.index)).fillna("")
            quality = frame.get(element + "_Quality_Code", pd.Series("", index=frame.index)).fillna("")
            measured = frame[element].notna() & frame[element].ne(-9999)
            present = measured & reports.isin(ROUTINE)
            good = present & ((sources.isin(SOURCE_A) & quality.eq("1")) |
                              (sources.isin(SOURCE_B) & quality.isin(["1", "5"])))
            unique = hours[good].drop_duplicates()
            monthly = unique.str.slice(5, 7).value_counts()
            results[element] = {
                "present_hours": int(hours[present].nunique()), "good_hours": int(unique.nunique()),
                "expected": expected, "present_pct": round(100 * hours[present].nunique() / expected, 3),
                "good_pct": round(100 * unique.nunique() / expected, 3),
                "monthly_good_pct": {str(m): round(100 * int(monthly.get("%02d" % m, 0)) /
                                                       (calendar.monthrange(year, m)[1] * 24), 3)
                                     for m in range(1, 13)},
                "any_report_type_hours": int(hours[measured].nunique()),
                "report_type_counts": {str(k): int(v) for k, v in reports[measured].value_counts().items()},
                "source_counts": {str(k): int(v) for k, v in sources[measured].value_counts().items()},
                "quality_counts": {str(k): int(v) for k, v in quality[measured].value_counts().items()},
            }
        return {"id": sid, "year": year, "status": "read", "rows": len(frame), "fields": results}
    except Exception as exc:
        return {"id": sid, "year": year, "status": "parse_error", "error": str(exc)}
    finally:
        if path.exists():
            path.unlink()


def hourly_windows(sid, annual, inventory):
    out = []
    for start in WINDOWS:
        years = list(range(start, 2025))
        expected = sum((366 if calendar.isleap(y) else 365) * 24 for y in years)
        valid = [annual[(sid, y)] for y in years if "fields" in annual.get((sid, y), {})]
        elements = {}
        for e in FIELDS:
            good = sum(r["fields"].get(e, {}).get("good_hours", 0) for r in valid)
            present = sum(r["fields"].get(e, {}).get("present_hours", 0) for r in valid)
            elements[e] = {"accepted_hours": good, "present_hours": present,
                           "accepted_hour_pct": round(100 * good / expected, 3),
                           "present_hour_pct": round(100 * present / expected, 3)}
        failures = {str(y): annual.get((sid, y), {}).get("status", "no_matched_inventory_entry")
                    for y in years if "fields" not in annual.get((sid, y), {})}
        worst = min(((r["fields"].get(e, {}).get("good_pct", 0), r["year"], e)
                     for r in valid for e in CORE), default=None)
        passing = sum(all(r["fields"].get(e, {}).get("good_hours", 0) /
                          ((366 if calendar.isleap(r["year"]) else 365) * 24) >= .95 for e in CORE)
                      for r in valid)
        out.append({"start_year": start, "end_year": 2024, "expected_hours": expected,
                    "years_expected": len(years), "years_read": len(valid),
                    "inventory_years": sum((sid, y) in inventory for y in years),
                    "unavailable_years": failures, "elements": elements,
                    "lowest_core_pct": min(elements[e]["accepted_hour_pct"] for e in CORE),
                    "years_all_core95": passing,
                    "weakest_read_year": {"pct": worst[0], "year": worst[1], "element": worst[2]} if worst else None})
    return out


def daily_windows(sid, cache):
    matches = [cache / ("metpipe_broad_daily_%s.dly" % sid)]
    matches += [Path(p) for p in glob.glob(str(cache / "metpipe_daily_*.dly"))]
    path = None
    for p in matches:
        if p.exists():
            with p.open() as stream:
                if stream.readline()[:11] == sid:
                    path = p
                    break
    if path is None:
        path = cache / ("metpipe_broad_daily_%s.dly" % sid)
        status, error = download("https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/%s.dly" % sid, path)
        if status:
            return {"id": sid, "status": status, "error": error, "windows": []}
    counts = {}
    with path.open() as stream:
        for line in stream:
            year, month, element = int(line[11:15]), int(line[15:17]), line[17:21]
            if not 1990 <= year <= 2024 or element not in ["TMAX", "TMIN", "PRCP"]:
                continue
            for day in range(calendar.monthrange(year, month)[1]):
                offset = 21 + day * 8
                if int(line[offset:offset + 5]) != -9999 and line[offset + 6] == " ":
                    counts[(element, year)] = counts.get((element, year), 0) + 1
    windows = []
    for start in WINDOWS:
        years = list(range(start, 2025))
        expected = sum(366 if calendar.isleap(y) else 365 for y in years)
        fields = {e: {"accepted_day_pct": round(100 * sum(counts.get((e, y), 0) for y in years) / expected, 3),
                      "years95": sum(counts.get((e, y), 0) / (366 if calendar.isleap(y) else 365) >= .95 for y in years)}
                  for e in ["TMAX", "TMIN", "PRCP"]}
        passing = sum(all(counts.get((e, y), 0) / (366 if calendar.isleap(y) else 365) >= .95
                          for e in fields) for y in years)
        windows.append({"start_year": start, "end_year": 2024, "expected_days": expected,
                        "years_expected": len(years), "elements": fields, "years_all_daily95": passing})
    return {"id": sid, "status": "read", "windows": windows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=ROOT / "docs/history_audit_registry.json")
    parser.add_argument("--cache", type=Path, default=Path("/tmp"))
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/audits/all94")
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    registry = json.loads(args.registry.read_text())["locations"]
    ids = {sid for r in registry for sid in r["hourly_ids"]}
    inv = inventories(ids, args.cache, args.output)
    inventory = {(r["id"], r["year"]) for r in inv}
    annual = {}
    seeds = [args.cache / "metpipe_full_hourly_results.json", args.cache / "metpipe_extra_full_hourly_results.json",
             args.output / "hourly_annual.json"]
    for path in seeds:
        if not path.exists():
            continue
        for r in json.loads(path.read_text()):
            if r["id"] in ids and ("fields" in r or "404" in r.get("error", "")):
                if "fields" in r:
                    r["status"] = "read"
                else:
                    r["status"] = "archive_file_unavailable"
                annual[(r["id"], r["year"])] = r
    pending = sorted(inventory - set(annual))
    print("LOCATIONS", len(registry), "INVENTORY_YEARS", len(inventory), "REUSED", len(annual), "TO_READ", len(pending), flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(audit_hourly, pair, args.cache): pair for pair in pending}
        for number, job in enumerate(as_completed(jobs), 1):
            r = job.result()
            annual[(r["id"], r["year"])] = r
            if r["status"] in ["download_error", "parse_error"]:
                print("UNRESOLVED", r["id"], r["year"], r["error"], flush=True)
            if number % 50 == 0:
                save(args.output / "hourly_annual.json", list(annual.values()))
                print("PROGRESS", number, "of", len(pending), flush=True)
    save(args.output / "hourly_annual.json", list(annual.values()))
    daily = {sid: daily_windows(sid, args.cache) for r in registry for sid in r["daily_ids"]}
    result = []
    for r in registry:
        result.append(dict(r, hourly={sid: hourly_windows(sid, annual, inventory) for sid in r["hourly_ids"]},
                           daily={sid: daily[sid] for sid in r["daily_ids"]}))
    audit = {"audit_date": "2026-10-12", "location_count": len(registry), "windows": WINDOWS,
             "method": "Strict source-aware QC for selected routine hours; daily GHCNd quality flags separately",
             "locations": result, "unresolved": [r for r in annual.values()
                                                      if r.get("status") in ["download_error", "parse_error"]]}
    save(args.output / "period_metrics.json", audit)
    print("COMPLETE", len(result), "locations", "unresolved", len(audit["unresolved"]), flush=True)


if __name__ == "__main__":
    main()
