-- Read-only checks for the original 20 stations and 2005–2024 dataset.
-- Times in weather_observations/weather_hourly are local standard time (UTC-5).

SELECT source_dataset, COUNT(*) AS rows, MIN(datetime), MAX(datetime)
FROM weather_observations GROUP BY source_dataset ORDER BY source_dataset;

-- Every station should have each target calendar year represented. Missing
-- observations within those years remain genuine gaps, not artificial rows.
WITH expected AS (
    SELECT station, year
    FROM station_metadata CROSS JOIN generate_series(2005, 2024) AS year
), actual AS (
    SELECT station, EXTRACT(YEAR FROM datetime)::int AS year, COUNT(*) AS rows
    FROM weather_observations GROUP BY station, EXTRACT(YEAR FROM datetime)::int
)
SELECT e.station, e.year, COALESCE(a.rows, 0) AS observations
FROM expected e LEFT JOIN actual a USING (station, year)
ORDER BY e.station, e.year;

-- Expected: zero UTC/LST inconsistencies and no GHCNh rows outside the backfill.
SELECT COUNT(*) FILTER (WHERE datetime_utc IS NULL OR
        datetime <> (datetime_utc AT TIME ZONE 'UTC') - interval '5 hours') AS time_mismatches,
       COUNT(*) FILTER (WHERE datetime < '2005-01-01' OR datetime >= '2020-01-01') AS outside_backfill,
       COUNT(*) FILTER (WHERE source_metadata IS NULL) AS missing_provenance,
       COUNT(*) FILTER (WHERE precipitation_trace IS TRUE AND precipitation <> 0) AS inconsistent_trace
FROM weather_observations WHERE source_dataset = 'GHCNh';

-- Stored legacy-compatible units must round-trip to source SI values.
SELECT COUNT(*) FILTER (WHERE temperature IS NOT NULL AND
           ABS(temperature - ((source_metadata #>> '{fields,temperature,raw}')::float8 * 1.8 + 32)) > 1e-8) AS temperature_mismatches,
       COUNT(*) FILTER (WHERE wind_speed IS NOT NULL AND
           ABS(wind_speed - (source_metadata #>> '{fields,wind_speed,raw}')::float8 * 2.2369362921) > 1e-8) AS wind_mismatches,
       COUNT(*) FILTER (WHERE station_pressure IS NOT NULL AND
           ABS(station_pressure - (source_metadata #>> '{fields,station_level_pressure,raw}')::float8 / 33.8638866667) > 1e-8) AS pressure_mismatches
FROM weather_observations WHERE source_dataset = 'GHCNh';

-- Files are UTC-calendar-year files. The 2020 files supply only the final five
-- hours of local-standard-time 2019, not replacement 2020 observations.
SELECT COUNT(*) AS source_files, SUM(imported_rows) AS expected_point_rows
FROM ghcnh_ingestion_files
WHERE local_start = '2005-01-01' AND local_end = '2020-01-01';

SELECT station, EXTRACT(YEAR FROM datetime)::int AS year,
       COUNT(*) AS routine_hours, COUNT(temperature) AS temperature_hours,
       COUNT(dewpoint) AS dewpoint_hours, COUNT(wind_speed) AS wind_hours,
       COUNT(precipitation) AS amount_value_hours,
       COUNT(*) FILTER (WHERE precipitation_trace IS TRUE) AS trace_hours
FROM weather_hourly
GROUP BY station, EXTRACT(YEAR FROM datetime)::int ORDER BY station, year;

-- UTC/SI interface for future model joins; observation time differs from the
-- hourly bucket time. Use actual observation_datetime_utc for lead/lag analysis.
SELECT * FROM weather_hourly_utc ORDER BY observation_datetime_utc DESC LIMIT 20;
