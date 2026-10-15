"""Read-only, gap-aware exploratory cooling events; not a forecasting model."""
import numpy as np
import pandas as pd
from sqlalchemy import bindparam, text

from hourly_pair import align_hourly, utc_hour

FIELDS = ["temperature_c", "dewpoint_c", "wind_speed_ms", "station_pressure_hpa"]


def shift_hours(timestamp, hours):
    """Explicit nanosecond arithmetic avoids pandas/NumPy scalar timedelta warnings."""
    timestamp = pd.Timestamp(timestamp)
    if timestamp.tzinfo is None:
        raise ValueError("Use a timezone-aware timestamp")
    return pd.Timestamp(timestamp.value + int(hours * 3_600_000_000_000), tz="UTC")


def load_event_hours(engine, stations, start, end):
    start, end = utc_hour(start), utc_hour(end)
    query = text("""SELECT datetime_utc AS hour_utc, station,
        observation_datetime_utc AS observation_time_utc, temperature_c,
        dewpoint_c, wind_speed_ms, wind_direction, station_pressure_hpa,
        source_dataset FROM weather_hourly_utc WHERE station IN :stations
        AND datetime_utc >= :start AND datetime_utc < :end
        ORDER BY datetime_utc, station""").bindparams(bindparam("stations", expanding=True))
    with engine.connect() as connection:
        if connection.execute(text("SELECT current_setting('transaction_read_only')")).scalar() != "on":
            raise ValueError("Use the read-only database engine")
        records = pd.read_sql_query(query, connection, params={
            "stations": list(stations), "start": start.to_pydatetime(), "end": end.to_pydatetime()})
    result = align_hourly(records, stations, start, end)
    direction = pd.to_numeric(result["wind_direction"], errors="coerce")
    # Calm/variable winds have no usable directional angle. Never interpolate VRB.
    result["wind_direction_deg"] = direction.where(direction.between(0, 360) & result.wind_speed_ms.gt(0))
    return result


def temperature_reference(reference, minimum_samples=40):
    """Four-year sample month/UTC-hour means, not official climate normals."""
    work = reference.assign(month=reference.hour_utc.dt.month, utc_hour=reference.hour_utc.dt.hour)
    result = work.groupby(["station", "month", "utc_hour"]).temperature_c.agg(["mean", "count"])
    result.loc[result["count"] < minimum_samples, "mean"] = np.nan
    return result.rename(columns={"mean": "reference_temperature_c", "count": "reference_samples"}).reset_index()


def add_reference_and_changes(hourly, reference, periods=3):
    """Differences require all intervening hours and near-nominal actual elapsed time."""
    if periods < 1 or int(periods) != periods:
        raise ValueError("Choose a positive whole-hour difference")
    work = hourly.assign(month=hourly.hour_utc.dt.month, utc_hour=hourly.hour_utc.dt.hour)
    work = work.merge(reference, on=["station", "month", "utc_hour"], how="left", validate="many_to_one")
    work["temperature_anomaly_c"] = work.temperature_c - work.reference_temperature_c
    pieces = []
    for _, frame in work.groupby("station", sort=False):
        frame = frame.sort_values("hour_utc").copy()
        expected = pd.date_range(frame.hour_utc.min(), frame.hour_utc.max(), freq="h")
        if not pd.DatetimeIndex(frame.hour_utc).equals(expected):
            raise ValueError("Keep the complete hourly scaffold, including missing hours")
        elapsed = (frame.observation_time_utc - frame.observation_time_utc.shift(periods)).dt.total_seconds() / 3600
        frame[f"elapsed_{periods}h"] = elapsed
        for field in ["temperature_c", "temperature_anomaly_c", "dewpoint_c", "station_pressure_hpa"]:
            present = frame[field].notna() & frame.observation_time_utc.notna()
            valid = present.rolling(periods + 1, min_periods=periods + 1).sum().eq(periods + 1)
            valid &= elapsed.between(periods - 0.25, periods + 0.25)
            if field == "temperature_anomaly_c":
                # A piecewise monthly reference can jump at month boundaries.
                # Never interpret that reference step as a weather tendency.
                valid &= frame.month.eq(frame.month.shift(periods))
            frame[f"{field}_change_{periods}h"] = frame[field].diff(periods).where(valid)
        pieces.append(frame)
    return pd.concat(pieces, ignore_index=True).sort_values(["hour_utc", "station"]).reset_index(drop=True)


