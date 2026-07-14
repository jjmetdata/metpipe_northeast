-- Legacy reference only. PostgreSQL COPY requires server-visible absolute paths.
-- Replace /absolute/path/to/metpipe_phase2 with the local repository path before use.

-- copy data from all CSV files into the new table, and add a new column "station" to indicate the station

BEGIN TRANSACTION;

-- create a temporary table to store the raw hourly weather data from the CSV files, which will be used for the data ingestion process.
-- this temp table will be used for all the CSV files, and we will truncate it before loading data from each file to ensure that it only contains the data from the current file being processed.
-- this temp table will be dropped automatically at the end of the transaction.
CREATE TEMP TABLE temp_weather (
    "datetime" TIMESTAMP,
    "temperature" DOUBLE PRECISION,
    "dewpoint" DOUBLE PRECISION,
    "relative_humidity" DOUBLE PRECISION,
    "precipitation" VARCHAR(5),
    "sky_conditions" VARCHAR(50),
    "station_pressure" DOUBLE PRECISION,
    "wind_direction" VARCHAR(3),
    "wind_speed" DOUBLE PRECISION,
    "wind_gust" DOUBLE PRECISION
)
ON COMMIT DROP;

-- PART I: Boston (BOS)
-- copy data from the Boston CSV file into the temporary table, and then insert the data into the "northeast_weather_2024" table with the station column set to 'BOS'
COPY temp_weather (
    "datetime",
    "temperature",
    "dewpoint",
    "relative_humidity",
    "precipitation",
    "sky_conditions",
    "station_pressure",
    "wind_direction",
    "wind_speed",
    "wind_gust"
) FROM '/absolute/path/to/metpipe_phase2/data/processed/bos_hourly_2024_cleaned.csv' DELIMITER ',' CSV HEADER;

-- handle the 'T' value in the precipitation column, by converting it to a small numeric value (e.g., 0.001) for consistency with the other numeric values in the column
INSERT INTO "northeast_weather_2024"
SELECT DISTINCT
    "datetime",
    'BOS' AS "station",
    "temperature",
    "dewpoint",
    "relative_humidity",
    CASE
        WHEN "precipitation" = 'T' THEN 0.001
        ELSE "precipitation"::double precision
    END AS "precipitation",
    "sky_conditions",
    "station_pressure",
    "wind_direction",
    "wind_speed",
    "wind_gust"
FROM temp_weather
ON CONFLICT ("datetime", "station") DO NOTHING;

-- PART II: Albany (ALB)
TRUNCATE temp_weather; -- truncate the temp table to remove the data from the previous file, and prepare it for the next file

-- copy data from the Albany CSV file into the temporary table, and then insert the data into the "northeast_weather_2024" table with the station column set to 'ALB'
COPY temp_weather (
    "datetime",
    "temperature",
    "dewpoint",
    "relative_humidity",
    "precipitation",
    "sky_conditions",
    "station_pressure",
    "wind_direction",
    "wind_speed",
    "wind_gust"
) FROM '/absolute/path/to/metpipe_phase2/data/processed/alb_hourly_2024_cleaned.csv' DELIMITER ',' CSV HEADER;

-- handle the 'T' value in the precipitation column, by converting it to a small numeric value (e.g., 0.001) for consistency with the other numeric values in the column
INSERT INTO "northeast_weather_2024"
SELECT DISTINCT
    "datetime",
    'ALB' AS "station",
    "temperature",
    "dewpoint",
    "relative_humidity",
    CASE
        WHEN "precipitation" = 'T' THEN 0.001
        ELSE "precipitation"::double precision
    END AS "precipitation",
    "sky_conditions",
    "station_pressure",
    "wind_direction",
    "wind_speed",
    "wind_gust"
FROM temp_weather
ON CONFLICT ("datetime", "station") DO NOTHING;

-- PART III: JFK
TRUNCATE temp_weather; -- truncate the temp table to remove the data from the previous file, and prepare it for the next file

-- copy data from the JFK CSV file into the temporary table, and then insert the data into the "northeast_weather_2024" table with the station column set to 'JFK'
COPY temp_weather (
    "datetime",
    "temperature",
    "dewpoint",
    "relative_humidity",
    "precipitation",
    "sky_conditions",
    "station_pressure",
    "wind_direction",
    "wind_speed",
    "wind_gust"
) FROM '/absolute/path/to/metpipe_phase2/data/processed/jfk_hourly_2024_cleaned.csv' DELIMITER ',' CSV HEADER;

-- handle the 'T' value in the precipitation column, by converting it to a small numeric value (e.g., 0.001) for consistency with the other numeric values in the column
INSERT INTO "northeast_weather_2024"
SELECT DISTINCT
    "datetime",
    'JFK' AS "station",
    "temperature",
    "dewpoint",
    "relative_humidity",
    CASE
        WHEN "precipitation" = 'T' THEN 0.001
        ELSE "precipitation"::double precision
    END AS "precipitation",
    "sky_conditions",
    "station_pressure",
    "wind_direction",
    "wind_speed",
    "wind_gust"
FROM temp_weather
ON CONFLICT ("datetime", "station") DO NOTHING;

-- PART IV: Providence (PVD)
TRUNCATE temp_weather; -- truncate the temp table to remove the data from the previous file, and prepare it for the next file

-- copy data from the Providence CSV file into the temporary table, and then insert the data into the "northeast_weather_2024" table with the station column set to 'PVD'
COPY temp_weather (
    "datetime",
    "temperature",
    "dewpoint",
    "relative_humidity",
    "precipitation",
    "sky_conditions",
    "station_pressure",
    "wind_direction",
    "wind_speed",
    "wind_gust"
) FROM '/absolute/path/to/metpipe_phase2/data/processed/pvd_hourly_2024_cleaned.csv' DELIMITER ',' CSV HEADER;

-- handle the 'T' value in the precipitation column, by converting it to a small numeric value (e.g., 0.001) for consistency with the other numeric values in the column
INSERT INTO "northeast_weather_2024"
SELECT DISTINCT
    "datetime",
    'PVD' AS "station",
    "temperature",
    "dewpoint",
    "relative_humidity",
    CASE
        WHEN "precipitation" = 'T' THEN 0.001
        ELSE "precipitation"::double precision
    END AS "precipitation",
    "sky_conditions",
    "station_pressure",
    "wind_direction",
    "wind_speed",
    "wind_gust"
FROM temp_weather
ON CONFLICT ("datetime", "station") DO NOTHING;

COMMIT;
