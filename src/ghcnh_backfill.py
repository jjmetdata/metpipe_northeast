"""Source-aware, non-destructive GHCNh backfill into the legacy-compatible table.

GHCNh UTC/SI records are converted to fixed UTC-5 local standard time and
US customary units, matching the existing LCDv1 table. UTC, per-element flags,
coded cloud data and downloaded Parquet sources are retained independently.
"""
import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import psycopg2
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year"
STATIONS = {"BOS":"14739", "PVD":"14765", "ALB":"14735", "JFK":"94789", "ORH":"94746",
            "PVC":"64708", "EWB":"94726", "HYA":"94720", "MVY":"94724", "PYM":"54769",
            "BAF":"14775", "BDL":"14740", "HVN":"14758", "UUU":"14787", "BTV":"14742",
            "DDH":"54781", "MHT":"14710", "LEB":"94765", "PWM":"14764", "AUG":"14605"}
NUMERIC = ["temperature", "dew_point_temperature", "relative_humidity", "precipitation",
           "station_level_pressure", "wind_direction", "wind_speed", "wind_gust"]
CORE = ["temperature", "dew_point_temperature", "wind_speed"]
REGULAR = ["FM15", "SAO", "SYSA", "SYMT", "SYAE", "SYAU", "SSA", "SAAU", "FM12"]
TYPE_MAP = {"FM15":"FM-15", "FM16":"FM-16", "FM12":"FM-12", "SYSA":"SY-SA"}
A = {"220", "221", "222", "223", "347", "348"}
B = {"313", "314", "315", "322", "335", "343", "344", "346"}
INHG_HPA = 33.8638866667
MS_MPH = 2.2369362921
COLUMNS = ["datetime", "station", "report_type", "temperature", "dewpoint", "relative_humidity",
           "precipitation", "sky_conditions", "station_pressure", "wind_direction", "wind_speed", "wind_gust",
           "datetime_utc", "source_dataset", "source_file_year", "source_metadata", "precipitation_trace"]


def scalar(value):
    if value is None or pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    return value


def metadata(row, field):
    return {key: scalar(row.get(field + suffix)) for key, suffix in
            [("s", "_Source_Code"), ("q", "_Quality_Code"), ("m", "_Measurement_Code"),
             ("r", "_Report_Type"), ("sid", "_Source_Station_ID")]
            if scalar(row.get(field + suffix)) is not None}


def rejected(field, flags):
    source, quality = str(flags.get("s", "")), str(flags.get("q", ""))
    if any(c.islower() for c in quality):
        return True  # GHCNh failed integrated QC test codes.
    if source in A and quality in {"2", "3", "5"}:
        return True
    if source in B and quality in {"2", "3", "6", "7"}:
        return True
    if field == "precipitation" and source == "382" and quality in {"X", "N", "Y", "K", "G", "O", "Z", "A", "M", "D", "Q"}:
        return True
    return False


def number(row, field, flags):
    value = scalar(row.get(field))
    if flags.get("r") in {"NSRDB", "SOD", "SOM"}:
        return None  # Synthetic and summary fields are not point observations.
    if value is None or rejected(field, flags):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value) or value <= -999:
        return None
    if field == "relative_humidity" and not 0 <= value <= 100:
        return None
    if field in {"wind_speed", "wind_gust", "precipitation"} and value < 0:
        return None
    return value


def report_type(row):
    types = [str(row.get(e + "_Report_Type", "") or "") for e in CORE]
    types += [str(row.get(e + "_Report_Type", "") or "") for e in NUMERIC]
    for code in REGULAR:
        if code in types:
            return TYPE_MAP.get(code, code)
    for code in ["FM16", "SAOSP", "PCP60", "PCP15"]:
        if code in types:
            return TYPE_MAP.get(code, code)
    return next((TYPE_MAP.get(t, t) for t in types if t and t != "nan"), None)


