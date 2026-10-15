"""NOAA-only neighbor screen; research outputs only, never database ingestion.

Availability: 2005–2024 UTC years. Correlations: 2020–2024, plus independent
2024 month/hour temperature departures using a 2020–2023 sample reference.
"""
import calendar
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from hourly_pair import align_hourly
from weather_events import add_pc24, add_reference_and_changes, temperature_reference

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/audits/pvc_neighbors"
BASE = "https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year"
IDS = {"GHG": "USW00064774", "CQX": "USW00094624", "HYA": "USW00094720",
       "PYM": "USW00054769", "PVC": "USW00064708"}
MAP = {"temperature": "temperature_c", "dew_point_temperature": "dewpoint_c",
       "station_level_pressure": "station_pressure_hpa", "sea_level_pressure": "sea_level_pressure_hpa",
       "wind_speed": "wind_speed_ms"}
A = {"220", "221", "222", "223", "347", "348"}
B = {"313", "314", "315", "322", "335", "343", "344", "346"}
ROUTINE = {"FM15", "FM12", "SAO", "SYSA", "SYMT", "SYAE", "SYAU", "SSA", "SAAU"}
METRICS = ["pc24_hpa", "station_pressure_hpa_change_3h", "temperature_c",
           "temperature_c_change_3h", "dewpoint_c", "wind_speed_ms"]


def qc_tier(source, quality, element):
    """0 excluded/unknown; 1 gross-limits/accepted AWOS; 2 all-checks/good.

    In particular B/4 is gross-limits passed, NOT A/4 (calculated).
    Lowercase integrated failure codes and suspect/error codes are excluded.
    """
    if source in A:
        return 2 if quality == "1" else 0
    if source in B:
        if quality in {"1", "5"}:
            return 2
        if quality in {"0", "4", "9"} or (quality == "C" and element in {"temperature", "dew_point_temperature"}):
            return 1
    return 0


def select_routine(frame, station, year):
    """One coherent routine row/hour; no per-element cherry-picking or specials."""
    frame = frame[frame.DATE.str.startswith(str(year))].copy()
    frame["observation_time_utc"] = pd.to_datetime(frame.DATE, utc=True)
    frame["hour_utc"] = frame.observation_time_utc.dt.floor("h")
    diagnostics = {}
    kind = pd.Series("", index=frame.index)
    for e in MAP:
        for suffix in ["_Report_Type", "_Source_Code", "_Quality_Code"]:
            if e + suffix not in frame:
                frame[e + suffix] = ""
        if e not in frame:
            frame[e] = np.nan
        report = frame[e + "_Report_Type"].fillna("")
        source = frame[e + "_Source_Code"].fillna("")
        quality = frame[e + "_Quality_Code"].fillna("")
        measured = pd.to_numeric(frame[e], errors="coerce")
        measured = measured.where(np.isfinite(measured) & measured.gt(-999))
        if e == "wind_speed":
            measured = measured.where(measured.ge(0))
        if e in {"station_level_pressure", "sea_level_pressure"}:
            measured = measured.where(measured.gt(0))
        tiers = pd.Series([qc_tier(str(s), str(q), e) for s, q in zip(source, quality)], index=frame.index)
        diagnostics[e] = {"source_quality_counts": (source + "/" + quality)[measured.notna()].value_counts().to_dict(),
                          "measured_routine_hours": int(frame.loc[measured.notna() & report.isin(ROUTINE), "hour_utc"].nunique()),
                          "screened_routine_hours_any_row": int(frame.loc[measured.notna() & report.isin(ROUTINE) & tiers.gt(0), "hour_utc"].nunique())}
        frame[MAP[e]] = measured.where(report.isin(ROUTINE) & tiers.gt(0))
        frame[MAP[e] + "_fullqc"] = measured.where(report.isin(ROUTINE) & tiers.eq(2))
        kind = kind.mask(kind.eq("") & report.isin(ROUTINE), report)
    # Prefer FM15 over other routine types; then core completeness, then latest.
    fm15 = pd.concat([frame[e + "_Report_Type"].eq("FM15") for e in MAP], axis=1).any(axis=1)
    frame["priority"] = np.where(fm15, 0, np.where(kind.eq("FM12"), 2, 1))
    frame["core_count"] = frame[["temperature_c", "dewpoint_c", "wind_speed_ms"]].notna().sum(axis=1)
    frame = frame[kind.isin(ROUTINE)].sort_values(["hour_utc", "priority", "core_count", "observation_time_utc"],
                                                 ascending=[True, True, False, False], kind="stable")
    chosen = frame.drop_duplicates("hour_utc").copy()
    chosen["station"] = station
    chosen["source_dataset"] = "GHCNh neighbor audit"
    fields = ["hour_utc", "station", "observation_time_utc", "source_dataset"]
    fields += [c for e in MAP for c in [MAP[e], MAP[e] + "_fullqc"]]
    return chosen[fields], diagnostics


