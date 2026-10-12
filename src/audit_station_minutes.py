"""Report the regular hourly observation minute and coverage by station-year."""

from calendar import isleap
from collections import defaultdict
from pathlib import Path

import pandas as pd

from file_utils import discover_weather_files


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def audit_file(weather_file):
    frame = pd.read_csv(
        weather_file.path,
        usecols=["STATION", "DATE", "REPORT_TYPE"],
        low_memory=False,
    )
    station_ids = frame["STATION"].dropna().astype(str).unique()
    if len(station_ids) != 1:
        raise ValueError(f"{weather_file.path} has {len(station_ids)} station IDs")

    times = pd.to_datetime(frame["DATE"], errors="coerce")
    regular = frame["REPORT_TYPE"].astype(str).str.strip() == "FM-15"
    regular_times = times[regular].dropna()
    if regular_times.empty:
        raise ValueError(f"{weather_file.path} has no FM-15 hourly reports")
    years = set(regular_times.dt.year.unique())
    if years != {weather_file.year}:
        raise ValueError(f"{weather_file.path} has FM-15 reports in {sorted(years)}")

    minute_counts = regular_times.dt.minute.value_counts()
    minute = int(minute_counts.index[0])
    scheduled_times = regular_times[regular_times.dt.minute == minute]
    hours = scheduled_times.dt.floor("h").nunique()
    expected_hours = 8784 if isleap(weather_file.year) else 8760
    return str(station_ids[0]), minute, hours, expected_hours


def main():
    files = discover_weather_files(RAW_DATA_DIR, cleaned=False)
    minutes_by_station = defaultdict(set)
    print("year station NOAA_ID minute scheduled_hours expected_hours coverage_pct")
    for weather_file in files:
        station_id, minute, hours, expected_hours = audit_file(weather_file)
        minutes_by_station[weather_file.station].add(minute)
        print(
            f"{weather_file.year} {weather_file.station} {station_id} "
            f":{minute:02d} {hours} {expected_hours} "
            f"{hours / expected_hours * 100:.1f}"
        )

    drifting = {
        station: sorted(minutes)
        for station, minutes in minutes_by_station.items()
        if len(minutes) > 1
    }
    if drifting:
        raise ValueError(f"Hourly minute changes by year: {drifting}")


if __name__ == "__main__":
    main()
