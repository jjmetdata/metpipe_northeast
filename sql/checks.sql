-- Multi-year validation checks for MetPipe Northeast.

-- List project tables and views.
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_type, table_name;

-- Verify coverage and row counts separately for every station and year.
SELECT
    "station",
    EXTRACT(YEAR FROM "datetime")::int AS "year",
    MIN("datetime") AS "first_obs_time",
    MAX("datetime") AS "last_obs_time",
    COUNT(*) AS "row_count"
FROM "weather_observations"
GROUP BY "station", EXTRACT(YEAR FROM "datetime")::int
ORDER BY "station", "year";

-- Find observations whose station is missing from metadata (expected: no rows).
SELECT DISTINCT w."station"
FROM "weather_observations" w
LEFT JOIN "station_metadata" m ON w."station" = m."station"
WHERE m."station" IS NULL;

-- Check for duplicate station-timestamp records (expected: no rows).
SELECT
    "datetime",
    "station",
    COUNT(*) AS "duplicate_count"
FROM "weather_observations"
GROUP BY "datetime", "station"
HAVING COUNT(*) > 1;

-- Check representative hourly coverage by station and year.
WITH hourly_counts AS (
    SELECT
        "station",
        EXTRACT(YEAR FROM "datetime")::int AS "year",
        COUNT(*) AS "hourly_row_count"
    FROM "weather_hourly"
    GROUP BY "station", EXTRACT(YEAR FROM "datetime")::int
)
SELECT
    h."station",
    h."year",
    m."minute_offset",
    h."hourly_row_count",
    EXTRACT(DOY FROM make_date(h."year", 12, 31))::int * 24 AS "expected_hours",
    ROUND(
        100.0 * h."hourly_row_count" /
        (EXTRACT(DOY FROM make_date(h."year", 12, 31))::int * 24),
        1
    ) AS "coverage_pct"
FROM hourly_counts h
JOIN "station_metadata" m ON h."station" = m."station"
ORDER BY h."station", h."year";

-- Every loaded row should retain its NOAA report type (expected: no rows).
SELECT "station", COUNT(*) AS "missing_report_type_rows"
FROM "weather_observations"
WHERE "report_type" IS NULL
GROUP BY "station";

-- Check daily coverage by station and year.
SELECT
    "station",
    EXTRACT(YEAR FROM "date")::int AS "year",
    COUNT(*) AS "daily_row_count"
FROM "weather_daily_summary"
GROUP BY "station", EXTRACT(YEAR FROM "date")::int
ORDER BY "station", "year";

-- Inspect monthly results. Month is a full date such as 2025-01-01.
SELECT *
FROM "weather_monthly_summary"
ORDER BY "station", "month";

-- Expect up to 12 rows for every complete station-year combination.
SELECT
    "station",
    EXTRACT(YEAR FROM "month")::int AS "year",
    COUNT(*) AS "monthly_row_count"
FROM "weather_monthly_summary"
GROUP BY "station", EXTRACT(YEAR FROM "month")::int
ORDER BY "station", "year";

SELECT *
FROM "weather_annual_summary"
ORDER BY "station", "year";