def cooling_mask(frame, raw_threshold=-5.0, anomaly_threshold=-4.0):
    return (frame.temperature_c_change_3h.le(raw_threshold) &
            frame.temperature_anomaly_c_change_3h.le(anomaly_threshold))


def select_events(signals, source="ALB", separation_hours=72, raw_threshold=-5., anomaly_threshold=-4.):
    """Greedy source-only ranking; downstream outcomes never influence selection."""
    if separation_hours < 72:
        raise ValueError("Use at least 72 hours between the displayed 72-hour cases")
    source_hours = signals[signals.station.eq(source)]
    candidates = source_hours[cooling_mask(source_hours, raw_threshold, anomaly_threshold)]
    # Complete 24-hours-before/48-hours-after plotting windows must fit the extract.
    candidates = candidates[candidates.hour_utc.ge(shift_hours(signals.hour_utc.min(), 24)) &
                            candidates.hour_utc.le(shift_hours(signals.hour_utc.max(), -47))]
    candidates = candidates.sort_values(["temperature_anomaly_c_change_3h", "hour_utc"], kind="stable")
    kept = []
    for _, row in candidates.iterrows():
        if all(abs(row.hour_utc.value - old.hour_utc.value) >= separation_hours * 3_600_000_000_000 for old in kept):
            kept.append(row)
    columns = ["station", "hour_utc", "observation_time_utc", "temperature_c_change_3h",
               "temperature_anomaly_c_change_3h", "elapsed_3h"]
    result = pd.DataFrame(kept, columns=signals.columns)[columns].reset_index(drop=True)
    result.insert(0, "event_rank", range(1, len(result) + 1))
    return result


def response_screen(signals, events, stations, after_hours=18):
    """First same-rule cooling after source detection, NOT a matched front-arrival lag."""
    rows = []
    for event in events.itertuples():
        for station in stations:
            frame = signals[signals.station.eq(station)]
            after = frame[frame.observation_time_utc.ge(event.observation_time_utc) &
                          frame.observation_time_utc.lt(shift_hours(event.observation_time_utc, after_hours))]
            # Include absent reports in coverage diagnostics using bucket boundaries.
            buckets = frame[frame.hour_utc.ge(event.hour_utc) &
                            frame.hour_utc.lt(shift_hours(event.hour_utc, after_hours))]
            before = frame[frame.observation_time_utc.ge(shift_hours(event.observation_time_utc, -6)) &
                           frame.observation_time_utc.lt(event.observation_time_utc)]
            hits = after[cooling_mask(after)].sort_values("observation_time_utc")
            hit = hits.iloc[0] if not hits.empty else None
            rows.append({"event_rank": event.event_rank, "station": station,
                         "first_qualifying_report_utc": hit.observation_time_utc if hit is not None else pd.NaT,
                         "detection_offset_hours_not_lag": (hit.observation_time_utc.value - event.observation_time_utc.value)/3_600_000_000_000 if hit is not None else np.nan,
                         "qualifying_reports_previous_6h": int(cooling_mask(before).sum()),
                         "valid_3h_changes_next_18_buckets": int(buckets.temperature_c_change_3h.notna().sum()),
                         "cooling_3h_c_at_detection": hit.temperature_c_change_3h if hit is not None else np.nan})
    return pd.DataFrame(rows)


def field_segments(frame, field):
    valid = frame.sort_values("hour_utc").dropna(subset=[field, "observation_time_utc"])
    starts = valid.hour_utc.diff().dt.total_seconds().ne(3600)
    if field == "temperature_anomaly_c":
        starts |= valid.hour_utc.dt.month.ne(valid.hour_utc.dt.month.shift())
    groups = starts.cumsum()
    return [piece for _, piece in valid.groupby(groups)]


def pressure_from_window_start(window):
    """Subtract each station's report in the common first bucket, not its first valid value.

    This is a within-station departure, not sea-level pressure or a gradient.
    A missing first-bucket pressure leaves that station's departure unavailable.
    """
    result = window.copy()
    start = result.hour_utc.min()
    anchors = result[result.hour_utc.eq(start)].set_index("station")
    if anchors.index.has_duplicates or set(anchors.index) != set(result.station):
        raise ValueError("Every station must have one scaffold row in the common first bucket")
    baseline = anchors.station_pressure_hpa.where(anchors.observation_time_utc.notna())
    result["window_start_pressure_hpa"] = result.station.map(baseline)
    result["pressure_departure_hpa"] = result.station_pressure_hpa - result.window_start_pressure_hpa
    return result