def transform(row, station, source_year):
    utc = datetime.fromisoformat(str(row["DATE"]).replace("Z", "+00:00"))
    if utc.tzinfo is None:
        utc = utc.replace(tzinfo=timezone.utc)
    else:
        utc = utc.astimezone(timezone.utc)
    local = (utc - timedelta(hours=5)).replace(tzinfo=None)
    flags = {e: metadata(row, e) for e in NUMERIC}
    values = {e: number(row, e, flags[e]) for e in NUMERIC}
    kind = report_type(row)
    if kind in {"SOD", "SOM", "NSRDB"}:
        return None
    sky = {k: scalar(v) for k, v in row.items()
           if (k.startswith("sky_") or k.startswith("ceiling_height")) and scalar(v) is not None}
    if not any(v is not None for v in values.values()) and not sky:
        return None
    raw_flags = {e: dict(f, raw=scalar(row.get(e))) for e, f in flags.items()
                 if scalar(row.get(e)) is not None or f}
    cloud_code = scalar(row.get("sky_condition"))
    if cloud_code is None:
        cloud_code = next((scalar(row.get(k)) for k in ["sky_cover_summation_1", "sky_cover_layer_1", "sky_cover_1"]
                           if scalar(row.get(k)) is not None), None)
    sky_text = ("GHCNh:" + str(cloud_code))[:50] if cloud_code is not None else None
    precipitation = values["precipitation"]
    pflags = flags["precipitation"]
    trace = (str(pflags.get("m", "")) == "T" or
             (str(pflags.get("m", "")) == "2" and str(pflags.get("s", "")) in A | B))
    # Only scheduled METAR hourly amounts enter the compatibility precipitation
    # field. Specials and accumulation windows remain in source_metadata/raw file.
    if pflags.get("r") not in {"FM15", "FM-15"} or str(pflags.get("m", "")) in {"3", "4", "5", "6", "7", "8", "I", "J", "E"}:
        precipitation = None
    if trace and precipitation is not None:
        precipitation = 0.0  # Trace is a flag, not an invented numeric rainfall amount.
    direction = values["wind_direction"]
    direction = "%03d" % int(direction) if direction is not None and 0 <= direction <= 360 else None
    if (flags["wind_direction"].get("m") == "V"
            and flags["wind_direction"].get("r") not in {"NSRDB", "SOD", "SOM"}
            and not rejected("wind_direction", flags["wind_direction"])):
        direction = "VRB"
    return {
        "datetime": local, "datetime_utc": utc, "station": station,
        "report_type": kind,
        "temperature": values["temperature"] * 1.8 + 32 if values["temperature"] is not None else None,
        "dewpoint": values["dew_point_temperature"] * 1.8 + 32 if values["dew_point_temperature"] is not None else None,
        "relative_humidity": values["relative_humidity"],
        "precipitation": precipitation / 25.4 if precipitation is not None else None,
        "precipitation_trace": trace if precipitation is not None else None,
        "sky_conditions": sky_text,
        "station_pressure": values["station_level_pressure"] / INHG_HPA if values["station_level_pressure"] is not None else None,
        "wind_direction": direction,
        "wind_speed": values["wind_speed"] * MS_MPH if values["wind_speed"] is not None else None,
        "wind_gust": values["wind_gust"] * MS_MPH if values["wind_gust"] is not None else None,
        "source_dataset": "GHCNh", "source_file_year": source_year,
        "source_metadata": {"id": "USW000" + STATIONS[station], "units": "SI", "fields": raw_flags, "sky": sky},
    }


def download(pair, raw_dir):
    station, year = pair
    sid = "USW000" + STATIONS[station]
    path = raw_dir / str(year) / (station + ".parquet")
    path.parent.mkdir(parents=True, exist_ok=True)
    url = "%s/%s/parquet/GHCNh_%s_%s.parquet" % (BASE, year, sid, year)
    if not path.exists():
        temp = path.with_suffix(".partial")
        p = subprocess.run(["curl", "-fLsS", "--max-time", "120", "--retry", "2", url, "-o", str(temp)], capture_output=True)
        if p.returncode:
            if temp.exists():
                temp.unlink()
            raise RuntimeError("%s %s download failed: %s" % (station, year, p.stderr.decode()[:250]))
        pq.ParquetFile(temp)  # Validate before publishing the raw file.
        temp.replace(path)
    return station, year, path, url, hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(path, station, source_year, start, end):
    names = pq.ParquetFile(path).schema.names
    columns = [k for k in names if k in {"STATION", "DATE"}
               or k.startswith("sky_") or k.startswith("ceiling_height")
               or any(k == e or k.startswith(e + "_") for e in NUMERIC)]
    table = pq.read_table(path, columns=columns)
    if "STATION" in table.column_names:
        ids = set(table.column("STATION").to_pylist())
        if ids != {"USW000" + STATIONS[station]}:
            raise ValueError("Station identity mismatch: %s" % ids)
    data = table.to_pandas()
    dates = pd.to_datetime(data["DATE"], utc=True, errors="raise")
    if set(dates.dt.year) != {source_year}:
        raise ValueError("Source file contains unexpected UTC years")
    local = dates.dt.tz_convert("Etc/GMT+5").dt.tz_localize(None)
    data = data[(local >= start) & (local < end)]
    records = [r for r in (transform(row, station, source_year) for row in data.to_dict("records")) if r is not None]
    # One harmonized source point per exact time. Never average duplicates.
    records.sort(key=lambda r: (r["report_type"] != "FM-15", -sum(r[e] is not None for e in ["temperature", "dewpoint", "wind_speed"])))
    unique = {}
    for r in records:
        unique.setdefault(r["datetime"], r)
    return sorted(unique.values(), key=lambda r: r["datetime"])


