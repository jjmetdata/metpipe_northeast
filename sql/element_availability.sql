-- Read-only availability audit for the confirmed 20-station network, 2020–2024.
-- Run in DataGrip or: psql -d metpipe_northeast -f sql/element_availability.sql
-- Availability measures stored values, not sensor accuracy or quality approval.
-- weather_hourly uses the checked FM-15 minute and one record per station/hour.

-- 1. Distinguish audited source stations from stations actually in PostgreSQL.
WITH network(station) AS (
    VALUES ('ALB'), ('AUG'), ('BAF'), ('BDL'), ('BOS'), ('BTV'), ('DDH'),
           ('EWB'), ('HVN'), ('HYA'), ('JFK'), ('LEB'), ('MHT'), ('MVY'),
           ('ORH'), ('PVC'), ('PVD'), ('PWM'), ('PYM'), ('UUU')
)
SELECT n.station,
       COUNT(w.datetime) AS ingested_observations,
       COUNT(DISTINCT EXTRACT(YEAR FROM w.datetime)) AS ingested_years,
       MIN(w.datetime) AS first_observation,
       MAX(w.datetime) AS last_observation
FROM network n
LEFT JOIN weather_observations w
  ON w.station = n.station
 AND w.datetime >= TIMESTAMP '2020-01-01'
 AND w.datetime < TIMESTAMP '2025-01-01'
GROUP BY n.station
ORDER BY n.station;

-- 2. Per-element coverage for each loaded station, both overall and by year.
-- pct_of_existing_reports excludes entirely missing hourly reports.
-- pct_of_expected_hours includes those missing reports in the denominator.
-- Blank text is absent. Numeric zero is present. Gusts are conditional reports,
-- so a low gust percentage alone is not evidence of an instrument outage.
-- Precipitation NULL must retain its source meaning; it is not changed to zero.
-- Some stations omit dry-hour precipitation values instead of encoding 0.00.
-- Precipitation non-null percentages alone are not comparable sensor-completeness
-- measures. Decode source METAR remarks and sensor-status flags before inferring
-- dry hours. PNO indicates an unavailable rain gauge; such blanks stay unknown.
WITH counts AS (
    SELECT station,
           EXTRACT(YEAR FROM datetime)::int AS year,
           COUNT(*) AS hourly_reports,
           COUNT(temperature) AS temperature,
           COUNT(dewpoint) AS dewpoint,
           COUNT(relative_humidity) AS relative_humidity,
           COUNT(station_pressure) AS station_pressure,
           COUNT(wind_speed) AS wind_speed,
           COUNT(NULLIF(TRIM(wind_direction), '')) AS wind_direction,
           COUNT(precipitation) AS precipitation,
           COUNT(NULLIF(TRIM(sky_conditions), '')) AS sky_conditions,
           COUNT(wind_gust) AS wind_gust
    FROM weather_hourly
    WHERE datetime >= TIMESTAMP '2020-01-01'
      AND datetime < TIMESTAMP '2025-01-01'
    GROUP BY GROUPING SETS (
        (station),
        (station, EXTRACT(YEAR FROM datetime)::int)
    )
), periods AS (
    SELECT *,
           CASE WHEN year IS NULL THEN 43848
                ELSE EXTRACT(DOY FROM make_date(year, 12, 31))::int * 24
           END AS expected_hours
    FROM counts
)
SELECT p.station,
       COALESCE(p.year::text, '2020-2024') AS period,
       e.element,
       p.hourly_reports,
       p.expected_hours,
       ROUND(100.0 * p.hourly_reports / p.expected_hours, 1) AS report_coverage_pct,
       e.present_values,
       ROUND(100.0 * e.present_values / NULLIF(p.hourly_reports, 0), 1)
           AS pct_of_existing_reports,
       ROUND(100.0 * e.present_values / p.expected_hours, 1)
           AS pct_of_expected_hours
FROM periods p
CROSS JOIN LATERAL (
    VALUES ('temperature', p.temperature),
           ('dewpoint', p.dewpoint),
           ('relative_humidity', p.relative_humidity),
           ('station_pressure', p.station_pressure),
           ('wind_speed', p.wind_speed),
           ('wind_direction', p.wind_direction),
           ('precipitation', p.precipitation),
           ('sky_conditions', p.sky_conditions),
           ('wind_gust', p.wind_gust)
) e(element, present_values)
ORDER BY p.station, p.year NULLS FIRST, e.element;

-- 3. Monthly PVC diagnostics: annual averages can hide concentrated field gaps.
SELECT date_trunc('month', datetime)::date AS month,
       COUNT(*) AS hourly_reports,
       ROUND(100.0 * COUNT(temperature) / COUNT(*), 1) AS temperature_pct,
       ROUND(100.0 * COUNT(station_pressure) / COUNT(*), 1) AS pressure_pct,
       ROUND(100.0 * COUNT(NULLIF(TRIM(sky_conditions), '')) / COUNT(*), 1)
           AS sky_pct,
       ROUND(100.0 * COUNT(precipitation) / COUNT(*), 1) AS precipitation_pct
FROM weather_hourly
WHERE station = 'PVC'
  AND datetime >= TIMESTAMP '2020-01-01'
  AND datetime < TIMESTAMP '2025-01-01'
GROUP BY date_trunc('month', datetime)::date
ORDER BY month;
