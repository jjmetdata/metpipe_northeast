"""Small, read-only station extracts that preserve actual times and gaps."""
import pandas as pd
from sqlalchemy import bindparam, text


def utc_hour(value):
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        raise ValueError("Window boundaries must have an explicit time zone")
    timestamp = timestamp.tz_convert("UTC")
    if timestamp != timestamp.floor("h"):
        raise ValueError("Window boundaries must be aligned to whole UTC hours")
    return timestamp


def align_hourly(records, stations, start, end):
    """Expected-hour scaffold; do not fabricate temperatures or report times."""
    start, end = utc_hour(start), utc_hour(end)
    if end <= start or len(stations) < 2 or len(set(stations)) != len(stations):
        raise ValueError("Choose at least two distinct stations and an increasing window")
    frame = records.copy()
    frame["hour_utc"] = pd.to_datetime(frame["hour_utc"], utc=True)
    frame["observation_time_utc"] = pd.to_datetime(frame["observation_time_utc"], utc=True)
    if frame.duplicated(["station","hour_utc"]).any():
        raise ValueError("More than one selected report in a station-hour")
    if not set(frame["station"]).issubset(stations):
        raise ValueError("Unexpected station in extract")
    if not frame["hour_utc"].between(start,end,inclusive="left").all():
        raise ValueError("Observation outside selected window")
    if (frame["observation_time_utc"].isna().any() or
            not frame["observation_time_utc"].dt.floor("h").eq(frame["hour_utc"]).all()):
        raise ValueError("Actual report times must belong to their UTC hour buckets")
    frame["has_report"] = True
    hours = pd.date_range(start,end,freq="h",inclusive="left")
    expected = pd.MultiIndex.from_product([hours,stations],names=["hour_utc","station"])
    result = frame.set_index(["hour_utc","station"]).reindex(expected).reset_index()
    result["has_report"] = result["has_report"].eq(True)
    return result


def load_hourly_pair(engine, stations, start, end):
    start, end = utc_hour(start), utc_hour(end)
    statement = text("""SELECT datetime_utc AS hour_utc, station,
        observation_datetime_utc AS observation_time_utc, temperature_c, source_dataset
        FROM weather_hourly_utc WHERE station IN :stations
        AND datetime_utc >= :start AND datetime_utc < :end
        ORDER BY datetime_utc, station""").bindparams(bindparam("stations",expanding=True))
    with engine.connect() as connection:
        if connection.execute(text("SELECT current_setting('transaction_read_only')")).scalar() != "on":
            raise ValueError("Use the read-only database engine")
        records = pd.read_sql_query(statement,connection,
                                    params={"stations":list(stations),"start":start.to_pydatetime(),"end":end.to_pydatetime()})
    return align_hourly(records,stations,start,end)


def coverage_stats(hourly):
    summary = hourly.groupby("station").agg(
        expected_hours=("hour_utc","size"),
        selected_reports=("has_report","sum"),
        valid_temperature_hours=("temperature_c","count"),
        temperature_mean_c=("temperature_c","mean"),
        temperature_median_c=("temperature_c","median"),
        temperature_min_c=("temperature_c","min"),
        temperature_max_c=("temperature_c","max"))
    summary["missing_report_hours"] = summary["expected_hours"] - summary["selected_reports"]
    summary["reports_without_temperature"] = summary["selected_reports"] - summary["valid_temperature_hours"]
    summary["temperature_coverage_pct"] = 100 * summary["valid_temperature_hours"] / summary["expected_hours"]
    return summary


def contiguous_temperature_segments(frame):
    """Do not draw a continuous line across absent reports or missing values."""
    valid = frame.sort_values("hour_utc").dropna(subset=["temperature_c","observation_time_utc"])
    starts = valid["hour_utc"].diff().dt.total_seconds().ne(3600)
    return [group for _,group in valid.groupby(starts.cumsum())]