def audit_year(pair):
    station, year = pair
    cached = ROOT / "data/raw/ghcnh" / str(year) / (station + ".parquet")
    path = cached if cached.exists() else OUT / "raw" / f"{station}_{year}.parquet"
    url = f"{BASE}/{year}/parquet/GHCNh_{IDS[station]}_{year}.parquet"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        response = subprocess.run(["curl", "-fLsS", "--max-time", "90", "--retry", "1", url, "-o", str(path)], capture_output=True)
        if response.returncode:
            path.unlink(missing_ok=True)
            error = response.stderr.decode()[:200]
            return None, {"station": station, "year": year, "id": IDS[station], "url": url,
                          "status": "confirmed_no_file" if "404" in error else "unresolved_download_error", "error": error}
    names = pq.ParquetFile(path).schema.names
    columns = ["DATE"] + [e + suffix for e in MAP for suffix in ["", "_Quality_Code", "_Source_Code", "_Report_Type"] if e + suffix in names]
    raw = pq.read_table(path, columns=columns, use_threads=False).to_pandas()
    selected, flags = select_routine(raw, station, year)
    metrics = {"station": station, "year": year, "id": IDS[station], "url": url,
               "status": "read", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "expected_hours": (366 if calendar.isleap(year) else 365) * 24,
               "routine_hours": len(selected), "flags": flags}
    for column in selected.columns:
        if column in MAP.values() or column.endswith("_fullqc"):
            metrics[column + "_hours"] = int(selected[column].notna().sum())
    return selected, metrics


def correlation_row(joined, candidate, metric, mask, sample):
    x, y = joined[metric + "_candidate"], joined[metric + "_PVC"]
    x, y = x[mask], y[mask]
    difference = x - y
    return {"candidate": candidate, "metric": metric, "sample": sample, "paired_hours": int(mask.sum()),
            "pearson_r": x.corr(y) if len(x) >= 500 and x.std() > 0 and y.std() > 0 else np.nan,
            "rmse": float(np.sqrt((difference ** 2).mean())), "mae": float(difference.abs().mean()),
            "mean_candidate_minus_PVC": float(difference.mean())}


def pair_mask(joined, metric, max_minutes=15):
    valid = joined[metric + "_candidate"].notna() & joined[metric + "_PVC"].notna()
    offset = (joined.observation_time_utc_candidate - joined.observation_time_utc_PVC).dt.total_seconds().abs() / 60
    valid &= offset.le(max_minutes)
    if metric == "pc24_hpa":
        prior = (joined.observation_time_24h_ago_utc_candidate - joined.observation_time_24h_ago_utc_PVC).dt.total_seconds().abs() / 60
        valid &= prior.le(max_minutes)
    if metric.endswith("_change_3h") and "observation_time_3h_ago_utc_candidate" in joined:
        prior = (joined.observation_time_3h_ago_utc_candidate - joined.observation_time_3h_ago_utc_PVC).dt.total_seconds().abs() / 60
        valid &= prior.le(max_minutes)
    return valid


def compare(signals, metrics):
    pvc = signals[signals.station.eq("PVC")].set_index("hour_utc")
    joined = {station: signals[signals.station.eq(station)].set_index("hour_utc").join(pvc, lsuffix="_candidate", rsuffix="_PVC")
              for station in IDS if station != "PVC"}
    rows, common = [], {}
    for metric in metrics:
        masks = {station: pair_mask(pair, metric) for station, pair in joined.items()}
        shared = pd.concat(masks.values(), axis=1).all(axis=1)
        common[metric] = shared
        for station, pair in joined.items():
            rows.append(correlation_row(pair, station, metric, masks[station], "pairwise"))
            rows.append(correlation_row(pair, station, metric, shared, "common_all_four"))
    return pd.DataFrame(rows), joined, common


