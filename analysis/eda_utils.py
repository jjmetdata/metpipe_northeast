"""Read-only database extracts and missingness-aware descriptive EDA helpers."""
import os

import numpy as np
import pandas as pd
from sqlalchemy import URL, create_engine, text

FIELDS = ["temperature_c", "dewpoint_c", "relative_humidity", "wind_speed_ms", "station_pressure_hpa"]
UNITS = {"temperature_c":"°C", "dewpoint_c":"°C", "relative_humidity":"%",
         "wind_speed_ms":"m/s", "station_pressure_hpa":"hPa"}
SI = {"temperature_c":"(temperature - 32) / 1.8", "dewpoint_c":"(dewpoint - 32) / 1.8",
      "relative_humidity":"relative_humidity", "wind_speed_ms":"wind_speed / 2.2369362921",
      "station_pressure_hpa":"station_pressure * 33.8638866667"}


def database_engine():
    url = URL.create("postgresql+psycopg2", username=os.getenv("DB_USER") or os.getenv("USER"),
                     password=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST", "localhost"),
                     port=int(os.getenv("DB_PORT", "5432")), database=os.getenv("DB_NAME", "metpipe_northeast"))
    return create_engine(url, connect_args={"options":"-c default_transaction_read_only=on -c statement_timeout=600000"})


def load_daily(engine, start, end):
    """Aggregate in PostgreSQL: never transfer millions of point/JSONB rows."""
    fields = [f"AVG({expression}) AS {field}, COUNT({expression}) AS {field}_hours"
              for field, expression in SI.items()]
    sql = """SELECT datetime::date AS date, station, MIN(source_dataset) AS source_dataset,
             COUNT(*) AS routine_hours, """ + ",".join(fields) + """,
             COUNT(precipitation) AS precipitation_mm_hours,
             SUM(precipitation) * 25.4 AS observed_precipitation_mm
             FROM weather_hourly WHERE datetime >= :start AND datetime < :end
             GROUP BY datetime::date, station ORDER BY date, station"""
    with engine.connect() as connection:
        frame = pd.read_sql_query(text(sql), connection, params={"start":start, "end":end}, parse_dates=["date"])
        stations = list(connection.execute(text("SELECT station FROM station_metadata ORDER BY station")).scalars())
        source_counts = pd.read_sql_query(text("""SELECT source_dataset, COUNT(*) AS point_observations,
            MIN(datetime) AS first_local_time, MAX(datetime) AS last_local_time FROM weather_observations
            WHERE datetime >= :start AND datetime < :end GROUP BY source_dataset ORDER BY source_dataset"""),
            connection, params={"start":start,"end":end})
    return complete_calendar(frame, stations, start, end), source_counts


def complete_calendar(frame, stations, start, end):
    """Add an expected-day scaffold; count zeros are not fabricated weather values."""
    if frame.duplicated(["date","station"]).any():
        raise ValueError("Duplicate station-days in the aggregate")
    dates = pd.date_range(start, end, freq="D", inclusive="left")
    index = pd.MultiIndex.from_product([dates,stations], names=["date","station"])
    result = frame.set_index(["date","station"]).reindex(index).reset_index()
    counts = ["routine_hours"] + [field + "_hours" for field in FIELDS] + ["precipitation_mm_hours"]
    for column in counts:
        result[column] = result[column].fillna(0).astype(int)
        if not result[column].between(0,24).all():
            raise ValueError(f"Invalid hourly counts: {column}")
        if column != "routine_hours" and (result[column] > result["routine_hours"]).any():
            raise ValueError(f"Element counts exceed routine reports: {column}")
    result["expected_hours"] = 24
    return result


def coverage_table(daily):
    columns = ["routine_hours"] + [f + "_hours" for f in FIELDS] + ["precipitation_mm_hours"]
    totals = daily.groupby("station")[columns + ["expected_hours"]].sum()
    return totals[columns].div(totals["expected_hours"],axis=0) * 100


def eligible_daily(daily, minimum_hours=18):
    """Mask low-coverage daily means; never replace a missing measurement by zero."""
    result = daily.copy()
    for field in FIELDS:
        result.loc[result[field + "_hours"] < minimum_hours, field] = np.nan
    return result


def period_means(daily, field, frequency="YS", minimum_fraction=0.9):
    """Hourly-count-weighted means, screened against expected calendar hours."""
    if field not in FIELDS:
        raise ValueError("Only continuous non-precipitation fields are supported")
    if frequency not in {"YS", "MS"}:
        raise ValueError("Choose annual YS or monthly MS periods")
    work = daily[["date","station",field,field+"_hours","expected_hours"]].copy()
    work["weighted_sum"] = work[field] * work[field+"_hours"]
    work["period"] = work["date"].dt.to_period("Y" if frequency == "YS" else "M").dt.to_timestamp()
    grouped = work.groupby(["period","station"])
    totals = grouped[[field+"_hours","expected_hours"]].sum()
    totals["weighted_sum"] = grouped["weighted_sum"].sum(min_count=1)
    totals["coverage"] = totals[field+"_hours"] / totals["expected_hours"]
    totals[field] = totals["weighted_sum"] / totals[field+"_hours"].replace(0,np.nan)
    totals.loc[totals["coverage"] < minimum_fraction,field] = np.nan
    return totals.reset_index()


def daily_wide(daily, field):
    return daily.pivot(index="date",columns="station",values=field).sort_index()


def seasonal_anomalies(wide):
    """Remove sample monthly means, descriptively; not a 30-year normal or CV transform."""
    return wide - wide.groupby(wide.index.month).transform("mean")


def correlations(wide, minimum_pairs=365):
    present = wide.notna().astype("int64")
    pair_counts = present.T.dot(present)
    matrix = wide.corr(min_periods=minimum_pairs)
    return matrix.where(pair_counts >= minimum_pairs), pair_counts


def lag_correlations(wide, source, target, maximum_days=3, minimum_pairs=365):
    """At lag k correlate source(t-k) with target(t); positive k means source earlier."""
    if (not isinstance(wide.index, pd.DatetimeIndex) or wide.empty or
            not wide.index.equals(pd.date_range(wide.index.min(), wide.index.max(), freq="D"))):
        raise ValueError("Daily lag analysis requires a complete, ordered calendar index; preserve gaps as NaN")
    result = []
    for lag in range(-maximum_days,maximum_days+1):
        pair = pd.concat([wide[source].shift(lag).rename("source"),wide[target].rename("target")],axis=1).dropna()
        r = pair["source"].corr(pair["target"]) if len(pair) >= minimum_pairs else np.nan
        result.append({"lag_days":lag,"paired_days":len(pair),"pearson_r":r})
    return pd.DataFrame(result)
