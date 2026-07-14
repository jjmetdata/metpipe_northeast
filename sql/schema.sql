-- DROP DATABASE IF EXISTS "northeast_weather_2024_phase2";
-- CREATE DATABASE "northeast_weather_2024_phase2";

-- execute these statements to start from scratch, if necessary.
DROP VIEW IF EXISTS "northeast_weather_2024_monthly_summary";
DROP VIEW IF EXISTS "northeast_weather_2024_daily_summary";
DROP VIEW IF EXISTS "northeast_weather_2024_hourly";
DROP TABLE IF EXISTS "northeast_weather_2024";
DROP TABLE IF EXISTS "station_metadata";

-- create a table to store the minute offset for each station, which will be used to filter the hourly data in the "northeast_weather_2024_hourly" view
CREATE TABLE "station_metadata" (
    "station" VARCHAR(3) PRIMARY KEY,
    "minute_offset" INT NOT NULL CHECK("minute_offset" >= 0 AND "minute_offset" < 60)
);

-- the minute offsets are based on the observation times in the original CSV files, which are not exactly on the hour.
-- we filter the hourly data in the "northeast_weather_2024_hourly" view,
-- which only includes rows where the minute part of the "datetime" column matches the corresponding minute offset for each station.
INSERT INTO "station_metadata" ("station", "minute_offset") VALUES
('BOS', 54),
('ALB', 51),
('JFK', 51),
('PVD', 51);

-- create the table to store the raw hourly weather data for the Northeast region in 2024
-- with a composite primary key of "datetime" and "station",
-- and a foreign key constraint on the "station" column referencing the "station_metadata" table
CREATE TABLE "northeast_weather_2024" (
    "datetime" TIMESTAMP,
    "station" VARCHAR(3),
    "temperature" DOUBLE PRECISION,
    "dewpoint" DOUBLE PRECISION,
    "relative_humidity" DOUBLE PRECISION,
    "precipitation" DOUBLE PRECISION,
    "sky_conditions" VARCHAR(50),
    "station_pressure" DOUBLE PRECISION,
    "wind_direction" VARCHAR(3),
    "wind_speed" DOUBLE PRECISION,
    "wind_gust" DOUBLE PRECISION,
    PRIMARY KEY ("datetime", "station"),
    FOREIGN KEY ("station") REFERENCES "station_metadata" ("station")
);


-- keep the date up to the hour part only, and filter the hourly data based on the minute offsets for each station
CREATE VIEW "northeast_weather_2024_hourly" AS
SELECT
    date_trunc('hour', w."datetime") AS "datetime",
    w."station",
    w."temperature",
    w."dewpoint",
    w."relative_humidity",
    w."precipitation",
    w."sky_conditions",
    w."station_pressure",
    w."wind_direction",
    w."wind_speed",
    w."wind_gust"
FROM "northeast_weather_2024" w
JOIN "station_metadata" m ON w."station" = m."station"
WHERE EXTRACT(MINUTE FROM w."datetime") = m."minute_offset";

-- daily and monthly numbers for each station
-- skip sky conditions and wind direction for the monthly summary (for now), since they require special handling

-- for the daily summary, we will calculate the average temperature, dewpoint, relative humidity, station pressure, wind speed, and wind gust for each station on each day,
-- and the total precipitation for each station on each day
CREATE VIEW "northeast_weather_2024_daily_summary" AS
SELECT
    DATE("datetime") AS "date",
    "station",
    ROUND(AVG("temperature")::numeric,1) AS "avg_temperature",
    ROUND(AVG("dewpoint")::numeric,1) AS "avg_dewpoint",
    ROUND(AVG("relative_humidity")::numeric,1) AS "avg_relative_humidity",
    ROUND(SUM("precipitation")::numeric,2) AS "total_precipitation",
    ROUND(AVG("station_pressure")::numeric,2) AS "avg_station_pressure",
    ROUND(AVG("wind_speed")::numeric,1) AS "avg_wind_speed",
    ROUND(AVG("wind_gust")::numeric,1) AS "avg_wind_gust"
FROM "northeast_weather_2024_hourly"
GROUP BY DATE("datetime"), "station";


-- for the monthly summary, we will calculate the average temperature, dewpoint, relative humidity, station pressure, wind speed, and wind gust for each station in each month,
-- and the total precipitation for each station in each month
CREATE VIEW "northeast_weather_2024_monthly_summary" AS
SELECT
    EXTRACT(MONTH FROM "datetime") AS "month",
    "station",
    ROUND(AVG("temperature")::numeric,1) AS "avg_temperature",
    ROUND(AVG("dewpoint")::numeric,1) AS "avg_dewpoint",
    ROUND(AVG("relative_humidity")::numeric,1) AS "avg_relative_humidity",
    ROUND(SUM("precipitation")::numeric,2) AS "total_precipitation",
    ROUND(AVG("station_pressure")::numeric,2) AS "avg_station_pressure",
    ROUND(AVG("wind_speed")::numeric,1) AS "avg_wind_speed",
    ROUND(AVG("wind_gust")::numeric,1) AS "avg_wind_gust"
FROM "northeast_weather_2024_hourly"
GROUP BY EXTRACT(MONTH FROM "datetime"), "station";