def weekly_bootstrap(joined, common, metric="pc24_hpa", repetitions=1000):
    """Paired, nonoverlapping 7-day block resampling of common-hour correlations."""
    mask = common[metric]
    if mask.sum() < 500:
        return pd.DataFrame()
    origin = mask.index.min().value
    moments = {}
    for station, pair in joined.items():
        x, y = pair.loc[mask, metric + "_candidate"], pair.loc[mask, metric + "_PVC"]
        block = (x.index.asi8 - origin) // (7 * 24 * 3_600_000_000_000)
        moments[station] = pd.DataFrame({"n": 1., "x": x, "y": y, "xx": x*x, "yy": y*y, "xy": x*y}).groupby(block).sum()
    index = sorted(set().union(*(set(m.index) for m in moments.values())))
    rng = np.random.default_rng(20261014)
    weights = rng.multinomial(len(index), np.repeat(1 / len(index), len(index)), size=repetitions)
    samples, rows = {}, []
    for station, sums in moments.items():
        total = weights @ sums.reindex(index, fill_value=0).to_numpy()
        n, x, y, xx, yy, xy = total.T
        r = (xy - x*y/n) / np.sqrt((xx-x*x/n)*(yy-y*y/n))
        samples[station] = r
        rows.append({"candidate": station, "metric": metric, "common_paired_hours": int(mask.sum()),
                     "weekly_blocks": len(index), "r_ci_low": float(np.quantile(r, .025)),
                     "r_ci_high": float(np.quantile(r, .975)),
                     "HYA_minus_candidate_r_ci_low": np.nan, "HYA_minus_candidate_r_ci_high": np.nan})
    for row in rows:
        if row["candidate"] != "HYA":
            difference = samples["HYA"] - samples[row["candidate"]]
            row["HYA_minus_candidate_r_ci_low"] = float(np.quantile(difference, .025))
            row["HYA_minus_candidate_r_ci_high"] = float(np.quantile(difference, .975))
    return pd.DataFrame(rows)