def add_pc24(hourly):
    """PC24 = station pressure now minus the report in the bucket 24h earlier.

    Only endpoints are required: this is a net difference, not an assertion
    about the intervening path. Never shift by 24 available records or impute.
    """
    pieces = []
    for _, frame in hourly.groupby("station", sort=False):
        frame = frame.sort_values("hour_utc").copy()
        expected = pd.date_range(frame.hour_utc.min(), frame.hour_utc.max(), freq="h")
        if not pd.DatetimeIndex(frame.hour_utc).equals(expected):
            raise ValueError("PC24 requires a complete hourly scaffold; retain absent hours")
        previous_pressure = frame.station_pressure_hpa.shift(24)
        previous_time = frame.observation_time_utc.shift(24)
        elapsed = (frame.observation_time_utc - previous_time).dt.total_seconds() / 3600
        valid = (frame.station_pressure_hpa.notna() & previous_pressure.notna() &
                 frame.observation_time_utc.notna() & previous_time.notna() & elapsed.between(23.75, 24.25))
        frame["pressure_24h_ago_hpa"] = previous_pressure
        frame["observation_time_24h_ago_utc"] = previous_time
        frame["pc24_elapsed_hours"] = elapsed
        frame["pc24_hpa"] = (frame.station_pressure_hpa - previous_pressure).where(valid)
        frame["pc24_window_valid_pressure_hours"] = (
            (frame.station_pressure_hpa.notna() & frame.observation_time_utc.notna())
            .astype(int).rolling(25, min_periods=25).sum())
        pieces.append(frame)
    return pd.concat(pieces, ignore_index=True).sort_values(["hour_utc", "station"]).reset_index(drop=True)


def pressure_window_summary(window):
    """Coverage and extremes of observed three-hour changes; no inferred regime labels."""
    window = pressure_from_window_start(window)
    rows = []
    for station, frame in window.groupby("station"):
        frame = frame.sort_values("hour_utc")
        start = frame.iloc[0]
        valid = frame.dropna(subset=["station_pressure_hpa_change_3h", "observation_time_utc"])
        peak = valid.loc[valid.station_pressure_hpa_change_3h.idxmax()] if not valid.empty else None
        trough = valid.loc[valid.station_pressure_hpa_change_3h.idxmin()] if not valid.empty else None
        rows.append({"station": station, "expected_hours": len(frame),
                     "valid_pressure_hours": int(frame.station_pressure_hpa.notna().sum()),
                     "valid_pressure_change_3h_hours": len(valid),
                     "baseline_report_utc": start.observation_time_utc if pd.notna(start.window_start_pressure_hpa) else pd.NaT,
                     "baseline_pressure_hpa": start.window_start_pressure_hpa,
                     "largest_observed_3h_change_hpa": peak.station_pressure_hpa_change_3h if peak is not None else np.nan,
                     "largest_change_report_utc": peak.observation_time_utc if peak is not None else pd.NaT,
                     "smallest_observed_3h_change_hpa": trough.station_pressure_hpa_change_3h if trough is not None else np.nan,
                     "smallest_change_report_utc": trough.observation_time_utc if trough is not None else pd.NaT})
    return pd.DataFrame(rows)