def checkpoint(connection, station, year, digest, start, end):
    with connection.cursor() as cursor:
        cursor.execute("SELECT source_sha256, imported_rows FROM ghcnh_ingestion_files WHERE station=%s AND source_year=%s AND local_start=%s AND local_end=%s", (station, year, start, end))
        previous = cursor.fetchone()
        if previous and previous[0] == digest:
            return previous[1]
    return None


def ingest(connection, station, year, path, url, digest, records, start, end):
    previous = checkpoint(connection, station, year, digest, start, end)
    if previous is not None:
        return previous, "unchanged"
    with connection.cursor() as cursor:
        cursor.execute("CREATE TEMP TABLE ghcnh_stage (LIKE weather_observations INCLUDING DEFAULTS) ON COMMIT DROP")
        stream = io.StringIO()
        writer = csv.writer(stream)
        for r in records:
            writer.writerow([json.dumps(r[c], separators=(",", ":"), allow_nan=False) if c == "source_metadata"
                             else r[c].isoformat() if isinstance(r[c], datetime)
                             else "\\N" if r[c] is None else r[c] for c in COLUMNS])
        stream.seek(0)
        cursor.copy_expert("COPY ghcnh_stage (%s) FROM STDIN WITH (FORMAT CSV, NULL '\\N')" % ",".join(COLUMNS), stream)
        update = ",".join('"%s"=EXCLUDED."%s"' % (c, c) for c in COLUMNS if c not in {"datetime", "station"})
        cursor.execute("INSERT INTO weather_observations (%s) SELECT %s FROM ghcnh_stage ON CONFLICT (datetime,station) DO UPDATE SET %s WHERE weather_observations.source_dataset='GHCNh' AND weather_observations.datetime >= %%s AND weather_observations.datetime < %%s" % (",".join(COLUMNS), ",".join(COLUMNS), update), (start, end))
        affected = cursor.rowcount
        cursor.execute("INSERT INTO ghcnh_ingestion_files (station,source_year,local_start,local_end,source_url,source_sha256,imported_rows) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (station,source_year,local_start,local_end) DO UPDATE SET source_url=EXCLUDED.source_url,source_sha256=EXCLUDED.source_sha256,imported_rows=EXCLUDED.imported_rows,ingested_at=now()", (station, year, start, end, url, digest, len(records)))
    connection.commit()
    return affected, "ingested"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2005)
    parser.add_argument("--end", type=int, default=2019, help="Inclusive local-standard-time year")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--download-only", action="store_true")
    parser.add_argument("--stations", nargs="+", choices=sorted(STATIONS), default=sorted(STATIONS))
    args = parser.parse_args()
    if not 2005 <= args.start <= args.end < 2020:
        raise ValueError("This preservation backfill is restricted to 2005–2019")
    start, end = datetime(args.start, 1, 1), datetime(args.end + 1, 1, 1)
    raw_dir = ROOT / "data/raw/ghcnh"
    jobs = [(s, y) for s in args.stations for y in range(args.start, args.end + 2)]
    sources = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for n, job in enumerate(as_completed([pool.submit(download, pair, raw_dir) for pair in jobs]), 1):
            sources.append(job.result())
            if n % 20 == 0:
                print("DOWNLOADED", n, "of", len(jobs), flush=True)
    if args.download_only:
        print("Raw sources ready:", len(sources))
        return
    connection = psycopg2.connect(host=os.getenv("DB_HOST", "localhost"), port=os.getenv("DB_PORT", "5432"),
                                  database=os.getenv("DB_NAME", "metpipe_northeast"),
                                  user=os.getenv("DB_USER") or os.getenv("USER"), password=os.getenv("DB_PASSWORD"))
    try:
        with connection.cursor() as cursor:
            cursor.execute((ROOT / "sql/schema.sql").read_text())
        connection.commit()
        total = 0
        for n, (station, year, path, url, digest) in enumerate(sorted(sources), 1):
            count = checkpoint(connection, station, year, digest, start, end)
            if count is None:
                records = prepare(path, station, year, start, end)
                count, state = ingest(connection, station, year, path, url, digest, records, start, end)
            else:
                state = "unchanged"
            total += count
            print("%s %s: %s %s rows (%s/%s files)" % (station, year, state, count, n, len(sources)), flush=True)
        print("COMPLETE", total, "processed rows", flush=True)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