def temperature_review_flags(frame):
    """Broad, station-independent coastal-MA bounds for sensitivity, not homogenization.

    This extra screen is post-hoc after suspicious readings were noticed. Raw
    QC-screened results remain available. No use of PVC/candidate differences.
    """
    value = frame.temperature_c
    warm = frame.hour_utc.dt.month.between(5, 9)
    return value.notna() & (value.lt(-35) | value.gt(45) | (warm & value.lt(-15)))


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    annual, recent = [], []
    jobs = [(station, year) for station in IDS for year in range(2005, 2025)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(audit_year, pair) for pair in jobs]
        for count, future in enumerate(as_completed(futures), 1):
            frame, result = future.result()
            annual.append(result)
            if frame is not None and result["year"] >= 2019:
                recent.append(frame)
            if count % 10 == 0 or result["status"] != "read":
                print(f"AUDIT {count}/100: {result['station']} {result['year']} {result['status']}", flush=True)
    (OUT / "annual_audit.json").write_text(json.dumps(sorted(annual, key=lambda r:(r["station"], r["year"])), indent=2))
    coverage = pd.DataFrame([{k:v for k,v in row.items() if k != "flags"} for row in annual])
    coverage["expected_hours"] = coverage.year.map(lambda y:(366 if calendar.isleap(y) else 365)*24)
    for field in ["routine"] + list(MAP.values()):
        column = field + "_hours"
        coverage[column] = coverage[column].fillna(0)
        coverage[field + "_pct"] = 100 * coverage[column] / coverage.expected_hours
    coverage.to_csv(OUT / "annual_coverage.csv", index=False)
    observations = pd.concat(recent, ignore_index=True)
    hourly = align_hourly(observations, list(IDS), "2019-01-01T00:00Z", "2025-01-01T00:00Z")
    hourly = add_pc24(hourly)
    hourly["temperature_review_flag"] = temperature_review_flags(hourly)
    hourly[hourly.temperature_review_flag][["station", "hour_utc", "observation_time_utc", "temperature_c"]].to_csv(
        OUT / "temperature_review_flags.csv", index=False)
    reference = temperature_reference(hourly[hourly.hour_utc.ge(pd.Timestamp("2020-01-01T00:00Z")) &
                                              hourly.hour_utc.lt(pd.Timestamp("2024-01-01T00:00Z"))])
    signals = add_reference_and_changes(hourly, reference)
    signals["observation_time_3h_ago_utc"] = signals.groupby("station").observation_time_utc.shift(3)
    signals = signals[signals.hour_utc.ge(pd.Timestamp("2020-01-01T00:00Z"))].copy()
    signals.to_parquet(OUT / "comparison_hourly.parquet", index=False)
    correlations, joined, common = compare(signals, METRICS)
    correlations.to_csv(OUT / "correlations_2020_2024.csv", index=False)
    pc24_points = pd.DataFrame({station: pair.loc[common["pc24_hpa"], "pc24_hpa_candidate"]
                               for station, pair in joined.items()})
    pc24_points["PVC"] = joined["HYA"].loc[common["pc24_hpa"], "pc24_hpa_PVC"]
    pc24_points.to_csv(OUT / "pc24_common_hours.csv")
    yearly = []
    for year in range(2020, 2025):
        selected = signals[signals.hour_utc.dt.year.eq(year)]
        table, _, _ = compare(selected, METRICS + (["temperature_anomaly_c"] if year == 2024 else []))
        table["year"] = year
        yearly.append(table)
    pd.concat(yearly, ignore_index=True).to_csv(OUT / "correlations_by_year.csv", index=False)
    for metric in ["pc24_hpa", "station_pressure_hpa_change_3h"]:
        weekly_bootstrap(joined, common, metric).to_csv(OUT / f"bootstrap_{metric}.csv", index=False)
    reviewed = hourly.copy()
    reviewed.loc[reviewed.temperature_review_flag, "temperature_c"] = np.nan
    sensitivity_reference = temperature_reference(reviewed[reviewed.hour_utc.ge(pd.Timestamp("2020-01-01T00:00Z")) &
                                                            reviewed.hour_utc.lt(pd.Timestamp("2024-01-01T00:00Z"))])
    sensitivity = add_reference_and_changes(reviewed, sensitivity_reference)
    sensitivity["observation_time_3h_ago_utc"] = sensitivity.groupby("station").observation_time_utc.shift(3)
    sensitivity = sensitivity[sensitivity.hour_utc.ge(pd.Timestamp("2020-01-01T00:00Z"))].copy()
    sensitivity_table, _, _ = compare(sensitivity, ["temperature_c", "temperature_c_change_3h"])
    sensitivity_table.to_csv(OUT / "temperature_sensitivity_2020_2024.csv", index=False)
    sensitivity_2024, temp_joined, temp_common = compare(sensitivity[sensitivity.hour_utc.dt.year.eq(2024)], ["temperature_c", "temperature_anomaly_c", "temperature_c_change_3h"])
    sensitivity_2024.to_csv(OUT / "temperature_sensitivity_2024.csv", index=False)
    weekly_bootstrap(temp_joined, temp_common, "temperature_anomaly_c").to_csv(OUT / "bootstrap_temperature_anomaly_2024.csv", index=False)
    # Source-sensitivity check only: the production database remains untouched.
    from eda_utils import database_engine
    from weather_events import load_event_hours
    engine = database_engine()
    try:
        production = load_event_hours(engine, ["HYA", "PYM", "PVC"], "2023-12-31T00:00Z", "2025-01-01T00:00Z")
    finally:
        engine.dispose()
    production = add_pc24(production)
    production = production[production.hour_utc.ge(pd.Timestamp("2024-01-01T00:00Z"))]
    sources = []
    for label, frame in [("production_LCDv1", production), ("NOAA_GHCNh_audit", signals[signals.hour_utc.dt.year.eq(2024)])]:
        table = frame.groupby("station").agg(expected_hours=("hour_utc", "size"), pressure_hours=("station_pressure_hpa", "count"), pc24_hours=("pc24_hpa", "count"))
        table["pressure_pct"] = 100 * table.pressure_hours / table.expected_hours
        table["pc24_pct"] = 100 * table.pc24_hours / table.expected_hours
        table["source"] = label
        sources.append(table.reset_index())
    pd.concat(sources, ignore_index=True).to_csv(OUT / "archive_vs_production_2024.csv", index=False)
    unresolved = [r for r in annual if r["status"] == "unresolved_download_error"]
    print("COMPLETE", len(annual), "station-years; unresolved:", len(unresolved), flush=True)
    print(correlations[correlations.metric.eq("pc24_hpa")].round(4).to_string(index=False), flush=True)
    if unresolved:
        raise RuntimeError("Some downloads are unresolved; do not call the history audit complete")


if __name__ == "__main__":
    run()
