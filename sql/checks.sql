-- sanity checks for database objects, station coverage, row counts, duplicates, and views

-- list all the tables
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_type, table_name;

-- check the presence of all stations, and the number of rows for each station in the "northeast_weather_2024" table
-- check each station's time coverage
SELECT
    "station",
    MIN("datetime") AS "first_obs_time",
    MAX("datetime") AS "last_obs_time",
    COUNT(*) AS row_count
FROM "northeast_weather_2024"
GROUP BY "station" ORDER BY "station";

SELECT
    m."station",
    MIN(w."datetime") AS "first_obs_time",
    MAX(w."datetime") AS "last_obs_time",
    COUNT(w."datetime") AS "row_count"
FROM "station_metadata" m
LEFT JOIN "northeast_weather_2024" w
    ON m."station" = w."station"
GROUP BY m."station"
ORDER BY m."station";

-- check for duplicate rows
SELECT
    "datetime",
    "station",
    COUNT(*)
FROM "northeast_weather_2024"
GROUP BY "datetime", "station"
HAVING COUNT(*) > 1;


-- check the views
SELECT "station", COUNT(*)
FROM "northeast_weather_2024_hourly"
GROUP BY "station"
ORDER BY "station";

SELECT *
FROM "northeast_weather_2024_daily_summary"
ORDER BY "date", "station"
LIMIT 20;

-- row counts for the daily summary
SELECT
    "station",
    COUNT(*) AS "daily_row_count"
FROM "northeast_weather_2024_daily_summary"
GROUP BY "station"
ORDER BY "station";

SELECT *
FROM "northeast_weather_2024_monthly_summary"
ORDER BY "station", "month";

-- row counts for the monthly summary
SELECT
    "station",
    COUNT(*) AS "monthly_row_count"
FROM "northeast_weather_2024_monthly_summary"
GROUP BY "station"
ORDER BY "station";