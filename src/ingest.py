"""Incrementally ingest every cleaned station-year CSV into PostgreSQL."""

from pathlib import Path
import os
from typing import Dict, List

import pandas as pd
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine

from file_utils import WeatherDataFile, discover_weather_files


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

COLUMN_RENAMES = {
    "DATE": "datetime",
    "REPORT_TYPE": "report_type",
    "HourlyDryBulbTemperature": "temperature",
    "HourlyDewPointTemperature": "dewpoint",
    "HourlyRelativeHumidity": "relative_humidity",
    "HourlyPrecipitation": "precipitation",
    "HourlySkyConditions": "sky_conditions",
    "HourlyStationPressure": "station_pressure",
    "HourlyWindDirection": "wind_direction",
    "HourlyWindSpeed": "wind_speed",
    "HourlyWindGustSpeed": "wind_gust",
}

DATABASE_COLUMNS = [
    "datetime",
    "station",
    "report_type",
    "temperature",
    "dewpoint",
    "relative_humidity",
    "precipitation",
    "sky_conditions",
    "station_pressure",
    "wind_direction",
    "wind_speed",
    "wind_gust",
]

INSERT_SQL = text(
    '''
    INSERT INTO "weather_observations" (
        "datetime",
        "station",
        "report_type",
        "temperature",
        "dewpoint",
        "relative_humidity",
        "precipitation",
        "sky_conditions",
        "station_pressure",
        "wind_direction",
        "wind_speed",
        "wind_gust"
    )
    VALUES (
        :datetime,
        :station,
        :report_type,
        :temperature,
        :dewpoint,
        :relative_humidity,
        :precipitation,
        :sky_conditions,
        :station_pressure,
        :wind_direction,
        :wind_speed,
        :wind_gust
    )
    ON CONFLICT ("datetime", "station") DO UPDATE SET
        "report_type" = EXCLUDED."report_type",
        "temperature" = EXCLUDED."temperature",
        "dewpoint" = EXCLUDED."dewpoint",
        "relative_humidity" = EXCLUDED."relative_humidity",
        "precipitation" = EXCLUDED."precipitation",
        "sky_conditions" = EXCLUDED."sky_conditions",
        "station_pressure" = EXCLUDED."station_pressure",
        "wind_direction" = EXCLUDED."wind_direction",
        "wind_speed" = EXCLUDED."wind_speed",
        "wind_gust" = EXCLUDED."wind_gust"
    WHERE "weather_observations"."source_dataset" = 'LCDv1';
    '''
)

REGISTER_STATION_SQL = text(
    '''
    INSERT INTO "station_metadata" ("station", "minute_offset")
    VALUES (:station, :minute_offset)
    ON CONFLICT ("station") DO NOTHING;
    '''
)

STATION_MINUTE_SQL = text(
    'SELECT "minute_offset" FROM "station_metadata" WHERE "station" = :station'
)


def build_engine() -> Engine:
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER") or os.getenv("USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "metpipe_northeast"),
    )
    return create_engine(database_url)


def prepare_records(weather_file: WeatherDataFile) -> List[Dict[str, object]]:
    """Transform one cleaned CSV into database-ready records."""
    frame = pd.read_csv(weather_file.path).rename(columns=COLUMN_RENAMES)

    missing_columns = sorted(set(COLUMN_RENAMES.values()) - set(frame.columns))
    if missing_columns:
        raise ValueError(
            f"{weather_file.path.name} is missing columns: "
            f"{', '.join(missing_columns)}"
        )

    frame["station"] = weather_file.station
    frame["report_type"] = frame["report_type"].astype("string").str.strip()
    frame["datetime"] = pd.to_datetime(frame["datetime"], errors="coerce")
    frame["precipitation"] = frame["precipitation"].replace("T", "0.001")
    frame["precipitation"] = pd.to_numeric(
        frame["precipitation"],
        errors="coerce",
    )
    frame = frame.dropna(subset=["datetime"])
    frame["_regular_report"] = frame["report_type"].eq("FM-15").fillna(False)
    frame = frame.sort_values("_regular_report", ascending=False, kind="stable")
    frame = frame.drop_duplicates(subset=["datetime", "station"])

    observed_years = set(frame["datetime"].dt.year.unique())
    if observed_years and observed_years != {weather_file.year}:
        raise ValueError(
            f"{weather_file.path} contains years {sorted(observed_years)}; "
            f"expected only {weather_file.year}."
        )

    database_frame = frame[DATABASE_COLUMNS].astype(object)
    database_frame = database_frame.where(pd.notna(database_frame), None)
    return database_frame.to_dict(orient="records")


def main() -> None:
    cleaned_files = discover_weather_files(DATA_DIR, cleaned=True)
    if not cleaned_files:
        raise FileNotFoundError(
            f"No cleaned files matching "
            f"<station>_hourly_<year>_cleaned.csv in {DATA_DIR}"
        )

    engine = build_engine()
    total_records = 0

    try:
        with engine.begin() as connection:
            for weather_file in cleaned_files:
                records = prepare_records(weather_file)
                if records:
                    minute_counts = pd.Series(
                        [record["datetime"].minute for record in records]
                    ).value_counts()
                    connection.execute(
                        REGISTER_STATION_SQL,
                        {
                            "station": weather_file.station,
                            "minute_offset": int(minute_counts.index[0]),
                        },
                    )
                    stored_minute = connection.execute(
                        STATION_MINUTE_SQL,
                        {"station": weather_file.station},
                    ).scalar_one()
                    observed_minute = int(minute_counts.index[0])
                    if stored_minute != observed_minute:
                        raise ValueError(
                            f"{weather_file.station} {weather_file.year} most often "
                            f"reports at :{observed_minute:02d}, but station_metadata "
                            f"specifies :{stored_minute:02d}. Review the raw "
                            "report types and station schedule before ingesting."
                        )
                    connection.execute(INSERT_SQL, records)

                total_records += len(records)
                print(
                    f"Ingested {weather_file.station} {weather_file.year}: "
                    f"{len(records):,} record(s) processed."
                )
    finally:
        engine.dispose()
    print(
        f"Ingestion complete: {len(cleaned_files)} station-year file(s), "
        f"{total_records:,} record(s) processed."
    )


if __name__ == "__main__":
    main()
