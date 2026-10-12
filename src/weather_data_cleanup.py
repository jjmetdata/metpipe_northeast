"""Clean every station-year NOAA CSV found in the raw-data directory."""

from pathlib import Path

import pandas as pd

from file_utils import WeatherDataFile, discover_weather_files


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

SELECTED_COLUMNS = [
    "DATE",
    "REPORT_TYPE",
    "HourlyDryBulbTemperature",
    "HourlyDewPointTemperature",
    "HourlyRelativeHumidity",
    "HourlyPrecipitation",
    "HourlySkyConditions",
    "HourlyStationPressure",
    "HourlyWindDirection",
    "HourlyWindSpeed",
    "HourlyWindGustSpeed",
]

NUMERIC_COLUMNS = [
    "HourlyDryBulbTemperature",
    "HourlyDewPointTemperature",
    "HourlyRelativeHumidity",
    "HourlyPrecipitation",
    "HourlyStationPressure",
    "HourlyWindSpeed",
    "HourlyWindGustSpeed",
]


def clean_weather_file(weather_file: WeatherDataFile) -> Path:
    """Clean one raw station-year file and return its output path."""
    print(f"Reading {weather_file.path.name}...")
    frame = pd.read_csv(
        weather_file.path,
        usecols=SELECTED_COLUMNS,
        low_memory=False,
    )[SELECTED_COLUMNS].copy()

    frame["HourlyPrecipitation"] = frame["HourlyPrecipitation"].replace(
        "T", "0.001"
    )
    frame[NUMERIC_COLUMNS] = frame[NUMERIC_COLUMNS].astype(str).apply(
        lambda column: column.str.replace(r"s$", "", regex=True)
    )
    frame[NUMERIC_COLUMNS] = frame[NUMERIC_COLUMNS].apply(
        pd.to_numeric,
        errors="coerce",
    )
    frame["DATE"] = pd.to_datetime(frame["DATE"], errors="coerce")

    observed_years = set(frame["DATE"].dropna().dt.year.unique())
    if observed_years and observed_years != {weather_file.year}:
        raise ValueError(
            f"{weather_file.path} contains years {sorted(observed_years)}; "
            f"expected only {weather_file.year}. Split the source by year first."
        )

    output_directory = PROCESSED_DATA_DIR / str(weather_file.year)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / f"{weather_file.path.stem}_cleaned.csv"
    frame.to_csv(output_path, index=False)

    print(
        f"Cleaned {weather_file.station} {weather_file.year}: "
        f"{len(frame):,} rows -> {output_path.name}"
    )
    return output_path


def main() -> None:
    raw_files = discover_weather_files(RAW_DATA_DIR, cleaned=False)
    if not raw_files:
        raise FileNotFoundError(
            f"No raw files matching <station>_hourly_<year>.csv in {RAW_DATA_DIR}"
        )

    for weather_file in raw_files:
        clean_weather_file(weather_file)

    print(f"Cleaning complete: {len(raw_files)} station-year file(s) processed.")


if __name__ == "__main__":
    main()