def pc24_transition_screen(signals, events, stations, before_hours=12, after_hours=24,
                           threshold=0., confirmation_reports=3):
    """Earliest observed nonpositive-to-positive crossing with causal confirmation.

    Previous report must be <= threshold, then consecutive hourly reports must
    be > threshold. Confirmation time is not backdated to the first report.
    The search interval is predefined relative to the temperature-selected case.
    """
    if confirmation_reports < 1 or int(confirmation_reports) != confirmation_reports:
        raise ValueError("Choose a positive whole number of confirmation reports")
    records = []
    for event in events.itertuples():
        begin = shift_hours(event.hour_utc, -before_hours)
        end = shift_hours(event.hour_utc, after_hours)
        for station in stations:
            frame = signals[signals.station.eq(station)].sort_values("hour_utc").copy()
            expected = pd.date_range(frame.hour_utc.min(), frame.hour_utc.max(), freq="h")
            if not pd.DatetimeIndex(frame.hour_utc).equals(expected):
                raise ValueError("Transition screening requires the complete hourly scaffold")
            pc = frame.pc24_hpa.to_numpy()
            in_search = frame.hour_utc.ge(begin) & frame.hour_utc.lt(end)
            hits = []
            for index in np.flatnonzero(in_search.to_numpy()):
                if index < 1 or index + confirmation_reports > len(frame):
                    continue
                block = frame.iloc[index - 1:index + confirmation_reports]
                values = pc[index - 1:index + confirmation_reports]
                elapsed = block.observation_time_utc.diff().dt.total_seconds().iloc[1:] / 3600
                if (np.isfinite(values).all() and values[0] <= threshold and
                        (values[1:] > threshold).all() and elapsed.between(.75, 1.25).all()):
                    hits.append(index)
            search = frame[in_search]
            valid_hours = int((search.pc24_hpa.notna() & search.observation_time_utc.notna()).sum())
            expected_hours = before_hours + after_hours
            gaps = len(search) != expected_hours or valid_hours != expected_hours
            initial = search.iloc[0].pc24_hpa if len(search) else np.nan
            row = {"event_rank": event.event_rank, "station": station,
                   "search_start_utc": begin, "search_end_utc": end,
                   "threshold_hpa": threshold, "confirmation_reports": confirmation_reports,
                   "expected_search_hours": expected_hours, "valid_pc24_search_hours": valid_hours,
                   "qualifying_crossings": len(hits),
                   "already_positive_at_search_start": bool(initial > threshold) if pd.notna(initial) else False,
                   "search_start_pc24_hpa": initial,
                   "status": ("multiple_observed_crossings" if len(hits) > 1 else
                              "one_observed_crossing" if len(hits) == 1 else "no_observed_crossing") +
                             ("_with_gaps" if gaps else ""),
                   "last_nonpositive_report_utc": pd.NaT,
                   "first_positive_report_utc": pd.NaT, "confirmation_report_utc": pd.NaT,
                   "first_positive_pc24_hpa": np.nan, "confirmation_pc24_hpa": np.nan}
            if hits:
                index = hits[0]
                first, previous, confirmed = frame.iloc[index], frame.iloc[index - 1], frame.iloc[index + confirmation_reports - 1]
                row.update(last_nonpositive_report_utc=previous.observation_time_utc,
                           first_positive_report_utc=first.observation_time_utc,
                           confirmation_report_utc=confirmed.observation_time_utc,
                           first_positive_pc24_hpa=first.pc24_hpa,
                           confirmation_pc24_hpa=confirmed.pc24_hpa)
            records.append(row)
    return pd.DataFrame(records)


def pc24_timing_comparisons(transitions, source="ALB", targets=("BOS", "PVC")):
    """Positive observed offsets mean source earlier; not forecast or causal lags."""
    rows = []
    def hours(later, earlier):
        return (later.value - earlier.value) / 3_600_000_000_000 if pd.notna(later) and pd.notna(earlier) else np.nan
    for rank, group in transitions.groupby("event_rank"):
        lookup = group.set_index("station")
        if source not in lookup.index:
            raise ValueError("Source transition row missing")
        origin = lookup.loc[source]
        for target in targets:
            destination = lookup.loc[target]
            clean = all(row.status == "one_observed_crossing" and
                        not row.already_positive_at_search_start for row in [origin, destination])
            rows.append({"event_rank": rank, "source": source, "target": target,
                         "source_status": origin.status, "target_status": destination.status,
                         "unambiguous_complete_search_pair": clean,
                         "first_positive_offset_hours": hours(destination.first_positive_report_utc, origin.first_positive_report_utc),
                         "confirmation_offset_hours": hours(destination.confirmation_report_utc, origin.confirmation_report_utc),
                         "source_confirmation_to_target_first_positive_hours": hours(destination.first_positive_report_utc, origin.confirmation_report_utc),
                         "crossing_offset_lower_bound_hours": hours(destination.last_nonpositive_report_utc, origin.first_positive_report_utc),
                         "crossing_offset_upper_bound_hours": hours(destination.first_positive_report_utc, origin.last_nonpositive_report_utc)})
    return pd.DataFrame(rows)
